#!/usr/bin/env python3
import json, collections
from pathlib import Path

root = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
timed = {}
for line in Path("/Users/id19/scratchpad/temporal_subset/temporal_timestamps.jsonl").open():
    if line.strip():
        row = json.loads(line)
        # Keep only cues with an actual numeric epoch. A cue that matches a
        # calendar-like string but has no machine epoch is not a usable anchor.
        if row.get("min_epoch") is None:
            continue
        timed[row["id"]] = row

core_edges = []
for line in (root / "forensics/run_2026/core/core_edges.ndjson").open():
    if line.strip():
        core_edges.append(json.loads(line))

out = []
for e in core_edges:
    a, b = e["source"], e["target"]
    if a in timed and b in timed:
        out.append({
            "edge_type": "TIME_DEPENDENCY",
            "source": a,
            "target": b,
            "proof": e["proof"],
            "supporting_dependency_class": e["edge_type"],
            "time_anchor_ids": [a, b],
        })
single_anchor = 0
for e in core_edges:
    a, b = e["source"], e["target"]
    if (a in timed) != (b in timed) and e["edge_type"] == "PARENT_DIRECT":
        out.append({
            "edge_type": "TIME_DEPENDENCY",
            "source": a,
            "target": b,
            "proof": e["proof"],
            "supporting_dependency_class": "PARENT_DIRECT",
            "time_anchor_id": a if a in timed else b,
        })
        single_anchor += 1

adj = collections.defaultdict(set)
for e in core_edges:
    if e["source"] in timed and e["target"] in timed:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])
seen = set()
component_sizes = []
for node in timed:
    if node in seen:
        continue
    stack = [node]
    comp = set()
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        comp.add(x)
        stack.extend(adj[x] - seen)
    component_sizes.append(len(comp))

support_counts = collections.Counter(e["supporting_dependency_class"] for e in out if "supporting_dependency_class" in e)
report = {
    "time_anchor_rows": len(timed),
    "time_anchor_kinds": {
        kind: sum(r.get("kind") == kind for r in timed.values())
        for kind in sorted({r.get("kind") for r in timed.values()})
    },
    "time_dependency_edges": len(out),
    "edges_with_both_endpoints_timed": sum(1 for e in out if "time_anchor_ids" in e),
    "single_anchor_parent_edges": single_anchor,
    "single_anchor_rows_not_in_filtered_sample_index?": "Core parent source IDs may not be rows, unlike Graph generation gap",
    "components_among_time_anchors": sum(size > 1 for size in component_sizes),
    "max_time_anchor_component": max(component_sizes) if component_sizes else 0,
    "support_class_counts": dict(sorted(support_counts.items())),
}
marker_counts = collections.Counter()
for r in timed.values():
    for marker in r.get("rare_markers", []):
        marker_counts[marker] += 1
report["top_time_anchor_markers"] = marker_counts.most_common(20)

out_dir = root / "forensics" / "run_2026"
(out_dir / "time_dependency_links.ndjson").write_text(
    "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in out),
    encoding="utf-8",
)
(out_dir / "time_dependency_summary.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(report, indent=2))
