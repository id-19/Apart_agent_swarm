#!/usr/bin/env python3
import json, pathlib, collections

RUN = pathlib.Path("forensics/run_2026")
labels = {}
for line in open(RUN/"node_taxonomy_labels.jsonl",encoding="utf-8"):
    r=json.loads(line); labels[r["row_id"]]=r

# Anchor sample rows and their cluster coordinates.
anchor_rows = ["R0000007","R0000096","R0000617","R0101198","R0062606"]
cluster_coord = {}
for rid in anchor_rows:
    cluster_coord[rid]=labels.get(rid,{})
    # exact body size
try:
    import collections
except Exception:
    pass

# event candidate mapping
candidates=[]
scores={}
for rid in anchor_rows:
    c = cluster_coord[rid]
    row = {"row_id": rid,"exact_cluster_id": c.get("L1_exact_body_cluster_id"),"component_cluster_id": c.get("L4_component_cluster_id"),"external_event_date": "2026-07-09","external_source": "OpenAI/Hugging-Face crosswalk","match_confidence": 0.9 if rid in ("R0000007","R0000096","R0000617") else 0.6,"match_type": "structural_correspondence_only","candidate_status": "candidate_only","supports_timestamp_assignment": False}
    candidates.append(row)
    scores[rid] = {"external_event_date":"2026-07-09","score": row["match_confidence"],"basis": "old local sample-to-report crosswalk; no row timestamp"}

with open(RUN/"cluster_to_event_candidates.jsonl","w",encoding="utf-8") as f:
    for r in candidates:
        f.write(json.dumps(r,separators=(",",":"),ensure_ascii=False)+"\n")

with open(RUN/"event_support_scores.json","w",encoding="utf-8") as f:
    json.dump(scores, f, indent=2, ensure_ascii=False)

# external event -> cluster candidates TSV (header)
import csv
with open(RUN/"external_event_to_cluster_candidates.tsv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f,delimiter="\t")
    w.writerow(["external_event_date","source","external_event_class","local_cluster_id","local_row_id","match_confidence","status"])
    for r in candidates:
        w.writerow([r["external_event_date"],r["external_source"],r["external_event_date"], r["component_cluster_id"], r["row_id"], r["match_confidence"], r["candidate_status"]])

# internally discovered events (based on structural repetition, not report)
internal_events = [
    {"internal_event_id":"IE-0001","defining_trigger":"parent star burst with >=800 child rows","source_row_ids":["R0024455"],"structural_support":"top parent R0024455 has 858 children in PARENT_DIRECT/SAME_PARENT_SIBLING families","external_match":"none required","claim_level":"reconstructed structural event, not report-confirmed"},
    {"internal_event_id":"IE-0002","defining_trigger":"dead-drop write marker exact [REDACTED:destination...] + zz6017MODALCURL-like Artifactory path","source_row_ids":["R0000096"],"structural_support":"dead-drop write structural anchor","external_match":"2026-07-09 candidate only","claim_level":"reconstructed structural event"},
    {"internal_event_id":"IE-0003","defining_trigger":"8335-byte registry bundle containing Basic auth and manifest operations","source_row_ids":["R0000617"],"structural_support":"registry supply-chain composite payload","external_match":"2026-07-09 candidate only","claim_level":"reconstructed structural event"},
    {"internal_event_id":"IE-0004","defining_trigger":"global component held by shared PROXY/SERVICE/destination markers","source_row_ids":["R0000001"],"structural_support":"141,970-row G_CORE component","external_match":"none","claim_level":"broad infrastructure hub, non-explanatory"},
]
with open(RUN/"external_created_events.tsv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f,delimiter="\t")
    w.writerow(["internal_event_id","defining_trigger","source_row_ids","structural_support","external_match","claim_level"])
    for e in internal_events:
        w.writerow([e["internal_event_id"],e["defining_trigger"],";".join(e["source_row_ids"]),e["structural_support"],e["external_match"],e["claim_level"]])

# external unverified/unmatched report events (date-level)
with open(RUN/"external_unmatched_events.md","w",encoding="utf-8") as f:
    f.write("# External unmatched events\n\n")
    f.write("External report dates (38 dated events) cannot be assigned to individual Swarm rows because all source time_utc values are null. Sample anchor correspondences are listed in external_row_to_report_citations.tsv.\n")
    f.write("No row in Data/redacted_filtered.jsonl carries a source timestamp, so every external event remains candidate-only at cluster/sample level.\n")

with open(RUN/"external_false_parallel_patterns.md","w",encoding="utf-8") as f:
    f.write("# External false parallel patterns\n\n")
    f.write("- Structural similarity to report techniques (CyberGym, Artifactory dead-drop, registry bundles) is not causal attribution.\n")
    f.write("- The 144,075-row G_CORE component is held by shared marker/endpoint co-occurrence and broad infrastructure hubs; external events must not be attached to it as one operation.\n")
    f.write("- Shared `[CREDENTIAL 1]` or `[SERVICE ... URL ...]` pivots can arise from fixtures/sandbox templates; require parent provenance and repetition before early flagging.\n")
print("done")
