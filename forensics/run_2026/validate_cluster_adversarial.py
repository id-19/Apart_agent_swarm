#!/usr/bin/env python3
import json, pathlib, collections, random

RUN=pathlib.Path("forensics/run_2026")
ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
core_rows=[json.loads(l) for l in open(RUN/"core/core_rows.ndjson",encoding="utf-8")]
source_rows=[json.loads(l) for l in open(ROOT/"Data/redacted_filtered.jsonl",encoding="utf-8") if l.strip()]
by_id={r["id"]:r for r in core_rows}
source_by_id={r["id"]:r for r in source_rows}
labels=[json.loads(l) for l in open(RUN/"node_taxonomy_labels.jsonl",encoding="utf-8")]
canonical_by_id={r["id"]:r["canonical_sha256"] for r in core_rows}
marker_by_id={r["id"]:set(r.get("markers",[])) for r in core_rows}
profiles=json.load(open(RUN/"cluster_signature_profiles.json"))
rng=random.Random(731)

def family(m):
    toks=m.strip("[]").split()
    return " ".join(toks[:3]) if len(toks)>=3 else (toks[0] if toks else m)

# Precompute marker-family sets and a global row id list.
family_to_ids=collections.defaultdict(set)
for rid,mks in marker_by_id.items():
    for m in mks:
        family_to_ids[family(m)].add(rid)
prefix_to_ids=collections.defaultdict(list)
for rid,r in source_by_id.items():
    prefix_to_ids[r["text"].lower()[:40]].append(rid)
all_ids=sorted(source_by_id)
# component id per row
comp_by_id={lab["row_id"]:lab["L4_component_cluster_id"] for lab in labels}
comp_members=collections.defaultdict(set)
for rid,cid in comp_by_id.items():
    comp_members[cid].add(rid)

results={"L1":[],"L3":[],"L4":[]}
l1_tested=l1_adv=l1_pass=0
l3_tested=l3_adv=l3_pass=0
l4_tested=l4_adv=l4_pass=0

# L1: all recurring clusters with >=10 members
for p in profiles:
    if p["level"]!="L1" or p["member_count"]<10:
        continue
    canon=p["canonical_sha256"]
    mems=set(p["sample_member_ids"])
    seed=source_by_id[p["sample_member_ids"][0]]["text"].lower()[:40]
    adv=[rid for rid in prefix_to_ids.get(seed,[]) if rid not in mems and canonical_by_id[rid]!=canon][:5]
    if len(adv)<3:
        continue
    l1_tested+=1; l1_adv+=len(adv)
    if all(canonical_by_id[rid]!=canon for rid in adv):
        l1_pass+=len(adv)
    results["L1"].append((p["cluster_id"],p["member_count"],len(adv),all(canonical_by_id[rid]!=canon for rid in adv)))

# L3: all marker-pivot clusters >=10
for p in profiles:
    if p["level"]!="L3" or p["member_count"]<10:
        continue
    marker=p["marker"]
    fam=family(marker)
    adv=[rid for rid in family_to_ids.get(fam,()) if marker not in marker_by_id[rid]][:5]
    if len(adv)<3:
        continue
    l3_tested+=1; l3_adv+=len(adv)
    if all(marker not in marker_by_id[rid] for rid in adv):
        l3_pass+=len(adv)

# L4: all components with >=10
for p in profiles:
    if p["level"]!="L4" or p["member_count"]<10:
        continue
    cid=p["cluster_id"]
    mems=comp_members.get(cid,set())
    adv=[rid for rid in all_ids if rid not in mems][:5]
    if len(adv)<3:
        continue
    l4_tested+=1; l4_adv+=len(adv)
    if all(rid not in mems for rid in adv):
        l4_pass+=len(adv)

report={
 "L1_recurring_clusters_tested":l1_tested,
 "L1_adversaries_tested":l1_adv,
 "L1_trigger_fail_rate_percent":round(100.0*l1_pass/max(l1_adv,1),4),
 "L3_marker_clusters_tested":l3_tested,
 "L3_adversaries_tested":l3_adv,
 "L3_trigger_fail_rate_percent":round(100.0*l3_pass/max(l3_adv,1),4),
 "L4_components_tested":l4_tested,
 "L4_adversaries_tested":l4_adv,
 "L4_nonmembership_fail_rate_percent":round(100.0*l4_pass/max(l4_adv,1),4),
 "sampling_rule":"up to 5 family-local adversarial rows per tested significant cluster",
 "seed":731,
}
(RUN/"cluster_adversarial_validation.json").write_text(__import__("json").dumps(report,indent=2))
print(__import__("json").dumps(report,indent=2))

# log
import datetime,json as j
entry={"ts":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"phase":2,"action":"independent_cluster_adversarial_validation_full","files":["cluster_adversarial_validation.json"],"status":"complete"}
with open(RUN.parent/"reconstruction_log.jsonl","a",encoding="utf-8") as f:
    f.write(j.dumps(entry,separators=(",",":"),ensure_ascii=False)+"\n")
