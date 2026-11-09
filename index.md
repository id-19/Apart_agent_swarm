# Swarm Traces Reconstruction Index

## Report handoff

- [REPORT_HANDOFF.md](./REPORT_HANDOFF.md) — report-ready conclusion, quotable
  counts, evidence boundaries, and canonical source map.

## Primary report

- [FINAL_RECONSTRUCTION_REPORT.md](./FINAL_RECONSTRUCTION_REPORT.md)
- [FINAL_summary.md](./FINAL_summary.md)
- [report.md](./report.md)

## Canonical graph and validation

- `forensics/run_2026/core/core_rows.ndjson` — 187,242 retained rows, one per cleaned sample.
- `forensics/run_2026/core/core_edges.ndjson` — 459,448 info-dependency core edges.
- `forensics/edges/edge_conditions.py` — authoritative edge conditions and schema.
- `forensics/edge_class_acceptance.json` — 10%/5% sampling acceptance.
- `forensics/disputed_edges.jsonl` — retained disputes.
- `forensics/edge_validation_report.md` — validation report.

## Phase 2 cluster artifacts

- `forensics/run_2026/cluster_signature_profiles.json` — 267,439 trigger-defined clusters.
- `forensics/run_2026/cluster_rankings.json`
- `forensics/run_2026/cluster_iteration_log.jsonl`
- `forensics/run_2026/cluster_disputes.jsonl`
- `forensics/run_2026/node_taxonomy_labels.jsonl` — every retained row with L1/L4/nested labels.
- `forensics/run_2026/cluster_coverage.json` — 100% coverage by L1 exact body.
- `forensics/run_2026/cluster_trigger_validation.json` — disproof trigger validation.

## Phase 3 temporal artifacts

- `forensics/run_2026/temporal_anchor_ledger.json` — 1,851 valid anchors.
- `forensics/run_2026/temporal_order_edge_classes.json` — temporal classifications over 945 grounded links.
- `forensics/run_2026/time_lead_candidates.json` — explicit lead candidates.
- `forensics/run_2026/temporal_conflict_report.json` — conflicts retained.
- `forensics/run_2026/chronology_partitions.jsonl` — explicit-time partitions.
- `forensics/run_2026/time_evidence.csv` and `timeline_chains.jsonl`.
- `forensics/run_2026/time_reasoning.md`, `temporal_comparison_audit.md`, `temporal_learnings.md`.

## Phase 4 event artifacts

- `forensics/run_2026/external_event_timeline.md`
- `forensics/run_2026/external_row_to_report_citations.tsv`
- `forensics/run_2026/cluster_to_event_candidates.jsonl`
- `forensics/run_2026/external_event_to_cluster_candidates.tsv`
- `forensics/run_2026/external_created_events.tsv`
- `forensics/run_2026/external_unmatched_events.md`
- `forensics/run_2026/external_false_parallel_patterns.md`
- `forensics/run_2026/event_support_scores.json`

## Phase 5 information-flow artifacts

- `forensics/run_2026/info_flow_edges_v1.jsonl` — 60,256 directed flow edges.
- `forensics/run_2026/info_flow_evidence.json`
- `forensics/run_2026/node_reconstruction_paths.json` — 59,311 paths.
- `forensics/run_2026/info_flow_visualization_export.json`

## Segmentation and early-detection artifacts

- `forensics/run_2026/graph_segments_v1.json` — 100 low-level structural segments.
- `forensics/findings/early_detection_verdict.md`
- `forensics/run_2026/reconstruction_components.csv`
- `forensics/run_2026/reconstruction_graph_v1.jsonl`

## Reproducibility

- `RUN.md`
- `forensics/reproduce_reconstruction.sh`
- `forensics/reconstruction_log.jsonl`
- `forensics/reconstruction_artifact_manifest.json`
