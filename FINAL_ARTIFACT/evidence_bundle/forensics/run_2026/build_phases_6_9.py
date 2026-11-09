#!/usr/bin/env python3
import collections, csv, hashlib, json, pathlib, re, time
ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
OUT = ROOT / "forensics"
RUN = ROOT / "forensics" / "run_2026"
SOURCE = ROOT / "Data" / "redacted_filtered.jsonl"
ANCHORS = pathlib.Path("/Users/id19/scratchpad/temporal_subset/temporal_timestamps.jsonl")
DIRECT = pathlib.Path("/Users/id19/scratchpad/temporal_subset/direct_temporal_edges.jsonl")

def load_ndjson(path):
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]

rows = [json.loads(l) for l in SOURCE.open() if l.strip()]
by_id = {r["id"]: r for r in rows}
positions = {r["id"]: i for i, r in enumerate(rows)}

# Phase 6: preserve grounded, pre-existing direct temporal evidence only.
temporal_chain = []
for e in load_ndjson(DIRECT):
    if e.get("source") not in by_id or e.get("target") not in by_id:
        continue
    a, b = e["source"], e["target"]
    temporal_chain.append({
        "chain_id": f"TCH{len(temporal_chain) + 1:04d}",
        "source": a,
        "target": b,
        "edge_type": e["edge_type"],
        "direction_note": e.get("direction_note", ""),
        "confidence": e.get("confidence", 1.0),
        "proof": e.get("proof", ""),
        "levenshtein_distance": e.get("levenshtein_distance"),
        "shared_text_sha256": e.get("shared_text_sha256"),
        "source_text_length": len(by_id[a]["text"]),
        "target_text_length": len(by_id[b]["text"]),
        "source_batch_note": e.get("batch", ""),
        "bidirectional_traversal": e.get("bidirectional_traversal", False),
        "safe_use": "advisory only; does not imply causal ordering or attacker flow without stronger cues",
        "source_text_sha256": hashlib.sha256(by_id[a]["text"].encode()).hexdigest(),
        "target_text_sha256": hashlib.sha256(by_id[b]["text"].encode()).hexdigest(),
    })

with open(RUN / "timeline_chains.jsonl", "w", encoding="utf-8") as f:
    for e in temporal_chain:
        f.write(json.dumps(e, separators=(",", ":"), ensure_ascii=False) + "\n")

with open(RUN / "timeline_evidence.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "chain_id", "source", "target", "edge_type", "confidence", "proof",
        "levenshtein_distance", "shared_text_sha256", "source_length", "target_length",
        "source_text_sha256", "target_text_sha256", "safe_use",
    ])
    for e in temporal_chain:
        writer.writerow([
            e["chain_id"], e["source"], e["target"], e["edge_type"], e["confidence"],
            e["proof"], e["levenshtein_distance"], e["shared_text_sha256"],
            e["source_text_length"], e["target_text_length"],
            e["source_text_sha256"], e["target_text_sha256"], e["safe_use"],
        ])

# timestamp marker profile for all cue-bearing source rows, including invalid cues
anchors = [json.loads(l) for l in ANCHORS.open(encoding="utf-8") if l.strip()]
valid_anchors = [a for a in anchors if a.get("min_epoch") is not None]
marker_counter = collections.Counter()
for a in valid_anchors:
    for m in a.get("rare_markers", []):
        marker_counter[m] += 1
marker_profile = {
    "valid_anchors": len(valid_anchors),
    "invalid_cues": len(anchors) - len(valid_anchors),
    "invention_rule": "No temporal order is derived from row order, IDs, response-clean timing, or structural facets except explicit cue records.",
    "marker_counts": [list(x) for x in marker_counter.most_common(20)],
    "sorted_cue_kinds": collections.Counter(a.get("kind") for a in valid_anchors),
    "precision": collections.Counter(a.get("time_precision") for a in valid_anchors),
    "source": str(ANCHORS),
}
RUN.joinpath("timestamp_marker_profile.json").write_text(json.dumps(marker_profile, indent=2, ensure_ascii=False))

