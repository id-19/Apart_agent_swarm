#!/usr/bin/env bash
set -euo pipefail

cd /Users/id19/Programming/AI_research/Apart_agent_swarm

python3 forensics/filter_useless_rows.py
python3 forensics/build_graph_core.py
g++ -O3 -std=c++17 -Wall -Wextra -o forensics/build_near_body_candidates forensics/build_near_body_candidates.cpp
forensics/build_near_body_candidates
python3 forensics/run_2026/near_distance_stats.py
python3 forensics/run_2026/audit_near_candidates.py
python3 forensics/run_2026/verify_core_graph.py

python3 - <<'PY'
import json, pathlib
root=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
assert root.joinpath("Data/redacted_filtered.jsonl").exists()
assert (root/"forensics/run_2026/core/core_edges.ndjson").stat().st_size > 50_000_000
core=json.load(open(root/"forensics/run_2026/core/graph_core_stats.json"))
assert core["edges"] == 459448
candidate=json.load(open(root/"forensics/run_2026/near_distance_stats.json"))
assert candidate["distance_3"]["edge_count"] == 18359221
audit=json.load(open(root/"forensics/run_2026/near_distance_candidate_audit.json"))
assert audit["duplicate_keys"] == 0
print("reproduction completed; full pass checked")
PY
