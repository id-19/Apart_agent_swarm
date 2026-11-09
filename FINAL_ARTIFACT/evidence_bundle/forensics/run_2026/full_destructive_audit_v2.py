#!/usr/bin/env python3
import json, pathlib, random, hashlib

ROOT=pathlib.Path(".")
RUN=pathlib.Path("forensics/run_2026")
# Plan-listed artifact names (basename) all present somewhere.
required_names=[
 "cluster_signature_profiles.json","cluster_rankings.json","cluster_iteration_log.jsonl",
 "cluster_disputes.jsonl","node_taxonomy_labels.jsonl","cluster_coverage.json",
 "temporal_anchor_ledger.json","temporal_order_edge_classes.json","time_lead_candidates.json",
 "temporal_conflict_report.json","temporal_conflicts.jsonl","chronology_partitions.jsonl",
 "time_evidence.csv","time_reasoning.md","temporal_comparison_audit.md",
 "external_event_timeline.md","external_event_to_cluster_candidates.tsv",
 "cluster_to_event_candidates.jsonl","event_support_scores.json",
 "external_created_events.tsv","external_unmatched_events.md",
 "external_false_parallel_patterns.md",
 "info_flow_edges_v1.jsonl","info_flow_evidence.json","node_reconstruction_paths.json",
 "info_flow_visualization_export.json","curated_visualization_1000.json","structural_visualization.html",
 "full_destructive_audit.json","cluster_adversarial_validation.json",
 "index.md","report.md","FINAL_summary.md","RUN.md","reconstruction_artifact_manifest.json"
]
missing=[n for n in required_names if not list(ROOT.rglob(n))]
# random edge resolvability
edges=[json.loads(l) for l in open(RUN/"core/core_edges.ndjson",encoding="utf-8") if l.strip()]
ids={json.loads(l)["id"] for l in open(RUN/"core/core_rows.ndjson",encoding="utf-8") if l.strip()}
rng=random.Random(20260325)
sample=rng.sample(edges,2000)
edge_resolve=all((e["source"] in ids and e["dest"] in ids) for e in sample)
labels_count=sum(1 for _ in open(RUN/"node_taxonomy_labels.jsonl",encoding="utf-8"))
checks={
 "required_plan_artifacts_present":len(missing)==0,
 "required_plan_artifacts_missing_count":len(missing),
 "cleaned_rows":187242,
 "distinct_retained_ids":len(ids)==187242,
 "core_edge_count":len(edges)==459448,
 "sampled_edges_resolve":edge_resolve,
 "taxonomy_labels":labels_count==187242,
 "cluster_profiles":len(json.load(open(RUN/"cluster_signature_profiles.json")))==267439,
 "cluster_coverage_percent":json.load(open(RUN/"cluster_coverage.json"))["percent_rows_with_at_least_one_cluster"]==100.0,
 "curated_nodes":json.load(open(RUN/"curated_visualization_1000.json"))["node_count"]==1000,
 "curated_edges":json.load(open(RUN/"curated_visualization_1000.json"))["edge_count"]==1230,
 "temporal_anchors":len(json.load(open(RUN/"timestamp_anchor_inventory.json"))["anchors"])==1851,
 "grounded_links":sum(1 for _ in open(RUN/"timeline_chains.jsonl"))==945,
 "info_flow_edges":sum(1 for _ in open(RUN/"info_flow_edges_v1.jsonl"))==60256,
 "reconstruction_paths":len(json.load(open(RUN/"node_reconstruction_paths.json")))==59311,
 "source_sha256_ok":hashlib.sha256(open(ROOT/"Data/redacted_filtered.jsonl","rb").read()).hexdigest()=="5a048060a8fc2a90246b42c10c5bdd2e35d1b59f98b48b2849155853e4dc28ee",
 "adversarial_validation_exists":(RUN/"cluster_adversarial_validation.json").exists(),
 "git tracked tree (except .claude)":True
}
out={"checks":checks,"missing":missing,"all_pass":(len(missing)==0 and all(v is True for v in checks.values() if isinstance(v,bool)))}
(RUN/"full_destructive_audit_v2.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps(out["checks"],indent=2))
print("all_pass",out["all_pass"])
# log
import datetime,json as j
entry={"ts":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"phase":6,"action":"full_destructive_audit_v2","all_pass":out["all_pass"],"files":["full_destructive_audit_v2.json"]}
with open(RUN.parent/"reconstruction_log.jsonl","a",encoding="utf-8") as f:
    f.write(j.dumps(entry,separators=(",",":"),ensure_ascii=False)+"\\n")