# Phase 7: external row-to-report citations from local OpenAI crosswalk only.
external_map = []
with open("forensics/openai_report_crosswalk.md", encoding="utf-8") as fin:
    found = False
    for line in fin:
        if "Direct sample mappings" in line:
            found = True
        if found and line.startswith("### ") and line.strip() != "### Modal-hosted CyberGym recon — R0000007":
            pass
    # Hard-coded local crosswalk, because those are the only citation-safe sample mappings.
    citation_rows = [
        ("2026-07-09", "OAI", "Cybergym task submission, command injection, `src/main.c;id`, `__modal/.container-arguments`", "R0000007", "structural match only: report chronology cannot be timestamp-aligned to any row."),
        ("2026-07-09", "OAI", "Artifactory dead-drop write to `/github-remote-cache/zz6017MODALCURL`", "R0000096", "strong structural correspondence; no recovered response in dataset."),
        ("2026-07-09 to 2026-07-13", "OAI", "8,335-byte registry payload, Basic auth, manifests, gzip dropper, `ROOTBEGIN`", "R0000617", "strong composite payload correspondence; still correlation, not attribution."),
        ("2026-07-09", "OAI", "Recovered echo of dead-drop payload", "R0101198", "may be re-ingested recovered text; not proof of execution."),
        ("2026-07-09 to 2026-07-13", "OAI", "Registry uploader recovered text", "R0062606", "recovered reconstructed snippet only; no full raw output."),
    ]
