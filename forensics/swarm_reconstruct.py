#!/usr/bin/env python3
"""Swarm Traces reconstruction tool.

Reads a JSONL trace file and builds:
  - nodes.ndjson
  - edges.ndjson
  - components.json
  - swarm_reconstruction.sqlite3
  - observer_report.md
  - viewer.html (first 1000 local nodes, visual subset)
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import sqlite3
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

TOKEN_RE = re.compile(r"\[[A-Z][A-Z0-9 _:-]*?\]|zz[A-Za-z0-9_]{4,}")

def read_rows(path, limit=None):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            if limit is not None and len(rows) >= limit:
                break
            rows.append(json.loads(line))
    return rows

def marker_inventory(text):
    return sorted(set(TOKEN_RE.findall(text or "")))

def normalize_token(token):
    s = token.lower().replace(" ", "_")
    s = re.sub(r"\d+", "N", s)
    return s


SHORT_PLACEHOLDER_EXACT = {
    "[ENCODED BLOB]", "[REDACTED BINARY]", "[ENCODED ARCHIVE]"
}

def meaningful_echo_text(text):
    t = (text or "").strip()
    if len(t) < 20:
        return False
    if t in SHORT_PLACEHOLDER_EXACT:
        return False
    if len(t) < 80 and t.startswith("[") and t.endswith("]"):
        return False
    return True

def sqlite_create(conn):
    conn.executescript("""
    CREATE TABLE nodes (
      id TEXT PRIMARY KEY,
      kind TEXT,
      text_len INTEGER,
      sha256 TEXT,
      markers TEXT,
      repr TEXT
    );
    CREATE TABLE edges (
      edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
      source_node TEXT,
      target_node TEXT,
      edge_type TEXT,
      confidence REAL,
      proof TEXT,
      FOREIGN KEY(source_node) REFERENCES nodes(id),
      FOREIGN KEY(target_node) REFERENCES nodes(id)
    );
    CREATE TABLE graph_meta (k TEXT PRIMARY KEY, v TEXT NOT NULL);
    CREATE INDEX idx_edges_source ON edges(source_node, edge_type, confidence);
    CREATE INDEX idx_edges_target ON edges(target_node, edge_type, confidence);
    CREATE INDEX idx_edges_type ON edges(edge_type);
    CREATE INDEX idx_nodes_kind ON nodes(kind);
    CREATE INDEX idx_nodes_sha ON nodes(sha256);
    """)

def add_node(conn, nf, node):
    nf.write(json.dumps(node, ensure_ascii=False) + "\n")
    conn.execute("INSERT OR REPLACE INTO nodes(id,kind,text_len,sha256,markers,repr) VALUES(?,?,?,?,?,?)",
                 (node["id"], node["kind"], node["text_len"], node.get("sha256"),
                  json.dumps(node["markers"]), node.get("label", "")[:240]))

def add_edge(conn, ef, e, min_conf):
    if e["confidence"] < min_conf:
        return False
    ef.write(json.dumps(e, ensure_ascii=False) + "\n")
    conn.execute("INSERT INTO edges(source_node,target_node,edge_type,confidence,proof) VALUES(?,?,?,?,?)",
                 (e["source"], e["target"], e["edge_type"], e["confidence"], e["proof"]))
    return True

def build_dataset(inp, out, limit=None, max_marker_freq=25, min_confidence=0.5, verbose=True):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = read_rows(inp, limit)
    hashes = Counter(hashlib.sha256(r.get("text", "").encode()).hexdigest() for r in rows)
    marker_sets = defaultdict(set)
    for r in rows:
        for token in marker_inventory(r.get("text", "")):
            marker_sets[token].add(r["id"])
    rare = {t: ids for t, ids in marker_sets.items() if 2 <= len(ids) <= max_marker_freq}
    if verbose:
        print("rows={0} exact_groups={1} rare_markers={2}".format(
            len(rows),
            sum(1 for c in hashes.values() if c > 1),
            len(rare),
        ))

    conn_path = out / "swarm_reconstruction.sqlite3"
    conn_path.unlink(missing_ok=True)
    conn = sqlite3.connect(conn_path)
    sqlite_create(conn)
    arr_nodes = []
    arr_edges = []
    edges_kept = []
    with open(out / "nodes.ndjson", "w", encoding="utf-8") as nf, open(out / "edges.ndjson", "w", encoding="utf-8") as ef:
        # Row nodes
        for r in rows:
            sha = hashlib.sha256(r.get("text", "").encode()).hexdigest()
            markers = marker_inventory(r.get("text", ""))
            rare_for_row = sorted(m for m in markers if m in rare)
            node = {
                "id": r["id"],
                "kind": r.get("kind", "payload"),
                "text_len": len(r.get("text", "") or ""),
                "sha256": sha,
                "markers": rare_for_row,
                "label": (r.get("text", "") or "")[:180],
                "parent_id": r.get("parent_id"),
                "cite": r.get("cite"),
            }
            arr_nodes.append(node)
            add_node(conn, nf, node)

        # Exact hash atoms + edges
        hash_atom = {}
        for r in rows:
            text = r.get("text", "") or ""
            if not meaningful_echo_text(text):
                continue
            h = hashlib.sha256(text.encode()).hexdigest()
            if hashes[h] <= 1:
                continue
            if h not in hash_atom:
                atom_id = "ATOMIC:sha:" + h
                hash_atom[h] = atom_id
                atom_node = {"id": atom_id, "kind": "exact_bucket", "text_len": 0, "sha256": h, "markers": ["exact_hash_bucket"], "label": "exact text hash " + h[:16]}
                arr_nodes.append(atom_node)
                add_node(conn, nf, atom_node)
            e = {"source": r["id"], "target": hash_atom[h], "edge_type": "echo_of_exact", "confidence": 1.0, "proof": "text_sha256:" + h}
            if add_edge(conn, ef, e, min_confidence):
                arr_edges.append(e)

        # Rare marker atoms + edges
        for token in rare:
            atom_id = "ATOMIC:marker:" + normalize_token(token)
            atom_node = {"id": atom_id, "kind": "marker_bucket", "text_len": 0, "sha256": normalize_token(token), "markers": [token], "label": "reused marker " + token}
            arr_nodes.append(atom_node)
            add_node(conn, nf, atom_node)
            for rid in sorted(rare[token]):
                e = {"source": rid, "target": atom_id, "edge_type": "references_marker", "confidence": 0.7, "proof": "rare pivot=" + token + " rows=" + str(len(marker_sets[token]))}
                if add_edge(conn, ef, e, min_confidence):
                    arr_edges.append(e)

        # Parent edges (ghost parent nodes if unavailable)
        parent_ids = set(r.get("parent_id") for r in rows if r.get("parent_id") is not None)
        for pid in parent_ids:
            stmt = conn.execute("SELECT 1 FROM nodes WHERE id=? LIMIT 1", (pid,)).fetchone()
            if not stmt:
                ghost = {"id": pid, "kind": "ghost_parent_reference", "text_len": 0, "sha256": "unknown", "markers": [], "label": "parent reference not in current source scope"}
                arr_nodes.append(ghost)
                add_node(conn, nf, ghost)
        for r in rows:
            pid = r.get("parent_id")
            if pid is not None:
                e = {"source": pid, "target": r["id"], "edge_type": "parent_of", "confidence": 1.0, "proof": "direct parent_id"}
                if add_edge(conn, ef, e, min_confidence):
                    arr_edges.append(e)

        # Meta
        conn.executemany("INSERT OR REPLACE INTO graph_meta(k,v) VALUES(?,?)", [
            ("built_utc", datetime.now(timezone.utc).isoformat()),
            ("source_rows", json.dumps(len(rows))),
            ("exact_hash_groups", json.dumps(sum(1 for c in hashes.values() if c > 1))),
            ("exact_hash_rows", json.dumps(sum(c for c in hashes.values() if c > 1))),
            ("rare_marker_buckets", json.dumps(len(rare))),
            ("title", json.dumps("Swarm Reconstruction Graph")),
        ])
        conn.commit()

        # Top components
        uf = {n["id"]: n["id"] for n in arr_nodes}
        def find(x):
            uf.setdefault(x, x)
            while uf[x] != x:
                uf[x] = uf[uf[x]]
                x = uf[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                uf[ra] = rb
        for e in arr_edges:
            union(e["source"], e["target"])
        comp_sizes = Counter()
        for n in arr_nodes:
            comp_sizes[find(n["id"])] += 1
        top_components_list = []
        for comp, size in sorted(comp_sizes.items(), key=lambda x: -x[1])[:20]:
            subset = [n["id"] for n in arr_nodes if find(n["id"]) == comp][:12]
            top_components_list.append({"component_id": comp, "size": size, "representative_nodes": subset})
        with open(out / "components.json", "w", encoding="utf-8") as fp:
            json.dump({"top_components": top_components_list}, fp, indent=2)

        export_viewer(out, arr_nodes, arr_edges)
        conn.close()
        # idempotent convenience report (full stats in observer_report.py later)
        return {"rows": rows, "nodes": arr_nodes, "edges": arr_edges, "conn_path": conn_path}

def export_viewer(out, nodes, edges):
    preview_nodes = [n["id"] for n in nodes if str(n["id"]).startswith("R")][:1000]
    preview_set = set(preview_nodes)
    preview_edges = [e for e in edges if e["source"] in preview_set or e["target"] in preview_set]
    vis_nodes = [{"id": n, "label": n} for n in preview_nodes]
    vis_edges = [{"from": e["source"], "to": e["target"], "title": e["edge_type"]} for e in preview_edges]
    html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Swarm Reconstruction Viewer</title>
<style>body{font-family:system-ui;background:#0f172a;color:#e2e8f0;margin:16px}#mynetwork{height:700px;background:#1e2932;border-radius:8px}</style>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
</head><body>
<h1>Swarm Reconstruction (preview of """ + str(len(preview_nodes)) + """ rows)</h1>
<div id="mynetwork"></div>
<script>
const nodes=new vis.DataSet(""" + json.dumps(vis_nodes) + """);
const edges=new vis.DataSet(""" + json.dumps(vis_edges) + """);
const network=new vis.Network(document.getElementById("mynetwork"),{nodes,edges},{physics:{enabled:true}});
</script></body></html>"""
    pathlib.Path(out, "viewer.html").write_text(html, encoding="utf-8")

