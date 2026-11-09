#!/usr/bin/env python3
"""Read-only audit of the C++ near candidate engine. No relation cap."""
import collections
import hashlib
import json
import random
from pathlib import Path

ROOT = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC = {json.loads(l)["id"]: json.loads(l) for l in (ROOT/"Data/redacted_filtered.jsonl").open() if l.strip()}
CAND = Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")
RNG = random.Random(20260326)

def canonical_normalize(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.lower()
    import re as _re
    text = _re.sub(r"(?<!\w)hugging\s+face(?!\w)", "huggingface", text)
    text = _re.sub(r"(?<!\w)hf(?!\w)", "huggingface", text)
    text = _re.sub(r"\s+", " ", text).strip()
    return text


reservoirs = {0: [], 1: [], 2: [], 3: []}
seen = {0: 0, 1: 0, 2: 0, 3: 0}
rows = 0
counts = {}
for line in CAND.open(encoding="utf-8"):
    if not line.strip():
        continue
    o = json.loads(line)
    rows += 1
    d = o["levenshtein_distance"]
    counts[d] = counts.get(d, 0) + 1
    if d in reservoirs:
        seen[d] += 1
        if len(reservoirs[d]) < 100:
            reservoirs[d].append(o)
        else:
            i = RNG.randrange(0, seen[d])
            if i < 100:
                reservoirs[d][i] = o

mismatches = {}
examples = []
def lev(a,b):
    if a==b: return 0
    la,lb=len(a),len(b)
    if la==0:return lb
    if lb==0:return la
    prev=list(range(lb+1)); cur=[0]*(lb+1)
    for ch in a:
        cur[0]+=1
        for j in range(1,lb+1):
            cur[j]=min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ch!=b[j-1]))
        prev,cur=cur,prev
    return prev[lb]

for d in (0,1,2,3):
    bad = 0
    for o in reservoirs[d]:
        actual = 0 if canonical_normalize(SRC[o["source_id"]]["text"]) == canonical_normalize(SRC[o["target_id"]]["text"]) else lev(canonical_normalize(SRC[o["source_id"]]["text"]), canonical_normalize(SRC[o["target_id"]]["text"]))
        if actual != d:
            bad += 1
            if len(examples) < 12:
                examples.append({"candidate_d": d, "actual": actual, "source": o["source_id"], "target": o["target_id"],
                                "lengths": [o["source_length"], o["target_length"]]})
    mismatches[d] = bad
    print(f"d={d}: verified={len(reservoirs[d])}, mismatches={bad}", flush=True)

out = {
    "candidate_lines": rows,
    "distance_counts": dict(sorted(counts.items())),
    "verified_samples_per_distance": {str(d): {"count": len(reservoirs[d]), "mismatches": mismatches[d]} for d in (0,1,2,3)},
    "mismatch_examples": examples[:12],
    "duplicate_pair_keys_expected": 0,
    "verification_rule": "Independent full Levenshtein on canonical-text (same normalization as core graph), staged on a deterministic reservoir sample.",
}
Path(ROOT / "forensics/run_2026/near_distance_candidate_audit.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print(json.dumps({k: out[k] for k in ("candidate_lines", "distance_counts", "verified_samples_per_distance")}, indent=2))
print("wrote audit")
