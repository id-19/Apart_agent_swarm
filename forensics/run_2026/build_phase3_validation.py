#!/usr/bin/env python3
import json, random, collections, pathlib, re, hashlib
ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
PROJ=ROOT/"forensics/projections"
RI=json.load((ROOT/"forensics/graph_rows_index.json").open())
SRC={json.loads(l)["id"]:json.loads(l) for l in (ROOT/"Data/redacted_filtered.jsonl").open()}
TIMED={json.loads(l)["id"]:json.loads(l) for l in open("/Users/id19/scratchpad/temporal_subset/temporal_timestamps.jsonl")}
random.seed(20261109)
SAMPLES_PER=1000

def canon(t):
    t=t.replace("\r\n","\n").replace("\r","\n").lower()
    t=re.sub(r"(?<!\w)hugging\s+face(?!\w)","huggingface",t)
    t=re.sub(r"(?<!\w)hf(?!\w)","huggingface",t)
    t=re.sub(r"\s+"," ",t).strip()
    return t

def normalize_semantics(s):
    collapsed=" ".join(s.lower().split())
    s2=re.sub(r"(?<![a-z0-9_-])hugging face(?![a-z0-9_-])","huggingface",collapsed)
    s2=re.sub(r"(?<![a-z0-9_-])hf(?![a-z0-9_-])","huggingface",s2)
    return s2

def lev(a,b):
    if a==b: return 0
    m,n=len(a),len(b)
    if abs(m-n)>3: return 4
    dp=list(range(n+1))
    for i,ch in enumerate(a,1):
        prev=dp[0]; dp[0]=i
        for j in range(1,n+1):
            cur=dp[j]
            cost=0 if ch==b[j-1] else 1
            dp[j]=min(dp[j]+1,dp[j-1]+1,prev+cost)
            prev=cur
        if min(dp)>3: return 4
    return dp[n]

def reservoir_sample(path,k):
    sample=[]; n=0
    with path.open() as f:
        for line in f:
            if not line.strip(): continue
            o=json.loads(line); n+=1
            if len(sample)<k:
                sample.append(o)
            else:
                r=random.randrange(n)
                if r<k:
                    sample[r]=o
    return n,sample

disputes=[]
accept=collections.defaultdict(lambda: collections.Counter())
for clsfile in sorted(PROJ.glob("*.ndjson")):
    n,sampled=reservoir_sample(clsfile,SAMPLES_PER)
    if n==0:
        cname=clsfile.stem
        accept[cname]["population"]=0
        accept[cname]["sampled"]=0
        continue
    cname=sampled[0]["edge_class"]
    name_class=cname
    # sample cap 10% but max 1000
    k=len(sampled)
    if k>n//10 and n//10>0:
        # resample smaller by reservoir of n//10
        k2=max(1,n//10)
        k2=min(k2,SAMPLES_PER)
        # quick truncate with reservoir already approximate; regenerate exact smaller
        _,sampled=reservoir_sample(clsfile,k2)
        k=k2
    ok=0
    for e in sampled:
        s=e["source_id"]; d=e["destination_id"]
        verdict="accepted"; reason=""
        if s not in RI or d not in RI:
            verdict="rejected"; reason="endpoint not in row index"
        else:
            ec=e["edge_class"]
            if ec=="EXACT_BODY":
                if SRC[s]["text"]!=SRC[d]["text"]: verdict="rejected"; reason="raw bodies not byte-identical"
            elif ec=="NORMALIZED_REPLAY":
                if canon(SRC[s]["text"])!=canon(SRC[d]["text"]) or SRC[s]["text"]==SRC[d]["text"]: verdict="rejected"; reason="canonical mismatch/raw identical"
            elif ec.startswith("NEAR_BODY_D"):
                dd=int(ec.split("_D")[1])
                dist=lev(normalize_semantics(SRC[s]["text"]),normalize_semantics(SRC[d]["text"]))
                if dist>dd or dist==0: verdict="rejected"; reason=f"levenshtein={dist} not class D{dd}"
            elif ec=="PARENT_DIRECT":
                if SRC[d].get("parent_id")!=s: verdict="rejected"; reason="parent_id mismatch"
            elif ec=="SAME_PARENT_SIBLING":
                if SRC[s].get("parent_id") is None or SRC[s].get("parent_id")!=SRC[d].get("parent_id"): verdict="rejected"; reason="parents differ"
            elif ec in ("MARKER_SAME","MARKER_ENDPOINT"):
                marker=e["trigger"]
                if marker not in SRC[s]["text"] or marker not in SRC[d]["text"]: verdict="rejected"; reason="marker absent"
            elif ec=="PARENT_MUTATION":
                if SRC[d].get("parent_id")!=s or SRC[s]["text"]==SRC[d]["text"]: verdict="rejected"; reason="not mutation parent-child"
            elif ec=="TIMESTAMP_ANCHOR":
                if s not in TIMED and d not in TIMED: verdict="rejected"; reason="neither endpoint timed"
            elif ec=="INTENT_SIGNATURE":
                if len(e["trigger"])<5: verdict="rejected"; reason="empty signature"
        if verdict=="accepted":
            ok+=1
        else:
            disputes.append({"edge":e,"verdict":verdict,"reason":reason})
    accept[name_class]["population"]=n
    accept[name_class]["sampled"]=k
    accept[name_class]["accepted"]=ok
    accept[name_class]["acceptance_rate"]= ok/k if k else None
    print(name_class, "pop",n,"sampled",k,"accepted",ok)

acc={k:dict(v) for k,v in accept.items()}
(ROOT/"forensics/edge_class_acceptance.json").write_text(json.dumps(acc,indent=2))
with (ROOT/"forensics/disputed_edges.jsonl").open("w") as f:
    for dd in disputes:
        f.write(json.dumps(dd,separators=(",",":"),ensure_ascii=False)+"\n")
lines=["# Edge validation report\n"]
for cname,a in sorted(acc.items()):
    lines.append(f"## {cname}\n")
    lines.append(f"- population: {a.get('population')}\n")
    lines.append(f"- sampled: {a.get('sampled')}\n")
    lines.append(f"- accepted: {a.get('accepted',0)}\n")
    lines.append(f"- acceptance_rate: {a.get('acceptance_rate')}\n")
    lines.append(f"- disputes: {sum(1 for d in disputes if d['edge']['edge_class']==cname)}\n")
lines.append(f"\nTotal disputes: {len(disputes)}\n")
(ROOT/"forensics/edge_validation_report.md").write_text("".join(lines))
print("disputes",len(disputes),"classes",len(acc))
