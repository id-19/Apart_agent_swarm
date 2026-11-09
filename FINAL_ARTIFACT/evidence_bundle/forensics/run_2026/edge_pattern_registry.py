#!/usr/bin/env python3
import collections, json, csv, re
from pathlib import Path

ROOT=Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
RUN=ROOT/"forensics/run_2026"
EDGES=RUN/"core/core_edges.ndjson"
ROWS=RUN/"core/core_rows.ndjson"
OUT=RUN/"edge_pattern_registry.csv"
rmap={json.loads(l)["id"]:json.loads(l) for l in ROWS.open() if l.strip()}
edges=[json.loads(l) for l in EDGES.open() if l.strip()]

def classify_marker(marker):
    low=marker.lower()
    if marker in ("[ENCODED BLOB]","[REDACTED SENSITIVE CONTENT]") or low.startswith("[redacted:runtime_identifier]"):
        return "generic_placeholder"
    if re.search(r"proxy|shortener|service host|ip address|server|relay|host|url",marker,re.I):
        return "endpoint_or_transit"
    if re.search(r"\d",marker) and re.search(r"[A-Za-z]",marker):
        return "numbered_content_pointer"
    if re.fullmatch(r"\[[A-Z][A-Z0-9 _:-]*\]",marker):
        return "named_static_pointer"
    return "structural_prefix"

# Aggregate by edge class and exact trigger, plus trigger category for markers
agg=collections.defaultdict(lambda: {"count":0,"samples":[]})
for e in edges:
    et=e["edge_type"]
    trig=e["proof"].rsplit(" rows=",1)[0]
    classification=classify_marker(trig) if et in ("MARKER_SAME","MARKER_ENDPOINT") else {
        "EXACT_BODY":"exact_satellite","NORMALIZED_REPLAY":"approved_normalization",
        "PARENT_DIRECT":"stored_lineage","SAME_PARENT_SIBLING":"shared_parent"}[et]
    # normalize categories to a marker tuple for the requested pattern study
    if et in ("MARKER_SAME","MARKER_ENDPOINT"):
        tuple_label=("marker", trig)
    elif et=="EXACT_BODY":
        tuple_label=("body_exact", trig)
    elif et=="NORMALIZED_REPLAY":
        tuple_label=("body_normalized", trig)
    elif et in ("PARENT_DIRECT","SAME_PARENT_SIBLING"):
        tuple_label=("parent", trig)
    else:
        tuple_label=(et,trig)
    key=(et,tuple_label[1])
    row=agg[key]
    if len(row["samples"])<4:
        if not row["samples"] or (e["source"],e["target"]) not in row["samples"]:
            row["samples"].append((e["source"],e["target"]))
    row["count"]+=1
    row["classification"]=classification
    row["tuple_label"]=str(tuple_label)

with OUT.open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["edge_class","trigger","category","tuple_label","edge_count","sample_endpoints","source_kind_pattern","target_kind_pattern"])
    for (et,trig),r in sorted(agg.items(),key=lambda x:(-x[1]["count"],x[0])):
        w.writerow([
            et,
            trig[:1200],
            r.get("classification",""),
            r.get("tuple_label",""),
            r["count"],
            ";".join(f"{a}->{b}" for a,b in r["samples"]),
            "source",
            "target",
        ])
print("uniquepatterns",len(agg),"edges",len(edges))
# Compact summary by edge class
print(json.dumps({k:sum(v["count"] for k2,v in agg.items() if k2[0]==k) for k in sorted(set(e["edge_type"] for e in edges))},sort_keys=True))