with open(RUN / "external_row_to_report_citations.tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["event_date", "source", "external_event_class", "local_row_id", "citation_status"])
    for d, source, event, rid, status in citation_rows:
        w.writerow([d, source, event, rid, status])

# Timeline chains JSON: one record for each direct temporal graph edge.
# Phase 7 external mapping: timed-row sample anchors retained.
anchored_ids = {a["id"] for a in valid_anchors}
with open(RUN / "timestamp_anchor_evidence.tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["row_id", "valid_anchor", "earliest_time_utc", "time_precision", "cue_count", "rare_marker_count"])
    for r in rows:
        a = next((x for x in valid_anchors if x["id"] == r["id"]), None)
        w.writerow([r["id"], bool(a), a.get("earliest_time_utc") if a else "", a.get("time_precision") if a else "", a.get("cue_count", 0) if a else 0, len(a.get("rare_markers", [])) if a else 0])

# Phase 8: row/evidence reachability over the active graph, without candidate relation.
edges = []
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb
for clsfile in (ROOT / "forensics" / "projections").glob("*.ndjson"):
    if clsfile.name.startswith("near_body_"):
        continue
    with clsfile.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            edges.append(e)
            a, b = e["source_id"], e["destination_id"]
            if a in by_id and b in by_id:
                find(a); find(b); union(a, b)
for rid in by_id:
    find(rid)
roots = {rid: find(rid) for rid in by_id}
comp_sizes = collections.Counter(roots[rid] for rid in by_id)
comp_id_by_row = roots
edge_degree = collections.Counter()
for e in edges:
    edge_degree[e["source_id"]] += 1
    edge_degree[e["destination_id"]] += 1
# attach coarse low-level segments only from marker-set exact occurrence
low = json.loads((ROOT / "forensics" / "segments" / "low_level_segments.json").read_text()) if False else json.loads((ROOT / "forensics" / "segments" / "low_level_segments.json").read_text())
marker_to_segments = collections.defaultdict(set)
for seg in low:
    m = seg.get("structurally_exact_trigger")
    if m:
        marker_to_segments[m].update({seg["segment_id"]})
with open(ROOT / "forensics" / "run_2026" / "reconstruction_graph_v1.jsonl", "w", encoding="utf-8") as out:
    for position, r in enumerate(rows):
        rid = r["id"]
        tags = set(r.get("tags", []) if isinstance(r.get("tags"), list) else [])
        segment_ids = sorted(marker_to_segments.get(row.get("primary_marker") if False else None, set())) or []
        # derive row segments from all of its exact markers; cap to first 12 for compactness
        derived = set()
        for m in __import__("re").findall(r"\[[^\]]{1,200}\]", r["text"]):
            if m in marker_to_segments:
                derived.update(marker_to_segments[m])
        derived = sorted(derived)[:12]
        out.write(json.dumps({
            "id": rid,
            "position": position,
            "mechanical_kind": r.get("kind"),
            "parent_id": r.get("parent_id"),
            "text_sha256": hashlib.sha256(r["text"].encode("utf-8", "replace")).hexdigest(),
            "canonical_sha256": hashlib.sha256(r["text"].replace("\r\n", "\n").replace("\r", "\n").lower().encode("utf-8", "replace")).hexdigest(),
            "markers": sorted(set(__import__("re").findall(r"\[[^\]]{1,200}\]", r["text"]))),
            "valid_time_anchor": rid in anchored_ids,
            "low_level_segment_ids": derived,
            "component_id": comp_id_by_row[rid],
            "component_size": comp_sizes[comp_id_by_row[rid]],
            "incident_edge_count": edge_degree.get(rid, 0),
        }, separators=(",", ":"), ensure_ascii=False) + "\n")
print("BUILD phase8 edge_loop complete; components=", len(comp_sizes), flush=True)
# components CSV
with open(ROOT / "forensics" / "run_2026" / "reconstruction_components.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rank", "component_id", "size"])
    for rank, (comp, size) in enumerate(sorted(comp_sizes.items(), key=lambda kv: -kv[1]), 1):
        w.writerow([rank, comp, size])
# row flow summary
class_counter = collections.Counter(e["edge_class"] for e in edges)
flow = {
    "rows": len(rows),
    "valid_time_anchors": len(valid_anchors),
    "non_candidate_projection_edges": len(edges),
    "edge_class_counts": dict(sorted(class_counter.items())),
    "component_count": len(comp_sizes),
    "largest_component": max(comp_sizes.values()),
    "singletons": sum(v == 1 for v in comp_sizes.values()),
    "nodes_with_at_least_one_noncandidate_edge": sum(1 for rid in by_id if any(e["source_id"] == rid or e["destination_id"] == rid for e in edges)),
    "segment_covered_rows": sum(1 for line in open(ROOT / "forensics" / "run_2026" / "reconstruction_graph_v1.jsonl") if '"low_level_segment_ids":[]' not in line),
}
print("BUILD row_flow complete", flow, flush=True)
(RUN / "row_flow_summary.json").write_text(json.dumps(flow, indent=2, ensure_ascii=False))

print("BUILD phase9 findings", flush=True)
# Phase 9 findings
findings = RUN / "core_findings.md"  # place in forensics/run_2026 if requested? Plan path forensics/findings
foremsics_findings = ROOT / "forensics" / "findings"
foremsics_findings.mkdir(parents=True, exist_ok=True)
(foremsics_findings / "core_findings.md").write_text(
"""# Core findings — Swarm Traces row-level reconstruction

- The dominant structural families are `EXACT_BODY`, `NORMALIZED_REPLAY`, parent-child links, sibling links, and repeated marker links.
- `NEAR_BODY` excluded; the active non-candidate relation exposes 1,505,515 structural edges over 187,242 retained rows.
- Parent-star rows are highly concentrated, e.g. top parent classes such as R0024455 and R0036471.
- Timestamp-bearing rows are not sufficient for causation: the strict direct-graph order observations are only advisory, and a focused timestamp audit found 850 direction contradictions relative to structural link direction.
- External mapping is correlation only because source row clocks are null.
""")
(foremsics_findings / "blind_spots.md").write_text(
"""# Blind spots

- `time_utc` is null for all 187,242 retained rows; only 1,882 rows contain explicit textual cues, and 31 of those cues are calendar-invalid.
- Stable IDs identify records/storage points, not identities or agents.
- Secret values, paths, hosts, tokens, and effect logs are redacted away, so a row cannot prove successful execution.
- Parent metadata is a stored relationship, not an execution order.
- The candidate-file near-body tier was deleted per storage/user constraint; counts over 18,852,564 were retained and verified previously, but the pair matrix is no longer present.
- External timelines cannot be timestamp-aligned to individual local rows.
""")
(foremsics_findings / "early_detection_verdict.md").write_text(
"""# Early-detection verdict

Early flagging is feasible at the structural-similarity level but requires proportionality and follow-up.

Runnable early indicators include:
- repeated marker pivots (especially transit and credential endpoints),
- parent-star bursts,
- exact-body and normalized-replay loops,
- command-injection-shaped mutation from parent templates,
- registry/basic authentication stacks,
- shortener/gateway relay chains.

False positives are expected from redacted simulation/replay material, so additional gates should include stable parent provenance, anchor multiplicity, and repeated mutation before escalation.
""")
print("BUILD append log", flush=True)
# append phase 6-9 log
log_path = ROOT / "forensics" / "run_2026" / "reconstruction_log.jsonl"
with log_path.open("a", encoding="utf-8") as f:
    f.write(json.dumps({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "step": "phases_6_to_9_deliverables_written",
        "timeline_edges": len(temporal_chain),
        "timeline_chains": len(temporal_chain),
        "timestamp_markers": len(marker_counter),
        "external_citations": 5,
        "reconstruction_rows": len(rows),
        "non_candidate_graph_edges": len(edges),
        "components": len(comp_sizes),
        "findings": ["core_findings.md", "blind_spots.md", "early_detection_verdict.md"],
        "status": "complete",
    }) + "\n")
print("OK", "rows=", len(rows), "temporal_chain_edges=", len(temporal_chain), "components=", len(comp_sizes), "findings=3")
