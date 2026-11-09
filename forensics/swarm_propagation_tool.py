#!/usr/bin/env python3
"""Swarm Traces information-propagation reconstruction tool."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import pathlib
import re
import sqlite3
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"\[[A-Z][A-Z0-9 _:-]*?\]|zz[A-Za-z0-9_]{4,}")
SHORT_PLACEHOLDER_EXACT = {"[ENCODED BLOB]", "[REDACTED BINARY]", "[ENCODED ARCHIVE]"}


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


def meaningful_echo_text(text):
    t = (text or "").strip()
    if len(t) < 20:
        return False
    if t in SHORT_PLACEHOLDER_EXACT:
        return False
    if len(t) < 80 and t.startswith("[") and t.endswith("]"):
        return False
    return True


def normalize_text(text):
    substitutions = [
        (r"\[REDACTED:source_identifier:[^\]]*\]", "[source]"),
        (r"\[REDACTED:runtime_identifier(?::[^\]]*)?\]", "[runtime]"),
        (r"\[REDACTED:destination:[^\]]*\]", "[destination]"),
        (r"\[REDACTED:[^\]]*\]", "[redacted]"),
        (r"\[SERVICE \d+ URL \d+\]", "[service]"),
        (r"\[SHORTENER [^\]]*\]", "[shortener]"),
        (r"\[PROXY \d+ URL \d+\]", "[proxy]"),
        (r"\[ENCODED BLOB(?: \d+)?\]", "[blob]"),
        (r"\[CREDENTIAL \d+\]", "[credential]"),
        (r"\[HF REPO \d+\]", "[hf-repo]"),
    ]
    out = text or ""
    for rx, rep in substitutions:
        out = re.sub(rx, rep, out, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", out).strip()


def payload_template(text):
    return hashlib.sha256(normalize_text(text).encode()).hexdigest()


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
      proof TEXT
    );
    CREATE TABLE graph_meta (k TEXT PRIMARY KEY, v TEXT NOT NULL);
    CREATE INDEX idx_edges_source ON edges(source_node, edge_type, confidence);
    CREATE INDEX idx_edges_target ON edges(target_node, edge_type, confidence);
    CREATE INDEX idx_edges_type ON edges(edge_type);
    CREATE INDEX idx_nodes_kind ON nodes(kind);
    CREATE INDEX idx_nodes_sha ON nodes(sha256);
    CREATE TABLE info_pieces (
      piece_id TEXT PRIMARY KEY,
      piece_kind TEXT,
      occurrence_count INTEGER,
      first_id TEXT,
      last_id TEXT
    );
    """)


def add_node(conn, nf, node):
    nf.write(json.dumps(node, ensure_ascii=False) + "\n")
    conn.execute(
        "INSERT OR REPLACE INTO nodes(id,kind,text_len,sha256,markers,repr) VALUES(?,?,?,?,?,?)",
        (node["id"], node["kind"], node["text_len"], node.get("sha256"),
         json.dumps(node["markers"]), node.get("label", "")[:240]),
    )


def add_edge(conn, ef, e, min_conf):
    if e["confidence"] < min_conf:
        return False
    ef.write(json.dumps(e, ensure_ascii=False) + "\n")
    conn.execute(
        "INSERT INTO edges(source_node,target_node,edge_type,confidence,proof) VALUES(?,?,?,?,?)",
        (e["source"], e["target"], e["edge_type"], e["confidence"], e["proof"]),
    )
    return True


