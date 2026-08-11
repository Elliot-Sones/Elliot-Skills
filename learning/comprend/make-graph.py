#!/usr/bin/env python3
"""Render ~/.claude/comprend/prereqs.md + knowledge.md as an interactive graph.

Output: ~/.claude/comprend/graph.html (vis-network via CDN).
Node fill = concept area. Border: green = known, amber = learning, dashed orange = shaky.
Validates the map: warns on undefined prerequisite references and cycles.
"""
import json
import re
import sys
from pathlib import Path

DATA = Path.home() / ".claude" / "comprend"
OUT = DATA / "graph.html"

PALETTE = [
    "#e3f2fd", "#e8f5e9", "#fff8e1", "#f3e5f5", "#e0f7fa",
    "#fbe9e7", "#f1f8e9", "#ede7f6", "#fffde7", "#e0f2f1", "#fce4ec",
]

NODE_RE = re.compile(r"^([a-z0-9-]+):\s*(.*)$")
ALIAS_RE = re.compile(r"^([a-z0-9-]+)\s*=\s*([a-z0-9-]+)$")
SECTION_RE = re.compile(r"^##\s+(.*)$")
LEDGER_RE = re.compile(r"^-\s*\[[^\]]+\]\s*([^:(]+):\s*(.*)$")


def parse_prereqs(path):
    nodes, aliases, section = {}, {}, "unsorted"
    sections = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("!"):
            continue
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1).strip()
            if section != "aliases" and section not in sections:
                sections.append(section)
            continue
        m = ALIAS_RE.match(line)
        if m:
            aliases[m.group(1)] = m.group(2)
            continue
        m = NODE_RE.match(line)
        if m:
            name, rest = m.group(1), m.group(2)
            rest = re.sub(r"\(added [^)]*\)", "", rest).strip()
            if rest in ("(none)", ""):
                prereqs = []
            else:
                prereqs = [p.strip() for p in rest.split(",") if p.strip()]
            nodes[name] = {"prereqs": prereqs, "section": section}
    return nodes, aliases, sections


def parse_ledger(path, aliases):
    status = {}
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


def validate(nodes):
    problems = []
    for name, info in nodes.items():
        for p in info["prereqs"]:
            if p not in nodes:
                problems.append(f"undefined prerequisite: {name} -> {p}")
    state = {}

    def visit(n, stack):
        state[n] = "in"
        for p in nodes.get(n, {"prereqs": []})["prereqs"]:
            if state.get(p) == "in":
                problems.append(f"cycle: {' -> '.join(stack + [n, p])}")
            elif state.get(p) is None:
                visit(p, stack + [n])
        state[n] = "done"

    for n in nodes:
        if state.get(n) is None:
            visit(n, [])
    return problems


def main():
    nodes, aliases, sections = parse_prereqs(DATA / "prereqs.md")
    ledger = parse_ledger(DATA / "knowledge.md", aliases)
    problems = validate(nodes)
    for p in problems:
        print(f"WARN: {p}", file=sys.stderr)

    color_of = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sections)}
    vis_nodes, vis_edges = [], []
    for name, info in nodes.items():
        st = ledger.get(name, "unknown")
        border = {"known": "#1a7f37", "learning": "#b58900", "shaky": "#cb4b16"}.get(st, "#9aa0a6")
        width = 1 if st == "unknown" else 3
        title = f"{name} [{info['section']}] status: {st}"
        title += " | needs: " + (", ".join(info["prereqs"]) if info["prereqs"] else "nothing")
        vis_nodes.append({
            "id": name, "label": name, "title": title, "shape": "box",
            "color": {"background": color_of.get(info["section"], "#eee"), "border": border},
            "borderWidth": width,
            "shapeProperties": {"borderDashes": st == "shaky"},
        })
        for p in info["prereqs"]:
            if p in nodes:
                vis_edges.append({"from": p, "to": name})

    counts = {"nodes": len(vis_nodes), "edges": len(vis_edges),
              "known": sum(1 for s in ledger.values() if s == "known"),
              "learning": sum(1 for s in ledger.values() if s == "learning")}

    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Comprend concept map</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body { margin: 0; font-family: -apple-system, sans-serif; }
  #bar { padding: 10px 14px; background: #111; color: #eee; display: flex; gap: 16px; align-items: center; }
  #bar b { font-weight: 600; }
  #search { padding: 5px 9px; border-radius: 6px; border: 1px solid #444; background: #222; color: #eee; width: 220px; }
  .chip { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 12px; }
  #net { height: calc(100vh - 46px); }
</style></head><body>
<div id="bar">
  <b>Comprend concept map</b>
  <span>__COUNTS__</span>
  <input id="search" placeholder="find a concept..." />
  <span class="chip" style="border: 2px solid #1a7f37; color: #eee;">known</span>
  <span class="chip" style="border: 2px solid #b58900; color: #eee;">learning</span>
  <span class="chip" style="border: 2px dashed #cb4b16; color: #eee;">shaky</span>
  <span class="chip" style="border: 1px solid #9aa0a6; color: #eee;">not yet</span>
</div>
<div id="net"></div>
<script>
  const nodes = new vis.DataSet(__NODES__);
  const edges = new vis.DataSet(__EDGES__);
  const net = new vis.Network(document.getElementById("net"), { nodes, edges }, {
    layout: { hierarchical: { enabled: true, direction: "LR", sortMethod: "directed",
      levelSeparation: 230, nodeSpacing: 34, treeSpacing: 40 } },
    physics: false,
    edges: { arrows: "to", color: { color: "#c5c9cf", highlight: "#111" },
      smooth: { type: "cubicBezier", forceDirection: "horizontal", roundness: 0.4 } },
    nodes: { font: { size: 15 } },
    interaction: { hover: true, navigationButtons: true, keyboard: true },
  });
  document.getElementById("search").addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const q = e.target.value.trim().toLowerCase().replaceAll(" ", "-");
    const hit = nodes.get().find(n => n.id.includes(q));
    if (hit) { net.focus(hit.id, { scale: 1.3, animation: true }); net.selectNodes([hit.id]); }
  });
</script></body></html>"""
    html = html.replace("__NODES__", json.dumps(vis_nodes))
    html = html.replace("__EDGES__", json.dumps(vis_edges))
    html = html.replace("__COUNTS__",
                        f"{counts['nodes']} concepts, {counts['edges']} edges, "
                        f"{counts['known']} known, {counts['learning']} learning")
    OUT.write_text(html)
    print(f"wrote {OUT} ({counts['nodes']} nodes, {counts['edges']} edges, "
          f"{len(problems)} warnings)")


if __name__ == "__main__":
    main()
