# Historical reproduction run

This is the recovered generation recipe, not a command to run casually against
the final workspace. Several steps write derived outputs and may replace
artifacts. The canonical final result is already preserved in `FINAL_ARTIFACT/`;
use its manifest and `REPORT_HANDOFF.md` for report writing and verification.

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

Historical key outputs:
- `Data/redacted_filtered.jsonl`
- `forensics/run_2026/core/core_rows.ndjson`
- `forensics/run_2026/core/core_edges.ndjson`
- `forensics/run_2026/core/graph_core_stats.json`
- `forensics/run_2026/near_distance_stats.json`
- `forensics/run_2026/graph_segments_v1.json`

The near-body candidate matrix is intentionally not retained in the final
workspace; only aggregate counts, audits, and the generator recipe remain.
Historical `TIME_DEPENDENCY` output was withdrawn from the active relation
families after temporal-direction audit. Do not cite either as causal evidence.