def query_blast(db_path, start, edge_types, min_conf, depth=2, limit=1000):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    types = ",".join("?" for _ in edge_types)
    results = []
    seen = {start: 0}
    queue = deque([(start, 0)])
    while queue:
        node, d = queue.popleft()
        if d >= depth:
            continue
        a = conn.execute(
            "SELECT target_node AS other,edge_type,confidence FROM edges WHERE source_node=? AND edge_type IN (" + types + ") AND confidence>=?",
            (node, *edge_types, min_conf),
        ).fetchall()
        b = conn.execute(
            "SELECT source_node AS other,edge_type,confidence FROM edges WHERE target_node=? AND edge_type IN (" + types + ") AND confidence>=?",
            (node, *edge_types, min_conf),
        ).fetchall()
        for row in a + b:
            nxt = row["other"]
            if nxt in seen:
                continue
            seen[nxt] = d + 1
            results.append({"id": nxt, "depth": d + 1, "via": row["edge_type"], "confidence": row["confidence"]})
            if len(results) >= limit:
                return results
            queue.append((nxt, d + 1))
    return results

def write_observer_report(out, data):
    conn = sqlite3.connect(str(out / "swarm_reconstruction.sqlite3"))
    node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    ec = conn.execute("SELECT edge_type,COUNT(*) FROM edges GROUP BY edge_type ORDER BY COUNT(*) DESC").fetchall()
    conn.close()
    lines = []
    lines.append("# Swarm Reconstruction Observer Report")
    lines.append("")
    lines.append("- source rows: {0}".format(len(data["rows"])))
    lines.append("- graph nodes (including synthetic atoms): {0}".format(node_count))
    lines.append("- graph edges: {0}".format(edge_count))
    for k, v in ec:
        lines.append("- {0}: {1}".format(k, v))
    lines.append("")
    lines.append("## What was reconstructed")
    lines.append("- Parent relationships: exact data lineage only.")
    lines.append("- Exact-hash matches: strong propagation/echo links among duplicated content.")
    lines.append("- Rare-marker edges: coupling signals, not guaranteed source-target conversations.")
    lines.append("")
    lines.append("## What an investigator still cannot prove with this dataset")
    lines.append("1. The precise chronological order of conversation events (all `time_utc` are null).")
    lines.append("2. The true human or agent identity behind a redaction handle.")
    lines.append("3. Whether a parent-child pair reflects execution rather than storage/recovery.")
    lines.append("4. Out-of-band channel content (proxy image beaconing, browser console output, server-side state).")
    lines.append("5. Effects of arbitrary content injected into a command environment.")
    lines.append("6. Causal intent for repeated stager pieces; classification cannot prove collusion.")
    (out / "observer_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Swarm Reconstruction Tool")
    sub = ap.add_subparsers(dest="command", required=True)
    cb = sub.add_parser("build")
    cb.add_argument("--input", required=True)
    cb.add_argument("--out-dir", required=True)
    cb.add_argument("--limit", type=int, default=None)
    cb.add_argument("--max-marker-freq", type=int, default=25)
    cb.add_argument("--min-confidence", type=float, default=0.5)
    cb.add_argument("--verbose", action="store_true")
    cr = sub.add_parser("blast")
    cr.add_argument("--db", required=True)
    cr.add_argument("--from", dest="start", required=True)
    cr.add_argument("--edge", nargs="+", default=["parent_of", "echo_of_exact", "references_marker"])
    cr.add_argument("--min-confidence", type=float, default=0.5)
    cr.add_argument("--depth", type=int, default=2)
    cr.add_argument("--limit", type=int, default=1000)
    args = ap.parse_args()
    if args.command == "build":
        rows = read_rows(args.input, args.limit)
        out = pathlib.Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        built = build_dataset(args.input, out, args.limit, args.max_marker_freq, args.min_confidence, True)
        write_observer_report(out, built)
        conn = sqlite3.connect(str(out / "swarm_reconstruction.sqlite3"))
        print("nodes={0} edges={1}".format(conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0],
                                           conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]))
        conn.close()
    elif args.command == "blast":
        ret = query_blast(args.db, args.start, tuple(args.edge), args.min_confidence, args.depth, args.limit)
        print(json.dumps(ret, indent=2))

if __name__ == "__main__":
    main()
