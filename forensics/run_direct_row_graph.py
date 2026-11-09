# -*- coding: utf-8 -*-
"""Build a direct row-to-row graph; no atom/synthetic bucket intermediates."""
import json
import sqlite3
import itertools
from pathlib import Path

FILTERED = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted_filtered.jsonl")
DB_PATH = "/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/direct_row_graph.sqlite3"
CAND = Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")

ids = set()
for line in FILTERED.open() if FILTERED.exists() else []:
    if line.strip():
        ids.add(json.loads(line)["id"])
ids = sorted(ids)

# compile exact buckets from old relational graph's atomic SHA records
sqlite_src = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/swarm_reconstruction_full/swarm_reconstruction.sqlite3")
src = sqlite3.connect(sqlite_src)
src.row_factory = sqlite3.Row
exact_members = {}
for row in src.execute("SELECT source_node,target_node,proof FROM edges"):
    if row["target_node"].startswith("ATOMIC:sha:") and row["source_node"].endswith(("X" if False else "")) or True:
        atom = row["target_node"]
        exact_members.setdefault(atom, set()).add(row["source_node"])
exact_pairs = []
for atom, members in exact_members.items():
    ms = sorted(members)
    if 2 <= len(ms) <= 400:
        exact_pairs.extend(itertools.combinations(ms, 2))
    elif len(ms) > 400:
        exact_pairs.extend(itertools.combinations(ms[:40], 2))
marker_members = {}
for row in src.execute("SELECT source_node,target_node,proof,edge_type FROM edges"):
    if row["edge_type"] != "references_marker":
        continue
    atom = row["target_node"]
    marker_members.setdefault(atom, set()).add(row["source_node"])
marker_pairs = []
for atom, members in marker_members.items():
    ms = sorted(members)
    if 2 <= len(ms) <= 30:
        marker_pairs.extend(itertools.combinations(ms, 2))

parent_pairs = []
for row in src.execute("SELECT source_node,target_node FROM edges WHERE edge_type='parent_of'"):
    source, target = row["source_node"], row["target_node"]
    if source in ids and target in ids:
        parent_pairs.append((source, target))

candidate_pairs = []
if Path(CAND).exists():
    with CAND.open() as f:
        for line in f:
            if not line.strip():
                continue
            n = json.loads(line)
            a, b = n.get("source_id"), n.get("target_id")
            if a not in ids or b not in ids:
                continue
            # strict near-copy only
            if int(n.get("levenshtein_distance", 999)) <= 2:
                candidate_pairs.append((a, b))

# write DB
import os
os.remove(DB_PATH) if Path(DB_PATH).exists() else None
dst = sqlite3.connect(DB_PATH)
dst.execute("CREATE TABLE nodes(id TEXT PRIMARY KEY)")
dst.execute("CREATE TABLE edges(source_node TEXT,target_node TEXT,edge_type TEXT,confidence REAL,proof TEXT)")
dst.execute("CREATE INDEX i1 ON edges(source_node,target_node,edge_type)")
dst.executemany("INSERT INTO nodes(id) VALUES (?)", [(v,) for v in ids])
edge_rows = []
seen = set()
def add(a, b, et, proof):
    global edge_rows, seen
    if a == b: return
    k = (a, b, et)
    if k in seen: return
    seen.add(k)
    edge_rows.append((a, b, et, 1.0 if et == "exact_piece" else 0.7, proof))
for p in parent_pairs:
    add(p[0], p[1], "parent_lifecycle", "preserved parent_of")
for p in exact_pairs:
    add(p[0], p[1], "exact_piece", "direct same raw body")
for p in marker_pairs:
    add(p[0], p[1], "shares_marker", "direct shared rare marker atom")
for p in candidate_pairs:
    add(p[0], p[1], "near_piece", "C++ candidate distance <=2")

dst.executemany("INSERT INTO edges(source_node,target_node,edge_type,confidence,proof) VALUES (?,?,?,?,?)", edge_rows)
dst.commit()
print("nodes", len(ids))
print("edges", len(edge_rows), "types", sorted(set(e[2] for e in edge_rows)))
print("exact_piece", sum(1 for e in edge_rows if e[2] == "exact_piece"))
print("near_piece", sum(1 for e in edge_rows if e[2] == "near_piece"))
print("shares_marker", sum(1 for e in edge_rows if e[2] == "shares_marker"))
print("parent_lifecycle", sum(1 for e in edge_rows if e[2] == "parent_lifecycle"))
dst.close()
PY