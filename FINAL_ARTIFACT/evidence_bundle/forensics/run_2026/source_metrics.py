import json,re,collections,time
rows=[json.loads(l) for l in open("Data/redacted_filtered.jsonl") if l.strip()]
ids=sorted(r["id"] for r in rows)
parent={r["id"]:r.get("parent_id") for r in rows}
present_ids=set(ids)
marker_groups=collections.defaultdict(list)
token_re=re.compile(r"\[[^\]]{1,200}\]")
for r in rows:
    for m in set(token_re.findall(r["text"])): marker_groups[m].append(r["id"])
counts={
 "rows":len(rows),
 "distinct_ids":len(ids),
 "parent_refs":sum(bool(r.get("parent_id")) for r in rows),
 "parents_resolves_to_row":sum(1 for r in rows if r.get("parent_id") in present_ids),
 "distinct_parents":len({r.get("parent_id") for r in rows if r.get("parent_id")}),
 "timestamp_iso_datetime":sum(1 for r in rows if re.search(r"\b20[0-9]{2}-[0-9]{2}-[0-9]{2}[ T]\d{2}:\d{2}:\d{2}", r["text"])),
 "timestamp_iso_date":sum(1 for r in rows if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", r["text"])),
 "timestamp_docker":sum(1 for r in rows if re.search(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[ 0-9]{1,2}\s+\d{2}:\d{2}:\d{2}\b", r["text"])),
 "rows_with_markers":sum(1 for r in rows if token_re.search(r["text"])),
 "distinct_marker_groups":len(marker_groups),
 "repeat_groups":sum(len(v)>1 for v in marker_groups.values()),
 "repeat_groups_gt100":sum(len(v)>100 for v in marker_groups.values()),
}
print(json.dumps(counts,indent=2))
# external time anchors from already parsed subset
import json as J
ts=J.load(open("/Users/id19/scratchpad/temporal_subset/subset_summary.json"))
print("temporal subset summary", json.dumps({k:ts.get(k) for k in ("timestamped_rows","nodes","edges")},indent=2))
with open("forensics/run_2026/source_metrics.json","w") as f:
    json.dump(counts,f,indent=2)
