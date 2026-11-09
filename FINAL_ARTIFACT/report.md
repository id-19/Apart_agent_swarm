# Executive Reconstruction Report: Swarm Traces

## Bottom line

The 187,242 retained Swarm Traces rows support structural reconstruction at the level of exploit templates, body replays, parent bursts, marker/route pivots, and information-flow candidates. They do not support identity, agency, authorization, execution outcome, or row-level chronology: `time_utc` is null in every retained row and all operational identifiers are redacted.

## Evidence counts

| Evidence class | Count | Interpretation limit |
|---|---:|---|
| Retained rows | 187,242 | All retained row time is null |
| Non-candidate graph edges | 459,448 | Structural co-association, not causation |
| Components | 26,043 | 144,075-row largest component is a broad hub |
| Singleton components | 22,894 | No linkage evidence |
| L1 exact-body clusters | 161,945 | 18,728 recurring (44,025 rows); 143,217 singletons |
| L3 marker clusters | 79,451 | Count threshold-free; broad hubs visibility-only |
| L4 structural components | 26,043 | Union-find over validated edges |
| Cluster coverage | 100% | Each row is in at least one L1 exact-body cluster |
| Valid timestamp anchors | 1,851 | Cue metadata only; 31 invalid retained as evidence |
| Grounded structural links | 945 | 11 explicit leads, 929 same-day anchor pairs |
| Information-flow edges | 60,256 | Parent-only direction or grounded stored direction |
| Curated visualization nodes | 1,000 | Curated subset, not population sample |
| Low-level segment signatures | 100 | 87,438 primary exact-bucket rows primary exact-bucket rows at exact 260-character normalized bucket level |
| Secondary marker-class segments | 100 | 133,242 rows (71.2%) across 18,657 distinct exact marker-class inventories (digits collapsed, all markers retained) |

## Validated graph

`EXACT_BODY` 23,471 edges over 18,999 raw-identical groups (42,470 rows); `NORMALIZED_REPLAY` 1,826 chains; `PARENT_DIRECT` 59,313; `SAME_PARENT_SIBLING` 33,466; `MARKER_SAME` 222,495; `MARKER_ENDPOINT` 118,877. Core audit reports `loophole_count: 0` and only two unresolved parent endpoints: storage parent `R0113768`. Edges use the four-field schema `source`, `dest`, `edge_class`, and `edge_sub_class`; triggers are retained inside the nested subclass.

## Cluster and pivot evidence

Top pivots include `[REDACTED:destination:000003]` (13,880 rows), `[PROXY 4 URL 72]` (11,977 rows), `[ENCODED BLOB]` (11,486 rows), `[SERVICE 3 URL 209]` (11,229 rows), and `[SERVICE 14 URL 4]` (9,268 rows). The largest parent bursts are `R0024455` with 858 child records and `R0036471` with 270. Independent adversarial validation tested 60 recurring L1 clusters, 628 L3 marker clusters, and 85 L4 components on 4,049 adversarial rows; all tested triggers failed as required.

## Temporal evidence

No row may be assigned to a report event at row level. The 1,851 valid anchors and 945 grounded links support only advisory partitions, precedence candidates, same-day anchors, conflicts, and partitions. Historical TIME_DEPENDENCY had 5,714 rows but only 11 strict chronological orders and 850 direction violations, so TIME_DEPENDENCY is withdrawn as an active causal family.

## External event mapping

Only five sample-to-report correspondences are retained: `R0000007`, `R0000096`, `R0000617`, `R0101198`, and `R0062606`. Each is a structural or composite payload correspondence around 2026-07-09 through 2026-07-13, not proof of execution or timestamp assignment. External reports contain 38 dated events and approximately 17,600 recovered actions in 6,280 clusters. Broad external patterns that do not map locally, or broad structural clusters, are not treated as proven row-level incidents.

## Information flow

60,256 directed edges include 59,311 parent-to-child body revision or replay edges and 945 grounded structural-flow candidates. 59,311 reconstruction paths to roots are available. No flow direction is invented: parent links use stored parent metadata, grounded-links use stored direction, and symmetric classes remain symmetric.

## Near-body candidates

Near-body similarity is candidate adjacency, not coordination proof. A materialized exemplar set now includes 205 exact computed D1/D2 pairs (79 D1 and 126 D2), each with its measured Levenshtein distance, normalized trigger, and 3 disproof rows. The full tier counts remain D0 66,592, D1 308,204, D2 2,922,781, and D3 15,621,579. The full 18,852,564-row candidate matrix is retained as tier counts and representative exemplars; D3 remains unusable as coordination evidence because it is broad candidate adjacency.

## Segmentation

The 100 low-level segment signatures cover 87,438 primary exact-bucket rows primary exact-bucket rows using deterministic, exact normalized 260-character text buckets. They are evidence families, not behavioral labels. Every row remains represented by one of the exact or marker-class tiers, or by its exact residual inventory label; no catch-all behavioral assignment is made. The remaining 53.3% are not assigned to a catch-all bucket; exact normalized signatures at this resolution simply occur once, so forcing all rows into 100 segments would invent false family membership.
Secondary `marker_class_segments.json` sorts the entire marker inventory with digits normalized to `<N>` and no slice/cap: 100 signatures cover 133,242 rows (71.2%), with 18,657 exact marker-class inventories before truncation. The residual rows differ in marker-class inventory or have no markers; no catch-all bucket is used.

## Measurement boundaries and residual data limitations

- Unresolved endpoints: storage parent `R0113768` (2 directed PARENT_DIRECT references).
- Broad hub: `SC-L4-COMP-00001` contains 144,075 rows and is visibility-only as marker/endpoint co-occurrence, not one operation. It has 48,467 exact transit-marker subsets, with the top 12 covering 39.2% and 37,602 singleton-subset rows; these are visibility subsets, not proof of distinct agents.
- Candidate matrix policy: 205 exact D1/D2 exemplars are materialized; tier counts are aggregate; the complete 18.85M matrix remains intentionally unmaterialized and D3 is not usable as coordination evidence.
- `time_utc` is null for all 187,242 retained rows.
- Stable IDs are storage identifiers, not identities or principals.
- Early-detection families require parent provenance, marker rareness, repetition, and context; report structures alone can arise from safe fixtures.

## Deliverable set

Primary top-level reports: `index.md`, `report.md`, `FINAL_summary.md`, `FINAL_RECONSTRUCTION_REPORT.md`, and `EXECUTIVE_REPORT.md`. Detailed machine-verifiable artifacts are under `forensics/`, especially `forensics/run_2026/`. Full validation evidence is in `full_destructive_audit_v2.json` and `cluster_adversarial_validation.json`.


## Phase gate evidence

- P1: four-field core edges (459,448) and edge-condition spec; audit 0 failed resolved edges, 2 documented orphan parents.
- P2: 161,945 L1, 79,451 L3, 26,043 L4 clusters; 44,025 recurring body rows (23.5%) and 164,348 multi-row components; 4,049 adversarial nonmembers failed triggers.
- P3: 1,851 valid anchors, 945 grounded links, 11 explicit leads, 0 conflict findings; partitions retained.
- P4: 5 structural event anchors, external-unmatched notes, 4 reconstructed events; no row event assignment.
- P5: 60,256 directed flow edges and 59,311 root paths.
- P6: curated 1,000-node/1,230-edge graph, 100 exact plus 100 marker-class segment tiers, exhaustive endpoint audit.
- P7: evidence bundle, manifest, report, index, graphs committed; repository collapsed to seven files.