def build_dataset(inp, out, limit=None, max_marker_freq=25, min_confidence=0.5, verbose=True):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = read_rows(inp, limit)
    byid = {r["id"]: r for r in rows}
    rows_sorted = sorted(rows, key=lambda r: r["id"])

    hashes = Counter(hashlib.sha256((r.get("text") or "").encode()).hexdigest() for r in rows)
    marker_sets = defaultdict(set)
    for r in rows:
        for token in marker_inventory(r.get("text", "")):
            marker_sets[token].add(r["id"])
    rare = {t: ids for t, ids in marker_sets.items() if 2 <= len(ids) <= max_marker_freq}

    template_sets = defaultdict(set)
    for r in rows:
        if r.get("kind") == "payload" and meaningful_echo_text(r.get("text", "")):
            template_sets[payload_template(r.get("text", ""))].add(r["id"])
    template_groups = {t: ids for t, ids in template_sets.items() if len(ids) >= 2}

    if verbose:
        print("rows={0} exact_groups={1} rare_markers={2} template_groups={3}".format(
            len(rows),
            sum(1 for c in hashes.values() if c > 1),
            len(rare),
            len(template_groups),
        ))

    conn_path = out / "swarm_reconstruction.sqlite3"
    conn_path.unlink(missing_ok=True)
    conn = sqlite3.connect(conn_path)
    sqlite_create(conn)
    arr_nodes = []
    arr_edges = []
    with open(out / "nodes.ndjson", "w", encoding="utf-8") as nf, open(out / "edges.ndjson", "w", encoding="utf-8") as ef:
        for r in rows_sorted:
            sha = hashlib.sha256((r.get("text") or "").encode()).hexdigest()
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

        parent_ids = set(r.get("parent_id") for r in rows if r.get("parent_id") is not None)
        for pid in parent_ids:
            if conn.execute("SELECT 1 FROM nodes WHERE id=? LIMIT 1", (pid,)).fetchone():
                continue
            ghost = {"id": pid, "kind": "ghost_parent_reference", "text_len": 0, "sha256": "unknown", "markers": [], "label": "parent reference not in current source scope"}
            arr_nodes.append(ghost)
            add_node(conn, nf, ghost)

        hash_atom = {}
        exact_ids_by_hash = defaultdict(list)
        for r in rows_sorted:
            exact_ids_by_hash[hashlib.sha256((r.get("text") or "").encode()).hexdigest()].append(r["id"])

        for r in rows_sorted:
            text = r.get("text", "") or ""
            if not meaningful_echo_text(text):
                continue
            h = hashlib.sha256(text.encode()).hexdigest()
            if hashes[h] <= 1:
                continue
            if h not in hash_atom:
                hash_atom[h] = "INFO:sha:" + h
                atom_node = {"id": hash_atom[h], "kind": "information_piece", "text_len": 0, "sha256": h,
                             "markers": ["exact_text_piece"], "label": "identical text piece " + h[:16]}
                arr_nodes.append(atom_node)
                add_node(conn, nf, atom_node)
            e = {"source": r["id"], "target": hash_atom[h], "edge_type": "references_information_piece",
                 "confidence": 0.9, "proof": "text_sha256:" + h}
            if add_edge(conn, ef, e, min_confidence):
                arr_edges.append(e)

        # passed identical content
        for r in rows_sorted:
            pid = r.get("parent_id")
            if pid is None or pid not in byid:
                continue
            if not meaningful_echo_text(r.get("text", "")):
                continue
            if hashlib.sha256((r.get("text") or "").encode()).hexdigest() != hashlib.sha256((byid[pid].get("text") or "").encode()).hexdigest():
                continue
            e = {"source": pid, "target": r["id"], "edge_type": "passed_identical_content",
                 "confidence": 1.0, "proof": "parent_id + identical_sha256"}
            if add_edge(conn, ef, e, min_confidence):
                arr_edges.append(e)

        # parent lineage
        for r in rows_sorted:
            pid = r.get("parent_id")
            if pid is None:
                continue
            e = {"source": pid, "target": r["id"], "edge_type": "parent_of", "confidence": 1.0, "proof": "direct parent_id"}
            if add_edge(conn, ef, e, min_confidence):
                arr_edges.append(e)

        # exact echo star edges
        for h, ids in exact_ids_by_hash.items():
            if len(ids) <= 1:
                continue
            text = byid[ids[0]].get("text", "") if ids[0] in byid else ""
            if not meaningful_echo_text(text):
                continue
            for dst in ids[1:]:
                e = {"source": ids[0], "target": dst, "edge_type": "exact_echo", "confidence": 0.95,
                     "proof": "first_occurrence->later sha256:" + h}
                if add_edge(conn, ef, e, min_confidence):
                    arr_edges.append(e)

        # rare markers
        for token in rare:
            atom_id = "MARKER:" + re.sub(r"\d+", "N", token.lower().replace(" ", "_"))
            atom_node = {"id": atom_id, "kind": "marker_bucket", "text_len": 0, "sha256": token, "markers": [token],
                         "label": "reused marker " + token}
            arr_nodes.append(atom_node)
            add_node(conn, nf, atom_node)
        for token in rare:
            atom_id = "MARKER:" + re.sub(r"\d+", "N", token.lower().replace(" ", "_"))
            for rid in sorted(rare[token]):
                e = {"source": rid, "target": atom_id, "edge_type": "references_marker", "confidence": 0.7,
                     "proof": "rare pivot=" + token + " rows=" + str(len(marker_sets[token]))}
                if add_edge(conn, ef, e, min_confidence):
                    arr_edges.append(e)

        # template echo
        for tmpl, ids in template_groups.items():
            ids = sorted(ids)
            if len(ids) < 2:
                continue
            for dst in ids[1:]:
                e = {"source": ids[0], "target": dst, "edge_type": "template_echo", "confidence": 0.8,
                     "proof": "normalized payload template first->later"}
                if add_edge(conn, ef, e, min_confidence):
                    arr_edges.append(e)

        # components
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
        for comp, size in sorted(comp_sizes.items(), key=lambda x: -x[1])[:30]:
            subset = [n["id"] for n in arr_nodes if find(n["id"]) == comp][:12]
            top_components_list.append({"component_id": comp, "size": size, "representative_nodes": subset})
        with open(out / "components.json", "w", encoding="utf-8") as fp:
            json.dump({"top_components": top_components_list}, fp, indent=2)

        # info pieces
        for h, ids in exact_ids_by_hash.items():
            if len(ids) < 2 or not meaningful_echo_text(byid[ids[0]].get("text", "") or ""):
                continue
            conn.execute("INSERT OR REPLACE INTO info_pieces(piece_id,piece_kind,occurrence_count,first_id,last_id) VALUES(?,?,?,?,?)",
                         ("exact_text:" + h, "exact_text", len(ids), ids[0], ids[-1]))
        for t, ids in rare.items():
            sids = sorted(ids)
            conn.execute("INSERT OR REPLACE INTO info_pieces(piece_id,piece_kind,occurrence_count,first_id,last_id) VALUES(?,?,?,?,?)",
                         ("marker:" + t, "rare_marker", len(ids), sids[0], sids[-1]))
        for tmpl, ids in template_groups.items():
            sids = sorted(ids)
            conn.execute("INSERT OR REPLACE INTO info_pieces(piece_id,piece_kind,occurrence_count,first_id,last_id) VALUES(?,?,?,?,?)",
                         ("template:" + tmpl, "payload_template", len(ids), sids[0], sids[-1]))

        conn.commit()
        write_early_flags(out, rows, rare, hashes, template_groups, byid)
        export_viewer(out, arr_nodes, arr_edges)
        conn.close()
        write_observer_report(out, len(rows))

    return {"rows": rows}


