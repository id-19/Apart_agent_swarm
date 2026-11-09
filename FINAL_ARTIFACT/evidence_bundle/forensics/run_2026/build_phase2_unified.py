#!/usr/bin/env python3
import collections, hashlib, json, pathlib
ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
PROJ=ROOT/"forensics"/"projections"
OUT=ROOT/"forensics"
# Rows index
src_rows=[json.loads(l) for l in (ROOT/"Data"/"redacted_filtered.jsonl").open() if l.strip()]
row_index={}
for position,row in enumerate(src_rows):
    text=row.get("text","")
    def canon(t):
        import re
        t=t.replace("\r\n","\n").replace("\r","\n").lower()
        t=re.sub(r"(?<!\w)hugging\s+face(?!\w)","huggingface",t)
        t=re.sub(r"(?<!\w)hf(?!\w)","huggingface",t)
        t=re.sub(r"\s+"," ",t).strip()
        return t
    import hashlib
    row_index[row["id"]]={
      "id":row["id"],
      "position":position,
      "mechanical_kind":row.get("kind"),
      "parent_id":row.get("parent_id"),
      "text_length":len(text),
      "text_sha256":hashlib.sha256(text.encode()).hexdigest(),
      "canonical_sha256":hashlib.sha256(canon(text).encode()).hexdigest(),
      "markers":sorted(set(__import__("re").findall(r"\[[^\]]{1,200}\]",text))),
      "cite":row.get("cite"),
      "time_utc_field":row.get("time_utc"),
      "tags":row.get("tags"),
    }
with (OUT/"graph_rows_index.json").open("w") as f:
    json.dump(row_index,f,separators=(",",":"),ensure_ascii=False)
print("wrote graph_rows_index.json",len(row_index))

# Unified edges
edge_classes=sorted(p.name.replace(".ndjson","") for p in PROJ.glob("*.ndjson"))
with (OUT/"graph_edges_v2.jsonl").open("w") as out:
    counts=collections.Counter()
    for clsfile in sorted(PROJ.glob("*.ndjson")):
        if clsfile.name.startswith("near_body_") or "NEAR_BODY" in clsfile.name.upper():
            print("skipping candidate projection", clsfile.name)
            continue
        with clsfile.open() as f:
            for line in f:
                if line.strip():
                    out.write(line)
                    counts[clsfile.stem]+=1
total=sum(counts.values())
print("edge counts",dict(sorted(counts.items())),"total",total)

# stats
endpoints=set()
for clsfile in PROJ.glob("*.ndjson"):
    with clsfile.open() as f:
        for line in f:
            if line.strip():
                o=json.loads(line); endpoints.add(o["source_id"]); endpoints.add(o["destination_id"])
stats={
 "rows":len(row_index),
 "edge_classes":dict(sorted(counts.items())),
 "total_edges":total,
 "distinct_endpoints":len(endpoints),
 "edge_class_files":sorted(str(p) for p in PROJ.glob("*.ndjson")),
}
(OUT/"graph_class_stats.json").write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
