#!/usr/bin/env python3
import json, re, collections, pathlib
ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC = ROOT / "Data" / "redacted_filtered.jsonl"
ROWS = ROOT / "forensics/run_2026/core/core_rows.ndjson"
OUT = ROOT / "forensics/run_2026/parent_mutation_profile.json"
source = {json.loads(l)["id"]: json.loads(l) for l in SRC.open() if l.strip()}
rows = {json.loads(l)["id"]: json.loads(l) for l in ROWS.open() if l.strip()}
MARKER = re.compile(r"\[[^\]]{1,200}\]")

def norm(text):
    text = text.replace("hugging face", "huggingface").replace("hf", "huggingface")
    return " ".join(text.lower().split())

def marker_set(text):
    return set(MARKER.findall(text))

def bounded_edit(parent, child, limit=200):
    if parent == child:
        return 0
    if not child or abs(len(parent)-len(child)) > limit:  # compare no pair of wildly different sizes
        return None
    m, n = len(parent), len(child)
    row = list(range(n + 1))
    for i in range(1, m + 1):
        prev = row
        row = [i] + [0] * n
        pc = parent[i - 1]
        for j in range(1, n + 1):
            cost = 0 if pc == child[j - 1] else 1
            row[j] = min(prev[j] + 1, row[j-1] + 1, prev[j-1] + cost)
    return row[n]

def classify(parent_text, child_text):
    if parent_text == child_text:
        return "exact_body_as_parent"
    if norm(parent_text) == norm(child_text):
        return "approved_normalization_replay"
    if parent_text in child_text or child_text in parent_text:
        return "body_contains_other"
    if len(parent_text) > 512 or len(child_text) > 512:
        d = None
    else:
        d = bounded_edit(parent_text, child_text, 64)
    if d is not None and d <= 3:
        return f"bounded_near_body_edit_d{d}"
    marker_delta = len(marker_set(child_text) - marker_set(parent_text)) + len(marker_set(parent_text) - marker_set(child_text))
    if marker_delta > 0:
        return "marker_inventory_change"
    if len(parent_text) != len(child_text) and abs(len(parent_text)-len(child_text)) <= 5:
        return "small_length_mutation"
    return "larger_body_mutation"

stats = {}
samples = {}
for rid, child in rows.items():
    parent_id = child["parent_id"]
    if not parent_id or parent_id not in source:
        continue
    pt = source[parent_id]["text"]
    ct = source[rid]["text"]
    cat = classify(pt, ct)
    stats[cat] = stats.get(cat, 0) + 1
    if len(samples.get(cat, [])) < 6:
        samples.setdefault(cat, []).append((rid, parent_id, len(ct) - len(pt), len(marker_set(ct) ^ marker_set(pt))))

out = {
    "pairs_compared": sum(stats.values()),
    "distinct_parents_with_available_child_rows": len({r["parent_id"] for r in rows.values() if r["parent_id"] in source}),
    "parents_present_inside_filtered_rows": len({r["id"] for r in source.values() if r["id"].startswith("R")}),
    "mutation_counts": dict(sorted(stats.items())),
    "sample_pairs_by_class": {k: v for k, v in sorted(samples.items())},
}
OUT.write_text(__import__("json").dumps(out, indent=2, ensure_ascii=False))
print(json.dumps(out, indent=2))
