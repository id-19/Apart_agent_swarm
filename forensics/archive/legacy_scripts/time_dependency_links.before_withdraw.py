#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from pathlib import Path
root = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
timed = {json.loads(l)["id"]: json.loads(l) for l in Path("/Users/id19/scratchpad/temporal_subset/temporal_timestamps.jsonl").open() if l.strip()}
core = [json.loads(l) for l in (root/"forensics"/"run_2026"/"core"/"core_edges.ndjson").open() if l.strip()]
out = []
for e in core:
    a,b = e["source"], e["target"]
    if a in timed and b in timed:
        out.append({
            "edge_type":"TIME_DEPENDENCY",
            "source":a,"target":b,
            "proof":e["proof"],
            "supporting_class":e["edge_type"],
            "supporting_edge_type":e["edge_type"],
            "time_anchors":[a,b],
        })
# preserve directed parent_time links if one endpoint timed and edge is parent.
for e in core:
    a,b=e["source"],e["target"]
    if (a in timed) ^ (b in timed) and e["edge_type"]=="PARENT_DIRECT":
        out.append({
            "edge_type":"TIME_DEPENDENCY",
            "source":a,"target":b,
            "proof":e["proof"],
            "supporting_dependency_class":e["edge_type"],
            "time_anchor_id": a if a in timed else b,
        })
undirected=Counter(e["supporting_edge_type"] for e in out)
adj=defaultdict(set)
parents={}
for e in core:
    if e["source"] in timed and e["target"] in timed:
        adj[e["source"]].add(e["target"]); adj[e["target"]].add(e["source"])
    else:
        pass
seen=set(); sizes=[]
for n in timed:
    if n in seen: continue
    stack=[n]; comp=set()
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x); comp.add(x)
        stack.extend(adj[x]-seen)
    sizes.append(len(comp))
report={
  "time_anchor_rows": len(timed),
  "time_dependencies": len(out),
  "within_time_anchor_edges_by_support_class": dict(sorted(undirected.items())),
  "single_anchor_parent_edges": sum(1 for e in out if "time_anchor_id" in e),
  "connected_time_anchor_components": sum(1 for s in sizes if s>1),
  "max_time_anchor_component": max(sizes),
  "average_time_precision": "varies; see temporal_timestamps.jsonl",
  "time_anchor_kinds": {k:(ts.values() if False else len([r for r in timed.values() if r["kind"]==k])) for k in sorted({r["kind"] for r in timed.values()})},
  "top_time anchors_by_parent_count": sorted(((k,len(v)) for k,v in defaultdict(list).items()),key=lambda x:-x[1])[:5],
}
# add top marker bundles by count. need marker counts
import collections
mc=collections.Counter(m for r in timed.values() for m in r.get("rare_markers",[]))
report["top_timed_markers"]=mc.most_common(15)
Path(root/"forensics/run_2026/time_dependency_links.ndjson").write_text("".join(json.dumps(e,sort_keys=True,separators=(",",":"))+"\n" for e in out),encoding="utf-8")
Path(root/"forensics/run_2026/time_dependency_summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("time anchors",len(timed),"dependencies",len(out))
print("by support",undirected)
print("timed components",sum(s>1 for s in sizes),"max",max(sizes))
print("top markers",mc.most_common(8))
print("files written")
