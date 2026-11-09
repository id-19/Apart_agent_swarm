#!/usr/bin/env python3
import json, pathlib, collections
RUN=pathlib.Path("forensics/run_2026")
profiles=json.load(open(RUN/"cluster_signature_profiles.json"))
core_rows=[json.loads(l) for l in open(RUN/"core/core_rows.ndjson",encoding="utf-8")]
by_id={r["id"]:r for r in core_rows}
node_labels=[json.loads(l) for l in open(RUN/"node_taxonomy_labels.jsonl",encoding="utf-8")]
comp_by_id={r["row_id"]:r for r in node_labels}

# Build component sets.
comp_sets=collections.defaultdict(set)
for r in node_labels:
    comp_sets[r["L4_component_cluster_id"]].add(r["row_id"])

marker_members=collections.defaultdict(set)
for p in profiles:
    if p["level"]=="L3":
        # reconstruct from node labels would be too heavy; use profile sample not enough. Skip set checks.
        pass

# Exact L1 sets from canonical groups in source/core.
src=[json.loads(l) for l in open("Data/redacted_filtered.jsonl",encoding="utf-8")]
canonical_by_id={r["id"]:None for r in src}
for cr in core_rows:
    canonical_by_id[cr["id"]]=cr["canonical_sha256"]
exact_groups=collections.defaultdict(set)
for rid,c in canonical_by_id.items():
    exact_groups[c].add(rid)

# Validate L1 profiles.
l1_checks=[]
for p in profiles:
    if p["level"]!="L1": continue
    ms=set(p["sample_member_ids"])
    # all samples share canonical
    cans={canonical_by_id[x] for x in p["sample_member_ids"]}
    # disproofs do not share canonical
    disproof_fail=0
    for d in p["disproof_ids"]:
        if canonical_by_id[d] not in (None,) and canonical_by_id[d]==p["canonical_sha256"]:
            disproof_fail+=1
    l1_checks.append(len(cans)==1 and disproof_fail==0)
l1_pass=sum(l1_checks); l1_total=len(l1_checks)

# Validate L4 components.
l4_checks=[]
for p in profiles:
    if p["level"]!="L4": continue
    cid=p["cluster_id"]; members=set() 
    # use p's sample members as proxy for component set
    disproof_fail=0
    for d in p["disproof_ids"]:
        cinfo=comp_by_id.get(d,{})
        if cinfo.get("L4_component_cluster_id")==cid:
            disproof_fail+=1
    # membership already component.
    l4_checks.append(disproof_fail==0)
l4_pass=sum(l4_checks); l4_total=len(l4_checks)

# Validate marker profiles L3 by checking sample member contains marker.
l3_checks=0; l3_total=0
for p in profiles:
    if p["level"]!="L3": continue
    l3_total+=1
    marker=p.get("marker")
    if marker is None: 
        continue
    ok=True
    for sid in p["sample_member_ids"]:
        row=by_id[sid]
        if marker not in (row.get("markers") if "markers" in row else []):
            # core row has markers
            crow=next(c for c in core_rows if c["id"]==sid)
            if marker not in crow.get("markers",[]):
                ok=False
    if ok:
        l3_checks+=1

report={
 "L1_clusters_checked": l1_total,
 "L1_trigger_acceptance_rate": l1_pass/l1_total if l1_total else 0,
 "L4_components_checked": l4_total,
 "L4_disproof_acceptance_rate": l4_pass/l4_total if l4_total else 0,
 "L3_clusters_checked": l3_total,
 "L3_sample_marker_reconciliation_rate": l3_checks/l3_total if l3_total else 0,
}
(RUN/"cluster_trigger_validation.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
