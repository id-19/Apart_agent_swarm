from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "Data" / "redacted.jsonl"
OUT = ROOT.parent / "scratchpad" if False else Path("/Users/id19/scratchpad")
OUT.mkdir(exist_ok=True)

rows = []
ids = set()
with DATA.open("r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        o = json.loads(line)
        rows.append(o)
        ids.add(o["id"])

parent_count = sum(1 for r in rows if r.get("parent_id") is not None)
row_count = len(rows)
hashes = collections.Counter(hashlib.sha256(r.get("text", "").encode("utf-8")).hexdigest() for r in rows)
marker_re = re.compile(r"\[[^]]+\]")
marker_counts = collections.Counter()
for r in rows:
    for token in marker_re.findall(r.get("text", "")):
        marker_counts[token] += 1

handle_prefixes = collections.Counter()
for token in marker_counts:
    m = re.match(r"\[REDACTED:([^:]+):", token)
    if m:
        handle_prefixes[m.group(1)] += marker_counts[token]

zz_counter = collections.Counter()
for r in rows:
    for zz in re.findall(r"zz[A-Za-z0-9_]{4,}", r.get("text", "")):
        zz_counter[zz] += 1

rows_by_kind = collections.Counter(r.get("kind") for r in rows)
parents_per_kind = collections.Counter((r.get("kind"), rows_by_kind.get(r.get("parent_id") and None)) for r in rows)
child_cardinality = collections.Counter()
for r in rows:
    if r.get("parent_id") is not None:
        child_cardinality[r["parent_id"]] += 1

exact_duplicate_groups = sum(1 for _, c in hashes.items() if c > 1)
exact_duplicate_rows = sum(c for _, c in hashes.items() if c > 1)

print("rows:", row_count)
print("unique ids:", len(ids))
print("rows with parent_id:", parent_count)
print("rows without parent_id (roots or recovered becoming roots):", row_count - parent_count)
print("table:", list(rows_by_kind.items()))
print("unique hash groups:", len(hashes))
print("groups with >1 exact text:", exact_duplicate_groups, "rows:", exact_duplicate_rows)
print("parents with >= 2 children:", sum(1 for x, c in child_cardinality.items() if c > 1))
print("max children:", max(child_cardinality.values()) if child_cardinality else 0)
print("top zz markers:")
for k, v in zz_counter.most_common(15):
    print(" ", v, k)
print("top redaction handle families:")
for k, v in handle_prefixes.most_common(20):
    print(" ", v, k)
print("distinct raw placeholder tokens:", len(marker_counts))

import json as _j
summary = {
    "row_count": row_count,
    "unique_ids": len(ids),
    "parent_count": parent_count,
    "root_count": row_count - parent_count,
    "kind_counts": dict(rows_by_kind),
    "unique_text_hashes": len(hashes),
    "exact_duplicate_groups": exact_duplicate_groups,
    "exact_duplicate_rows": exact_duplicate_rows,
    "parents_with_multiple_children": sum(1 for x, c in child_cardinality.items() if c > 1),
    "max_children": max(child_cardinality.values()) if child_cardinality else 0,
    "distinct_placeholders": len(marker_counts),
    "handle_prefix_counts": dict(handle_prefixes.most_common()),
    "top_zz_markers": dict(zz_counter.most_common(30)),
}
(OUT / "swarm_graph_basic_stats.json").write_text(_j.dumps(summary, indent=2), encoding="utf-8")
print("wrote", OUT / "swarm_graph_basic_stats.json")
