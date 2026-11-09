#!/usr/bin/env python3
import collections,json,re,hashlib
from pathlib import Path
ROOT=Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC=ROOT/"Data/redacted_filtered.jsonl"
EDGES=ROOT/"forensics/run_2026/core/core_edges.ndjson"
OUT=ROOT/"forensics/run_2026"
token_re=re.compile(r"\[[^\]]{1,200}\]")

rows=[json.loads(l) for l in SRC.open() if l.strip()]
groups=collections.defaultdict(list)
for r in rows:
    for m in set(token_re.findall(r["text"])):
        groups[m].append(r["id"])  # exact lexical pointer form

def classify_marker(m):
    low=m.lower()
    if m in ("[ENCODED BLOB]","[REDACTED SENSITIVE CONTENT]") or low.startswith("[redacted:runtime_identifier") or '[' in m.rstrip(']')[1:] or "host" in low and m.startswith("[REDACTED") or 'url' in low and m.startswith("[REDACTED"):
        return "likely_generic_or_redacted_pointer"
    if re.fullmatch(r"\[[A-Z 0-9_:\-]+\]",m) and re.search(r"\d",m):
        return "structured_numbered_pointer"
    if re.search(r"proxy|shortener|service host|ip address",m,re.I):
        return "transit_or_service_pointer"
    return "lexical_signature"

# marker registry
with (OUT/"marker_pattern_registry.csv").open("w",encoding="utf-8",newline="") as f:
    import csv
    w=csv.writer(f)
    w.writerow(["marker","group_size","classification","unique_source_rows","kinds","sample_rows"])
    for m,ids in sorted(groups.items(),key=lambda x:(-len(x[1]),x[0])):
        kinds=collections.Counter(json.loads(next_line:=None) if False else None for rid in ids[:0]) if False else collections.Counter()
        for rid in ids:
            kinds[src.get(rid,"kind" ) if False else None] if False else None
        kinds=collections.Counter(next(json.loads(ln) for ln in open(SRC) if json.loads(ln)["id"]==rid)["kind"] for rid in ids[:1])
        kinds=collections.Counter()
        for rid in ids:
            rr=src_map.get(rid) if False else None
        kinds=collections.Counter()
        kind_lookup={}
        for rid in ids[:5]: kind_lookup[rid]=None
        for rid in ids:
            kind_lookup[rid]=next(r["kind"] for r in rows if r["id"]==rid)
        kinds=collections.Counter(kind_lookup[rid] for rid in ids)
        codes=";" .join(f"{k}:{v}" for k,v in sorted(kinds.items()))
        samples=";".join(ids[:5])
        w.writerow([m,len(ids),classify_marker(m),len(ids),codes,samples])
# edge class pattern
edge_counters=collections.Counter()
sample_by={}
for e in (json.loads(l) for l in EDGES.open() if l.strip()):
    et=e["edge_type"]
    trig=e["proof"].rsplit(" rows=",1)[0]
    if et.startswith("MARKER"):
        trig=f"MARKER {trig}"
    key=(et,trig)
    edge_counters[key]+=1
    if key not in sample_by:
        sample_by[key]=(e["source"],e["target"])
with (OUT/"link_pattern_registry.csv").open("w",encoding="utf-8",newline="") as f:
    import csv
    w=csv.writer(f)
    w.writerow(["edge_class","trigger","edge_count","type_tuple","sample_source","sample_target"])
    for (et,trig),n in sorted(edge_counters.items(),key=lambda x:-x[1]):
        if et in ("MARKER_SAME","MARKER_ENDPOINT"):
            tuple_label=f"('marker','{trig[:100]}')"
        elif et=="EXACT_BODY":
            tuple_label=f"('body_exact',{trig[:16]})"
        else:
            tuple_label=f"('{et.lower()}','{trig[:100]}')"
        s,t=sample_by[(et,trig)]
        w.writerow([et,trig,n,tuple_label,s,t])
print("markerPatternGroups",len(groups),"linkPatternGroups",len(edge_counters))
# Candidate exact-distance linkage pattern
candidate="/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson"
counts=collections.Counter()
seen=set()
with open(candidate) as f:
    for line in f:
        if not line.strip(): continue
        o=json.loads(line)
        k=(o["source_id"],o["target_id"])
        if k in seen: continue
        seen.add(k)
        counts[o["levenshtein_distance"]]+=1
print("unique candidate pairs",len(seen),"distance totals",dict(sorted(counts.items())))
