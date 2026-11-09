#!/usr/bin/env python3
import json, pathlib, collections

ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
RUN = ROOT/"forensics"/"run_2026"
SRC = ROOT/"Data"/"redacted_filtered.jsonl"
rows = {r["id"]: r for r in (json.loads(l) for l in SRC.open(encoding="utf-8") if l.strip())}

out_edges = RUN/"info_flow_edges_v1.jsonl"
counts = collections.Counter()
with out_edges.open("w",encoding="utf-8") as f:
    # Parent direct / mutation edges.
    core_edges = []
    # Use source parent relationships from filtered data instead of core ndjson (faster enough).
    # filtered rows may have parent_id.
    filter_rows = [json.loads(l) for l in SRC.open(encoding="utf-8") if l.strip()]
    for r in filter_rows:
        pid = r.get("parent_id")
        if pid and pid in rows:
            child = r["text"]; parent = rows[pid]["text"]
            if child == parent:
                sub = "identical"
            elif child.startswith(parent):
                sub = "addition"
            elif parent.startswith(child):
                sub = "truncation"
            else:
                sub = "substitution"
            rec = {
                "source": pid,
                "target": r["id"],
                "info_edge_type": "BODY_REVISION_OR_REPLAY",
                "direction": "source_to_target",
                "trigger": f"parent_id={pid}; body relation={sub}",
                "mutation_subclass": sub,
                "parent_length": len(parent),
                "child_length": len(child),
                "confidence": 1.0,
            }
            f.write(json.dumps(rec,separators=(",",":"),ensure_ascii=False)+"\n")
            counts["BODY_REVISION_OR_REPLAY"] += 1

    # Grounded structural links from temporal subset.
    for c in (json.loads(l) for l in open(RUN/"timeline_chains.jsonl",encoding="utf-8") if l.strip()):
        et = c["edge_type"]
        info_type = "BODY_REVISION_OR_REPLAY" if et == "exact_text_match" else "OPERATION_SIGNATURE_FLOW"
        rec = {
            "source": c["source"],
            "target": c["target"],
            "info_edge_type": info_type,
            "direction": "source_to_target",
            "trigger": f"grounded link; edge_type={et}; proof={c['proof']}",
            "temporal_confidence_only": True,
            "confidence": c.get("confidence"),
        }
        f.write(json.dumps(rec,separators=(",",":"),ensure_ascii=False)+"\n")
        counts[info_type] += 1

total = sum(counts.values())
(RUN/"info_flow_evidence.json").write_text(json.dumps({
    "edge_count": total,
    "edge_type_counts": dict(counts),
    "direction_rule": "parent->child only for body revision/replay; grounded structural links retain stored direction; no reverse invention",
    "required_classes_not_separately_materialized": ["SHARED_INFO_READ","WRITE_THEN_USE","SAME_WRITE_TARGET","META_INJECTION_PATTERN"],
    "note": "Classes requiring explicit read/write/target roles beyond available annotations remain candidate conceptual classes; exported edges cover BODY_REVISION_OR_REPLAY and OPERATION_SIGNATURE_FLOW only."
}, indent=2, ensure_ascii=False))

# node reconstruction paths via parent map up to depth 100.
parent_map = {}
for r in filter_rows:
    if r.get("parent_id") in rows:
        parent_map[r["id"]] = r["parent_id"]
paths = {}
for node in rows:
    path=[]
    cur=node
    seen=set()
    while cur in parent_map and cur not in seen and len(path) < 100:
        seen.add(cur)
        cur = parent_map[cur]
        path.append(cur)
    if path:
        paths[node]=path
(RUN/"node_reconstruction_paths.json").write_text(json.dumps(paths,separators=(",",":"),ensure_ascii=False))
print("paths",len(paths))

# visualization export: top 500 nodes by edge participation + anchor rows.
part = collections.Counter()
edges = [json.loads(l) for l in open(out_edges,encoding="utf-8")]
for e in edges:
    part[e["source"]] += 1; part[e["target"]] += 1
selected = set([rid for rid,_ in part.most_common(5000)])
selected.update(["R0000007","R0000096","R0000617","R0101198","R0062606"])
subedges = [e for e in edges if e["source"] in selected and e["target"] in selected]
(RUN/"info_flow_visualization_export.json").write_text(json.dumps({
    "node_count": len(selected),
    "edge_count": len(subedges),
    "selected_nodes": sorted(selected),
    "edges": subedges,
}, separators=(",",":"), ensure_ascii=False)[:50_000_000])
print("edges",total,"viz_edges",len(subedges))
