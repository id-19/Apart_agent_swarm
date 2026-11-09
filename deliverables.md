# Deliverables

## Authority and recovery

- `REPORT_HANDOFF.md` is the report-writing handoff and states the evidence
  boundaries explicitly.
- `FINAL_ARTIFACT/` is the canonical shipped artifact set.
- The root-level reports and `forensics/` tree are recovered working history and
  reproducibility material. Keep them for provenance; use the final artifact for
  final counts and wording.
- `FINAL_ARTIFACT/plans/` contains the seven recovered phase plans.

## Canonical report set
- `index.md` - navigable index.
- `report.md` - report body.
- `FINAL_summary.md` - concise final counts and limits.
- `FINAL_RECONSTRUCTION_REPORT.md` - original full reconstruction report.

## Graph evidence
- `forensics/run_2026/core/core_rows.ndjson` - 187,242 retained rows.
- `forensics/run_2026/core/core_edges.ndjson` - 459,448 standard four-field edges.
- `forensics/edges/edge_conditions.py` - edge trigger specification.
- `forensics/edge_class_acceptance.json` - 10%/5% validation counts.
- `forensics/disputed_edges.jsonl` - retained disputes.

## Clusters and taxonomy
- `forensics/run_2026/cluster_signature_profiles.json`
- `forensics/run_2026/cluster_rankings.json`
- `forensics/run_2026/cluster_iteration_log.jsonl`
- `forensics/run_2026/cluster_disputes.jsonl`
- `forensics/run_2026/node_taxonomy_labels.jsonl`
- `forensics/run_2026/cluster_coverage.json`
- `forensics/run_2026/cluster_trigger_validation.json`

## Temporal evidence
- `forensics/run_2026/temporal_anchor_ledger.json`
- `forensics/run_2026/temporal_order_edge_classes.json`
- `forensics/run_2026/time_lead_candidates.json`
- `forensics/run_2026/temporal_conflict_report.json`
- `forensics/run_2026/chronology_partitions.jsonl`
- `forensics/run_2026/timeline_chains.jsonl`
- `forensics/run_2026/time_evidence.csv`
- `forensics/run_2026/time_reasoning.md`

## Event and information flow
- `forensics/run_2026/external_event_timeline.md`
- `forensics/run_2026/cluster_to_event_candidates.jsonl`
- `forensics/run_2026/info_flow_edges_v1.jsonl`
- `forensics/run_2026/info_flow_evidence.json`
- `forensics/run_2026/node_reconstruction_paths.json`
- `forensics/run_2026/info_flow_visualization_export.json`

## Visualization and audit
- `forensics/run_2026/structural_visualization.html`
- `forensics/run_2026/curated_visualization_1000.json`
- `forensics/run_2026/full_destructive_audit.json`

## Reproducibility
- `RUN.md`
- `forensics/reproduce_reconstruction.sh`
- `forensics/reconstruction_log.jsonl`
- `forensics/reconstruction_artifact_manifest.json`
