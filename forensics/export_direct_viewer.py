import json
import sqlite3
from pathlib import Path

DB = Path("forensics/swarm_reconstruction_full/swarm_reconstruction.sqlite3")
OUT = Path("forensics/swarm_reconstruction_full/viewer_direct.html")

def load_subset(conn):
    nodes = {"R0000617", "R0000007", "R0000096"}
    for i in range(497, 512):
        nodes.add(str(i) if False else f"R0053{i}")
    for i in range(594, 611):
        nodes.add(f"R0062{i}")
    available = {r[0] for r in conn.execute("SELECT id FROM nodes WHERE id LIKE 'R%'").fetchall()}
    nodes = sorted(n for n in nodes if n in available)
    return nodes

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    nodes = load_subset(conn)
    node_set = set(nodes)
    edges = []
    # exact-edge data source: parent edges and direct edges recorded already.
    for row in conn.execute("SELECT source_node,target_node,edge_type,confidence,proof FROM edges"):
        s, t = row["source_node"], row["target_node"]
        if s in node_set and t in node_set:
            edges.append((s, t, row["edge_type"], float(row["confidence"]), str(row["proof"])))
    # deduplicate
    edges = sorted(set(edges))
    nodes_json = [{"id": n, "label": n, "title": f"Open row {n}; check it in JSONL"} for n in nodes]
    edges_json = [{"from": s, "to": t, "label": et, "title": proof, "value": max(0.3, conf)} for s, t, et, conf, proof in edges]
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Swarm Direct Viewer</title>
<style>
body {{ font-family: system-ui,sans-serif; background:#0f172a; color:#e2e8f0; margin:16px; }}
#mynetwork {{ height:740px; background:#1e2932; border-radius:8px; border:1px solid rgba(148,163,184,.25); }}
#legend {{ margin:10px 0 14px; font-size:13px; color:#94a3b8; }}
code {{ font-family:Consolas,monospace; }}
</style>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
</head>
<body>
<h1>Swarm Direct Viewer</h1>
<p>Direct links only among {len(nodes)} interesting real rows (parents, exact echoes, and shared markers). Atomic/synthetic bridge nodes are removed for readability.</p>
<div id="legend">Legend: see tooltip by hovering. node labels are row identifiers. This page deliberately avoids synthetic nodes so edges can be followed visually.</div>
<div id="mynetwork"></div>
<script>
const nodes = new vis.DataSet({json.dumps(nodes_json)});
const edges = new vis.DataSet({json.dumps(edges_json)});
const container = document.getElementById('mynetwork');
const data = {{ nodes, edges }};
const options = {{
  physics: {{ barnesHut: {{ gravitationalConstant: -20000, centralGravity: 0.15, springLength: 180 }} }},
  interaction: {{ hover: true, tooltipDelay: 120 }},
  edges: {{ smooth: {{ type: "dynamic", roundness: 0.25 }}, width: 2, font: {{ size: 10, background: "#111827" }} }},
  nodes: {{ shape: "dot", size: 12, font: {{ size: 11 }} }}
}};
const network = new vis.Network(container, data, options);
</script>
</body></html>"""
    print("DEBUG", len(nodes_json), len(edges_json))
    OUT.write_text(html, encoding="utf-8")
    print("wrote", OUT, "nodes", len(nodes_json), "edges", len(edges_json))

main()