def write_early_flags(out, rows, rare, hashes, template_groups, byid):
    exact_seen = set()
    template_seen = set()
    marker_seen = set()
    alerts = []
    def alert(name, rid, idx, extra=None):
        if any(a["name"] == name for a in alerts):
            return
        rec = {"name": name, "row_id": rid, "row_index": idx}
        if extra:
            rec.update(extra)
        alerts.append(rec)

    family_cum = {f: 0 for f in ("link", "api", "img", "eval", "cmd", "canvas")}
    def family(text):
        tl = (text or "").lower()
        out = []
        if "shortener" in tl or "document.write" in tl or "script src=" in tl or "location.hash" in tl: out.append("link")
        if "fetch(" in tl or "xmlhttprequest" in tl: out.append("api")
        if "new image" in tl or "i.src=" in tl: out.append("img")
        if "eval(" in tl or "atob(" in tl or "fromcharcode" in tl: out.append("eval")
        if "src/main.c" in tl or "uname -a" in tl or "/proc/1/status" in tl or ";id;" in tl: out.append("cmd")
        if "canvas" in tl: out.append("canvas")
        return out

    pass_first = None
    for i, r in enumerate(rows, 1):
        text = r.get("text", "") or ""
        for fam_ in family(text):
            family_cum[fam_] += 1

        h = hashlib.sha256(text.encode()).hexdigest()
        if meaningful_echo_text(text) and h in exact_seen:
            alert("first_exact_duplicate_content", r["id"], i, {"sha256": h})
        exact_seen.add(h)

        if r.get("kind") == "payload" and meaningful_echo_text(text):
            t = payload_template(text)
            if t in template_seen:
                alert("first_repeated_payload_template", r["id"], i, {"template": t})
            template_seen.add(t)

        for tok in marker_inventory(text):
            if tok in marker_seen and tok in rare:
                alert("first_repeated_rare_marker", r["id"], i, {"marker": tok})
            marker_seen.add(tok)

        pid = r.get("parent_id")
        if pid is not None and pid in byid and meaningful_echo_text(text):
            if hashlib.sha256(text.encode()).hexdigest() == hashlib.sha256((byid[pid].get("text") or "").encode()).hexdigest():
                if pass_first is None:
                    pass_first = (r["id"], i, pid)
                alert("first_passed_identical_content", r["id"], i, {"parent": pid})

        for threshold_name, fam, thr in (("cmd_reaches_10", "cmd", 10), ("img_reaches_10", "img", 10),
                                         ("link_reaches_10", "link", 10), ("eval_reaches_10", "eval", 10)):
            if family_cum[fam] == thr:
                alert(threshold_name, r["id"], i, {"count": thr})

    outdoc = {
        "alerts": alerts,
        "family_cumulative_final": family_cum,
        "first_passed_identical_content": pass_first,
    }
    (out / "early_flags.json").write_text(json.dumps(outdoc, indent=2), encoding="utf-8")
    with open(out / "early_flags.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "row_id", "row_index"])
        for a in alerts:
            w.writerow([a["name"], a["row_id"], a["row_index"]])


def export_viewer(out, nodes, edges):
    passed = [e for e in edges if e["edge_type"] == "passed_identical_content"]
    node_ids = set()
    for e in passed:
        node_ids.add(e["source"]); node_ids.add(e["target"])
    if not node_ids:
        node_ids = {n["id"] for n in nodes if str(n["id"]).startswith("R")}
    if len(node_ids) > 3000:
        node_ids = set(sorted(node_ids)[:3000])
    nodes_out = [{"id": n, "label": n} for n in sorted(node_ids)]
    edges_out = [{"from": e["source"], "to": e["target"], "label": "passed"} for e in passed
                 if e["source"] in node_ids and e["target"] in node_ids]
    html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Swarm Information Passage DAG</title>
<style>body{font-family:system-ui;background:#0f172a;color:#e2e8f0;margin:16px}#mynetwork{height:780px;background:#1e2932;border-radius:8px}</style>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
</head><body>
<h1>Swarm Information Passage DAG (passed identical content)</h1>
<p>Nodes: """ + str(len(nodes_out)) + """ | Edges: """ + str(len(edges_out)) + """</p>
<div id="mynetwork"></div>
<script>
const nodes=new vis.DataSet(""" + json.dumps(nodes_out) + """);
const edges=new vis.DataSet(""" + json.dumps(edges_out) + """);
const network=new vis.Network(document.getElementById("mynetwork"),{nodes,edges},{layout:{hierarchical:{direction:'LR',sortMethod:'directed'}},physics:false});
</script></body></html>"""
    (out / "info_passage_dag.html").write_text(html, encoding="utf-8")

    preview_nodes = [n["id"] for n in nodes if str(n["id"]).startswith("R")][:1000]
    preview_set = set(preview_nodes)
    preview_edges = [e for e in edges if e["source"] in preview_set or e["target"] in preview_set]
    vis_nodes = [{"id": n, "label": n} for n in preview_nodes]
    vis_edges = [{"from": e["source"], "to": e["target"], "title": e["edge_type"]} for e in preview_edges]
    html2 = """<!doctype html>
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
    (out / "viewer.html").write_text(html2, encoding="utf-8")

    with open(out / "info_passage_dag.dot", "w", encoding="utf-8") as f:
        f.write("digraph info_passage {\n  rankdir=LR;\n")
        for n in sorted(node_ids):
            f.write('  "' + n + '";\n')
        for e in edges_out:
            f.write('  "' + e["from"] + '" -> "' + e["to"] + '";\n')
        f.write("}\n")


def write_observer_report(out, row_count):
    conn = sqlite3.connect(str(out / "swarm_reconstruction.sqlite3"))
    node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    ec = conn.execute("SELECT edge_type,COUNT(*) FROM edges GROUP BY edge_type ORDER BY COUNT(*) DESC").fetchall()
    passed = conn.execute("SELECT COUNT(*) FROM edges WHERE edge_type='passed_identical_content'").fetchone()[0]
    conn.close()
    lines = []
    lines.append("# Swarm Reconstruction Observer Report")
    lines.append("")
    lines.append("- source rows: {0}".format(row_count))
    lines.append("- graph nodes (including synthetic atoms): {0}".format(node_count))
    lines.append("- graph edges: {0}".format(edge_count))
    for k, v in ec:
        lines.append("- {0}: {1}".format(k, v))
    lines.append("")
    lines.append("## strongest propagation signal")
    lines.append("- passed_identical_content edges: {0}".format(passed))
    lines.append("")
    lines.append("## What was reconstructed")
    lines.append("- Parent lineage: producer -> derived record (execution/output lineage).")
    lines.append("- Exact echo edges: first -> later occurrence of byte-identical content.")
    lines.append("- Passed content edges: parent and child are byte-identical (information passed unchanged).")
    lines.append("- Rare marker edges: structural coupling among records sharing an uncommon pivot.")
    lines.append("- Template echo edges: campaign-shape reuse among payloads.")
    lines.append("")
    lines.append("## What an investigator still cannot prove with this dataset")
    lines.append("1. Precise chronological order: every time_utc is null; ID order is observed order only.")
    lines.append("2. True identity behind redaction handles; handles are masks, not people.")
    lines.append("3. Whether parent-child lineage is execution vs storage/recovery.")
    lines.append("4. Out-of-band channel content (image beacons, proxy calls, console output, server state).")
    lines.append("5. Exact causal intent or collusion; structural correlation is not causation.")
    lines.append("6. Effects of injected command fragments; only their presence is recorded, not execution outcomes beyond returned text.")
    lines.append("7. Deduplication of agents: one operator or many accounts is not resolvable from redacted IDs.")
    (out / "observer_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Swarm propagation reconstruction tool")
    sub = ap.add_subparsers(dest="command", required=True)
    cb = sub.add_parser("build")
    cb.add_argument("--input", required=True)
    cb.add_argument("--out-dir", required=True)
    cb.add_argument("--limit", type=int, default=None)
    cb.add_argument("--max-marker-freq", type=int, default=25)
    cb.add_argument("--min-confidence", type=float, default=0.5)
    args = ap.parse_args()
    if args.command == "build":
        build_dataset(args.input, pathlib.Path(args.out_dir), args.limit,
                      args.max_marker_freq, args.min_confidence, True)
        conn = sqlite3.connect(str(pathlib.Path(args.out_dir) / "swarm_reconstruction.sqlite3"))
        print("nodes={0} edges={1}".format(conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0],
                                           conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]))
        print("passed_identical=", conn.execute("SELECT COUNT(*) FROM edges WHERE edge_type='passed_identical_content'").fetchone()[0])
        conn.close()
        ef = json.load(open(pathlib.Path(args.out_dir) / "early_flags.json"))
        print("early alerts:", [(a['name'], a['row_id'], a['row_index']) for a in ef['alerts']])


if __name__ == "__main__":
    main()
