#!/usr/bin/env python3
"""Precompute the comprend edge space -> ~/.claude/comprend/space.json

Run once, and again whenever prereqs.md grows. It is the ONLY moving part behind
the six edge-space features; everything downstream is a lookup in the resulting
JSON. If ollama is down, it exits non-zero and the skill degrades to plain
comprend (no analogies, no confusable/false-friend warnings).

Outputs (all derived, all rebuildable, never part of the benchmark ruler):
  edges          : every prereq edge with its top parallel edges (analogy anchors + quiz)
  confusables    : per-node name-twins, cosine >= CONFUSE_MIN  (contrast-first + repair)
  false_friends  : per-node high-similarity but graph-far pairs (name-collision warnings)

Thresholds are tunable; picked from the 2026-08 experiments on the v2 map.
"""
import json
import re
import sys
import urllib.request
from collections import deque
from pathlib import Path

DATA = Path.home() / ".claude" / "comprend"
PREREQS = DATA / "prereqs.md"
OUT = DATA / "space.json"
MODEL = "nomic-embed-text"

CONFUSE_MIN = 0.80      # name-twin cosine floor -> contrast before teaching
FF_SIM_MIN = 0.66       # false-friend: this similar in name-space...
FF_DIST_MIN = 5         # ...yet this far apart on the map -> likely a name collision
PARALLELS_PER_EDGE = 6  # analogy candidates stored per edge (runtime filters to known)

NODE_RE = re.compile(r"^([a-z0-9-]+):\s*(.*)$")
ALIAS_RE = re.compile(r"^([a-z0-9-]+)\s*=\s*([a-z0-9-]+)$")
SECTION_RE = re.compile(r"^##\s+(.*)$")


def parse_map():
    nodes, edges, aliases, section = [], [], {}, "unsorted"
    seen = set()
    for raw in PREREQS.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("!"):
            continue
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1).strip()
            continue
        if section == "aliases":
            am = ALIAS_RE.match(line)
            if am:
                aliases[am.group(1)] = am.group(2)
            continue
        m = NODE_RE.match(line)
        if m:
            name = m.group(1)
            rest = re.sub(r"\(added [^)]*\)", "", m.group(2)).strip()
            if name not in seen:
                seen.add(name)
                nodes.append(name)
            if rest not in ("(none)", ""):
                for p in [x.strip() for x in rest.split(",") if x.strip()]:
                    edges.append((p, name))
    edges = [(p, c) for p, c in edges if p in seen and c in seen]
    return nodes, edges, aliases


def embed(texts):
    req = urllib.request.Request(
        "http://localhost:11434/api/embed",
        data=json.dumps({"model": MODEL, "input": texts}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["embeddings"]


def main():
    try:
        import numpy as np
    except ImportError:
        sys.exit("build-space: numpy required (pip install numpy)")

    nodes, edges, aliases = parse_map()

    vecs = []
    try:
        for i in range(0, len(nodes), 64):
            vecs.extend(embed([n.replace("-", " ") for n in nodes[i:i + 64]]))
    except Exception as e:
        sys.exit(f"build-space: ollama unreachable ({e}). Start it: `ollama serve`. "
                 f"Skill degrades to plain comprend until then.")

    M = np.array(vecs, dtype=float)
    M /= np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-9)
    ni = {n: i for i, n in enumerate(nodes)}

    # edge difference vectors (child - parent), normalized
    ev, ekeys = [], []
    for p, c in edges:
        d = M[ni[c]] - M[ni[p]]
        n = np.linalg.norm(d)
        if n > 1e-9:
            ev.append(d / n)
            ekeys.append((p, c))
    EV = np.array(ev)
    ES = EV @ EV.T  # edge-edge cosine

    edges_out = []
    for i, (p, c) in enumerate(ekeys):
        order = np.argsort(-ES[i])
        parallels = []
        for j in order:
            if j == i:
                continue
            pp, cc = ekeys[j]
            # a genuine analogy shares no endpoint with the query edge
            if pp in (p, c) or cc in (p, c):
                continue
            parallels.append({"from": pp, "to": cc, "sim": round(float(ES[i, j]), 3)})
            if len(parallels) >= PARALLELS_PER_EDGE:
                break
        edges_out.append({"from": p, "to": c, "parallels": parallels})

    # node-node cosine for confusables + false friends
    NS = M @ M.T
    adj = {n: set() for n in nodes}
    for p, c in edges:
        adj[p].add(c)
        adj[c].add(p)

    def graph_dist(a, b):
        if a == b:
            return 0
        seen = {a}
        dq = deque([(a, 0)])
        while dq:
            u, d = dq.popleft()
            for v in adj[u]:
                if v == b:
                    return d + 1
                if v not in seen:
                    seen.add(v)
                    dq.append((v, d + 1))
        return 99

    confusables, false_friends = {}, {}
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            s = float(NS[i, j])
            a, b = nodes[i], nodes[j]
            if s >= CONFUSE_MIN:
                confusables.setdefault(a, []).append({"pair": b, "sim": round(s, 3)})
                confusables.setdefault(b, []).append({"pair": a, "sim": round(s, 3)})
            elif s >= FF_SIM_MIN:
                gd = graph_dist(a, b)
                if gd >= FF_DIST_MIN:
                    false_friends.setdefault(a, []).append({"pair": b, "sim": round(s, 3), "graph_dist": gd})
                    false_friends.setdefault(b, []).append({"pair": a, "sim": round(s, 3), "graph_dist": gd})

    for d in (confusables, false_friends):
        for k in d:
            d[k].sort(key=lambda x: -x["sim"])

    out = {
        "built": None,  # stamp after the run; Date() is unavailable inside the script
        "model": MODEL,
        "thresholds": {"confuse_min": CONFUSE_MIN, "ff_sim_min": FF_SIM_MIN, "ff_dist_min": FF_DIST_MIN},
        "counts": {"nodes": len(nodes), "edges": len(ekeys),
                   "confusable_nodes": len(confusables), "false_friend_nodes": len(false_friends)},
        "edges": edges_out,
        "confusables": confusables,
        "false_friends": false_friends,
    }
    OUT.write_text(json.dumps(out, indent=0))
    c = out["counts"]
    print(f"wrote {OUT}")
    print(f"  {c['nodes']} nodes, {c['edges']} edges")
    print(f"  {c['confusable_nodes']} nodes have a name-twin (>= {CONFUSE_MIN})")
    print(f"  {c['false_friend_nodes']} nodes have a false-friend warning")


if __name__ == "__main__":
    main()
