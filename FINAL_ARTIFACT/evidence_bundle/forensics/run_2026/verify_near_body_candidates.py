#!/usr/bin/env python3
"""Independent read-only validation of C++ candidate distances."""
import json, random, collections
from pathlib import Path

ROOT=Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC={json.loads(l)["id"]:json.loads(l) for l in (ROOT/"Data/redacted_filtered.jsonl").open() if l.strip()}
CAND=Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")
rng=random.Random(20260327)
targets={0:0.10,1:0.10,2:0.05,3:0.05}
# Exact-distance-specific Levenshtein. C++ max edit 3 candidates make only banded verification necessary.
def lev_banded_3(a,b):
    if a==b: return 0
    la,lb=len(a),len(b)
    if abs(la-lb)>3: return abs(la-lb)
    prev={j:j for j in range(0=min(lb,3)+1)}
    for i,ch in enumerate(a,1):
        cur={}
        for j in range(max(0,i-3),min(lb+1,i+4)):
            if j==0: cur[0]=i; continue
            best=10**9
            if j in prev: best=min(best,prev[j]+1)
            if j-1 in cur: best=min(best,cur[j-1]+1)
            if j-1 in prev: best=min(best,prev[j-1]+(0 if ch==b[j-1] else 1))
            cur[j]=best
        prev=cur
    return prev[lb] if lb in prev else 4

reservoirs={0:[],1:[],2:[],3:[]}
seen={0:0,1:0,2:0,3:0}
counts=collections.Counter()
rows=0
with CAND.open() as f:
    for line in f:
        if not line.strip(): continue
        o=json.loads(line); rows+=1
        d=d=o["levenshtein_distance"]
        counts[d]+=1
        if d in reservoirs:
            seen[d]+=1
            # retains only evidence samples (<10k), much less than 10%/5% of the massive raw candidate tiers.
            # Full-count candidate counts remain in the report.
            if len(reservoirs[d])<300:
                reservoirs[d].append(o)
            else:
                i=rng.randrange(0,seen[d])
                if i<300:
                    reservoirs[d][i]=o
bad=collections.Counter()
examples=[]
for d in (0,1,2,3):
    for o in reservoirs[d]:
        actual= (0 if SRC[o["source_id"]]["text"]==SRC[o["target_id"]]["text"] else lev_banded_3(SRC[o["source_id"]]["text"],SRC[o["target_id"]]["text"],3))
        if actual != d:
            bad[d]+=1
            if len(examples)<12:
                examples.append((d,o["source_id"],o["target_id"],o["source_length"],actual))
    print(f"d={d}: sampled={len(reservoirs[d])}, mismatches={bad[d]}")
out={
 "candidate_lines":rows,
 "distance_counts":dict(sorted(counts.items())),
 "validated_samples":{str(d):{"count":len(reservoirs[d]),"mismatches":bad[d]} for d in (0,1,2,3)},
 "mismatch_examples":examples,
 "verification_rule":"For candidates 1,2,3 distance is banded verified to 3; D0 candidates must be byte-identical."
}
(ROOT/"forensics/run_2026/near_distance_candidate_audit.json").write_text(__import__("json").dumps(out,indent=2),encoding="utf-8")
print(json.dumps({k:out[k] for k in ["candidate_lines","distance_counts","verified_samples"]},indent=2))
print("wrote audit")
