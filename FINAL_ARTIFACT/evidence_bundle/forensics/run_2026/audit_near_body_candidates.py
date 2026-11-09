#!/usr/bin/env python3
"""Read-only audit of the C++ near-body candidate file. No arbitrary caps."""
import json, random
from pathlib import Path

ROOT = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC = {json.loads(l)["id"]: json.loads(l) for l in (ROOT/"Data/redacted_filtered.jsonl").open() if l.strip()}
CAND = Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")
rng = random.Random(20260326)

def banded_distance(a,b,k=3):
    if a==b: return 0
    la,lb=len(a),len(b)
    if abs(la-lb)>k: return abs(la-lb)
    prev_lo,prev_hi=0,min(lb,k)
    prev={j:j for j in range(prev_lo,prev_hi+1)}
    for ai in range(1,la+1):
        lo=max(0,ai-k); hi=min(lb,ai+k)
        cur={}
        for j in range(lo,hi+1):
            if j==0:
                cur[0]=ai; continue
            best=10**9
            if j in prev: best=min(best,prev[j]+1)
            if j-1 in cur: best=min(best,cur[j-1]+1)
            if j-1 in prev: best=min(best,prev[j-1]+(0 if a[ai-1]==b[j-1] else 1))
            cur[j]=best
        prev,prev_lo,prev_hi=cur,lo,hi
    return prev[lb] if lb in prev else k+1

reservoirs={1:[],2:[],3:[]}; seen={1:0,2:0,3:0}; rows=0; keys=set(); duplicate=0; counts={}
with CAND.open(encoding="utf-8") as f:
    for line in f:
        if not line.strip(): continue
        o=json.loads(line); rows+=1; d=o["levenshtein_distance"]
        counts[d]=counts.get(d,0)+1
        key=(o["source_id"],o["target_id"])
        if key in keys: duplicate+=1
        else: keys.add(key)
        if d in reservoirs:
            seen[d]+=1
            cap=500
            if len(reservoirs[d])<cap:
                reservoirs[d].append(o)
            else:
                n=rng.randrange(0,seen[d])
                if n<cap: reservoirs[d][n]=o

mism={}; examples=[]
for d in (1,2,3):
    bad=0
    for o in reservoirs[d]:
        actual=0 if SRC[o["source_id"]]["text"]==SRC[o["target_id"]]["text"] else banded_distance(SRC[o["source_id"]]["text"],SRC[o["target_id"]]["text"],3)
        if actual!=d:
            bad+=1
            if len(examples)<12: examples.append({"candidate_d":d,"actual":actual,"source":o["source_id"],"target":o["target_id"],"lengths":[o["source_length"],o["target_length"]]})
    mism[d]=bad
    print(f"d={d}: verified={len(reservoirs[d])}, mismatches={bad}",flush=True)

out={
  "candidate_lines":rows,
  "unique_pair_keys":len(keys),
  "duplicate_keys":duplicate,
  "distance_counts":dict(sorted(counts.items(),key=lambda kv:int(kv[0]))),
  "verification_samples":{str(d):{"count":len(reservoirs[d]),"mismatches":mism[d]} for d in (1,2,3)},
  "mismatch_examples":examples,
  "verification_rule":"For each candidate pair, independent banded Levenshtein distance <=3 was computed because candidate distances are in {1,2,3}; D0 exact candidates are represented as exact_body.",
  "candidate_generator":"forensics/build_near_body_candidates.cpp compiled -O3 -std=c++17; maxd set by constants K/MAXD=3",
}
Path("/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/near_body_candidate_audit.json").write_text(__import__("json").dumps(out,indent=2))
print(json.dumps({k:out[k] for k in ("candidate_lines","unique_pair_keys","duplicate_keys","distance_counts","verification_samples")},indent=2))
print("wrote audit")
