#!/usr/bin/env python3
import json, random
from pathlib import Path
ROOT=Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC={json.loads(l)["id"]:json.loads(l) for l in (ROOT/"Data/redacted_filtered.jsonl").open() if l.strip()}
CAND=Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")
rng=random.Random(20260326)
reservoirs={0:[],1:[],2:[],3:[]}
seen={0:0,1:0,2:0,3:0}
counts={}
keys=set(); duplicate=0; total=0
with CAND.open(encoding="utf-8") as f:
    for line in f:
        if not line.strip(): continue
        o=json.loads(line); total+=1
        d=o["levenshtein_distance"]
        counts[d]=counts.get(d,0)+1
        key=(o["source_id"],o["target_id"])
        if key in keys: duplicate+=1
        else: keys.add(key)
        if d in reservoirs:
            seen[d]+=1
            if len(reservoirs[d])<1000:
                reservoirs[d].append(o)
            else:
                i=rng.randrange(0,seen[d])
                if i<1000:
                    reservoirs[d][i]=o
def standard_distance(a,b):
    if a==b: return 0
    m,n=len(a),len(b)
    if abs(m-n)>5: return abs(m-n) # enough to falsify d<=3; no need full billion-cost giant long
    prev=list(range(n+1))
    for ch in a:
        cur=[len(prev)]+ [0]*n
        cur[0]=prev[0]+1
        for j,ch2 in enumerate(b,1):
            cost = 0 if ch==ch2 else 1
            cur[j]=min(prev[j]+1,cur[j-1]+1,prev[j-1]+cost)
        prev=cur
    return prev[n]
mismatches={}
examples=[]
for d in (1,2,3):
    bad=0
    for o in reservoirs[d]:
        actual=standard_distance(SRC[o["source_id"]]["text"],SRC[o["target_id"]]["text"])
        if actual != d:
            bad+=1
            if len(examples)<12:
                examples.append({"candidate_d":d,"actual":actual,"source":o["source_id"],"target":o["target_id"],"lengths":[o["source_length"],o["target_length"]]})
    mismatches[d]=bad
    print(f"d={d}: verified {len(reservoirs[d])}, mismatches {bad}",flush=True)
# confirm zero sample for d0
bad0=sum(SRC[o["source_id"]]["text"]!=SRC[o["target_id"]]["text"] for o in reservoirs[0][:1000])
mismatches[0]=bad0
print("d=0: verified=1000, mismatches",bad0,flush=True)
out={"candidate_lines":total,"unique_pair_keys":len(keys),"duplicate_keys":duplicate,"distance_counts":dict(sorted(counts.items(),key=lambda kv:int(kv[0]))),
"verified_samples":{str(d):{"count":len(reservoirs[d]),"mismatches":mism[d]} for d in reservoirs},
"verification_method":"Python exact Levenshtein for sampled candidates; d0 byte-equality","initial_reserved_mismatch_examples":examples}
(ROOT/"forensics/run_2026/near_distance_candidate_audit.json").write_text(__import__("json").dumps(out,indent=2),encoding="utf-8")
print(json.dumps({k:out[k] for k in ("candidate_lines","unique_pair_keys","duplicate_keys","distance_counts","verified_samples")},indent=2))
print("wrote audit")
