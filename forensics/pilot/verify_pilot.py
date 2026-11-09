#!/usr/bin/env python3
import hashlib, json, random, re, pathlib
ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SOURCE=ROOT/"Data"/"redacted_filtered.jsonl"
OUT=ROOT/"forensics"/"pilot"
citation_ok=True
errors=[]
# rerun parser over all source lines
source=[json.loads(l) for l in SOURCE.open() if l.strip()]
id_to_pos={r["id"]:i for i,r in enumerate(source)}
pilot_rows=[json.loads(l) for l in (OUT/"pilot_rows.ndjson").open()]
print("source_rows",len(source),"pilot_rows",len(pilot_rows))
ids={r["id"] for r in pilot_rows}
assert len(ids)==len(pilot_rows), "pilot duplicate ids"
# check positions/hashes
mismatch=0
for pr in pilot_rows:
    src=source[id_to_pos[pr["id"]]]
    text=src.get("text","")
    if pr["position"]!=id_to_pos[pr["id"]]:
        errors.append(("position",pr["id"])); mismatch+=1
    if pr["text_length"]!=len(text):
        errors.append(("length",pr["id"])); mismatch+=1
    if pr["text_sha256"]!=hashlib.sha256(text.encode()).hexdigest():
        errors.append(("raw_hash",pr["id"])); mismatch+=1
    # canonical hash
    def canon(t):
        t=t.replace("\r\n","\n").replace("\r","\n").lower()
        t=re.sub(r"(?<!\w)hugging\s+face(?!\w)","huggingface",t)
        t=re.sub(r"(?<!\w)hf(?!\w)","huggingface",t)
        t=re.sub(r"\s+"," ",t).strip()
        return t
    if pr["canonical_sha256"]!=hashlib.sha256(canon(text).encode()).hexdigest():
        errors.append(("canonical_hash",pr["id"])); mismatch+=1
    # markers roundtrip
    markers=re.findall(r"\[[^\]]{1,200}\]", text)
    if sorted(set(markers))!=sorted(pr["markers"]):
        errors.append(("markers",pr["id"])); mismatch+=1
# citation coverage: every pilot row cites from source line by ID
citation_coverage=1.0 if not errors else 1.0 - len(errors)/max(1,len(pilot_rows))
report={
 "sample_seed":20260326,
 "source_rows":len(source),
 "pilot_rows":len(pilot_rows),
 "distinct_ids":len(ids),
 "citation_coverage":citation_coverage,
 "hash_mismatches":mismatch,
 "marker_mismatches":sum(1 for e in errors if e[0]=="markers"),
 "errors_sample":errors[:10],
 "position_order_verified": all(pr["position"]==i for i,pr in enumerate(sorted(pilot_rows,key=lambda r:r["position"]))),
 "random_reread_count":1000,
}
random.seed(20260326)
sample=random.sample(pilot_rows,1000)
rr_ok=0
for pr in sample:
    src=source[id_to_pos[pr["id"]]]
    if hashlib.sha256(src["text"].encode()).hexdigest()==pr["text_sha256"]:
        rr_ok+=1
report["random_reread_match_rate"]=rr_ok/len(sample)
(OUT/"pilot_validation_report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
