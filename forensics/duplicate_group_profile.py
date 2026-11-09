import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
DATA = Path("Data/redacted.jsonl")
rows = []
with DATA.open() as f:
    for line in f:
        if line.strip():
            rows.append(json.loads(line))
groups = defaultdict(list)
for r in rows:
    h = hashlib.sha256(r["text"].encode()).hexdigest()
    groups[h].append(r)
groups = {h: v for h, v in groups.items() if len(v) >= 2}
print("rows", len(rows))
print("groups", len(groups))
print("rows in groups", sum(len(v) for v in groups.values()))
print("group size distribution:", Counter(len(v) for v in groups.values()))
# group kinds inside
kinds = Counter()
mix = Counter()
for h, vs in groups.items():
    mix[tuple(sorted(set(v["kind"] for v in vs)))] += 1
print("group kind-combinations count", mix)
# id span
spans = []
for h, vs in groups.items():
    ids = sorted(int(v["id"][1:]) for v in vs)
    spans.append(ids[-1]-ids[0])
print("avg span", sum(spans)/len(spans), "max", max(spans), "median-ish", sorted(spans)[len(spans)//2])
# large hashes
big = [(h, len(v), v) for h, v in groups.items() if len(v) >= 50]
big.sort(key=lambda x: -x[1])
print("groups >= 50:", len(big))
for h,n,vs in big[:8]:
    ids = [v["id"] for v in vs]
    print("  count",n,"first",ids[0],"last",ids[-1],"example parent",vs[0].get("parent_id"))
PY