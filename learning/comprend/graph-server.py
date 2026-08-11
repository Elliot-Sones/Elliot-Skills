#!/usr/bin/env python3
"""Serve the comprend concept map as a live local app.

http://127.0.0.1:8377  (localhost only)
  /      -> graph-app.html (Obsidian-style force graph)
  /data  -> fresh JSON parsed from prereqs.md + knowledge.md on every request,
            so ledger changes show up live (the page polls every 5s).
"""
import errno
import json
import re
import socketserver
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

DATA = Path.home() / ".claude" / "comprend"
APP = Path(__file__).parent / "graph-app.html"
PORT = 8377

NODE_RE = re.compile(r"^([a-z0-9-]+):\s*(.*)$")
ALIAS_RE = re.compile(r"^([a-z0-9-]+)\s*=\s*([a-z0-9-]+)$")
SECTION_RE = re.compile(r"^##\s+(.*)$")
LEDGER_RE = re.compile(r"^-\s*\[[^\]]+\]\s*([^:(]+):\s*(.*)$")


def parse_prereqs():
    nodes, aliases, section, areas = {}, {}, "unsorted", []
    for raw in (DATA / "prereqs.md").read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("!"):
            continue
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1).strip()
            if section != "aliases" and section not in areas:
                areas.append(section)
            continue
        m = ALIAS_RE.match(line)
        if m:
            aliases[m.group(1)] = m.group(2)
            continue
        m = NODE_RE.match(line)
        if m:
            name, rest = m.group(1), m.group(2)
            rest = re.sub(r"\(added [^)]*\)", "", rest).strip()
            prereqs = [] if rest in ("(none)", "") else [p.strip() for p in rest.split(",") if p.strip()]
            nodes[name] = {"prereqs": prereqs, "area": section}
    return nodes, aliases, areas


def parse_ledger(aliases):
    status = {}
    path = DATA / "knowledge.md"
    if not path.exists():
        return status
    for raw in path.read_text().splitlines():
        m = LEDGER_RE.match(raw.strip())
        if not m:
            continue
        name = m.group(1).strip().lower().replace(" ", "-")
        name = aliases.get(name, name)
        rest = m.group(2)
        if "shaky" in rest:
            status[name] = "shaky"
        elif "(learning" in rest:
            status[name] = "learning"
        elif "known" in rest:
            status[name] = "known"
    return status


def build_data():
    nodes, aliases, areas = parse_prereqs()
    ledger = parse_ledger(aliases)
    degree = {n: 0 for n in nodes}
    edges = []
    for name, info in nodes.items():
        for i, p in enumerate(info["prereqs"]):
            if p in nodes:
                edges.append({"id": f"{p}->{name}", "from": p, "to": name})
                degree[name] += 1
                degree[p] += 1
    out_nodes = [{
        "id": n, "area": info["area"], "status": ledger.get(n, "unknown"),
        "degree": degree[n], "needs": ", ".join(info["prereqs"]),
        "ready": ledger.get(n) is None and all(ledger.get(p) == "known" for p in info["prereqs"]),
    } for n, info in nodes.items()]
    counts = {
        "nodes": len(out_nodes), "edges": len(edges),
        "known": sum(1 for n in out_nodes if n["status"] == "known"),
        "learning": sum(1 for n in out_nodes if n["status"] == "learning"),
        "shaky": sum(1 for n in out_nodes if n["status"] == "shaky"),
        "ready": sum(1 for n in out_nodes if n["ready"]),
    }
    return {"nodes": out_nodes, "edges": edges, "areas": areas, "aliases": aliases, "counts": counts}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/data":
            body = json.dumps(build_data()).encode()
            ctype = "application/json"
        else:
            # Everything else serves the app; query strings (/?path=...) and
            # stray paths must never 404 a live map.
            body = APP.read_bytes()
            ctype = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    try:
        server = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(f"already running at http://127.0.0.1:{PORT}")
            return
        raise
    print(f"comprend graph at http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
