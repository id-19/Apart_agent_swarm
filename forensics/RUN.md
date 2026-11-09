# Reproduction run

All commands run from the repository root:

```bash
cd /Users/id19/Programming/AI_research/Apart_agent_swarm
```

1. Filter trivial/short rows:
   ```bash
   python3 forensics/filter_useless_rows.py
   ```

2. Build the row-level core graph:
   ```bash
   python3 forensics/build_graph_core.py
   ```

3. Rebuild near-body candidates. The C++ constants are already set in
   `forensics/build_near_body_candidates.cpp` (`K=3`, `MAXD=3`,
   `MAX_REPS=1000000`, `PER_SOURCE_CAP=1000000`):
   ```bash
   g++ -O3 -std=c++17 -Wall -Wextra \
       -o forensics/build_near_body_candidates \
       forensics/build_near_body_candidates.cpp
   forensics/build_near_body_candidates \
       Data/redacted_filtered.jsonl \
       forensics/run_2026
   ```

4. Aggregate per-distance candidate links:
   ```bash
   python3 forensics/run_2026/near_distance_stats.py
   ```

5. Time-anchor profile:
   ```bash
   python3 forensics/run_2026/build_time_dependency.py
   ```

6. Deterministic structural segments:
   ```bash
   python3 forensics/run_2026/build_graph_segments.py
   ```

7. Parent mutation probe:
   ```bash
   python3 forensics/run_2026/parent_mutation_profile.py
   ```

8. Audit core edges:
   ```bash
   python3 forensics/run_2026/verify_core_graph.py
   ```

9. Audit near-body candidate distances:
   ```bash
   python3 forensics/run_2026/audit_near_candidates.py
   ```

Key outputs:
- `Data/redacted_filtered.jsonl`
- `forensics/run_2026/core/core_rows.ndjson`
- `forensics/run_2026/core/core_edges.ndjson`
- `forensics/graph_info_dependency_edges.ndjson`
- `forensics/graph_time_dependency_edges.ndjson`
- `forensics/run_2026/core/graph_core_stats.json`
- `/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson`
- `forensics/run_2026/near_distance_stats.json`
- `forensics/run_2026/time_dependency_links.ndjson`
- `forensics/run_2026/graph_segments_v1.json`
- `FORENSICS_FINAL_REPORT.md`


## Consolidation cleanup (current)

- Projection edge schema now uses `source_id`, `destination_id`, `source`, `target`,
  `edge_class`, `trigger`, `distance`, and explicit `direction` only. `evidence_snippet`
  and `bucket_hash` are removed.
- `PARENT_DIRECT`, `PARENT_MUTATION`, and `TIMESTAMP_ANCHOR` remain directed.
  Structurally symmetric classes are marked `direction: "symmetric"`; no reverse edges
  are silently created.
- `TIME_DEPENDENCY` is withdrawn. Steps 5 above is reduced to timestamp-anchor
  inventory metadata only: `forensics/run_2026/timestamp_anchor_inventory.json`
  (1851 anchors). No temporal relation edges are generated.
- The 18,852,564-row near-body candidate relation is intentionally not materialized.
  `forensics/graph_edges_v2.jsonl` now contains the 1,310,038 non-candidate edges only.
- `forensics/clean_tap_datasets.py` imports `forensics.graph` (not the typo path).
- Legacy dumps/checkpoints were moved to `forensics/archive/`; the typo directory
  `foremsics` was removed.
