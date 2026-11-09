#!/usr/bin/env python3
import json, collections, re
from pathlib import Path

ROOT=Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
RUN=ROOT/"forensics"/"run_2026"
CORE=RUN/"core"
ROWS=ROOT/"Data/redacted_filtered.jsonl"
row_map={}
for line in ROWS.open(encoding="utf-8"):
    if line.strip():
        r=json.loads(line)
        row_map[r["id"]]=r
rows={json.loads(line)["id"]:json.loads(line) for line in (CORE/"core_rows.ndjson").open(encoding="utf-8") if line.strip()}
edges=[json.loads(l) for l in (CORE/"core_edges.ndjson").open(encoding="utf-8") if l.strip()]
uf={rid:rid for rid in rows}
def find(x):
    root=x
    while uf[root]!=root: root=uf[root]
    while uf[x]!=root:
        uf[x],x=root,uf[x]
    return root
for e in edges:
    if e["source"] in uf and e["target"] in uf:
        a,b=e["source"],e["target"]
        ra,rb=find(a),find(b)
        if ra!=rb: uf[ra]=rb
for rid in rows: find(rid)
comp_members=collections.defaultdict(list)
for rid in rows: comp_members[find(rid)].append(rid)
edge_counts=collections.defaultdict(collections.Counter)
for e in edges:
    if e["source"] in uf and e["target"] in uf:
        edge_counts[find(e["source"])][e["edge_type"]]+=1
token_re=re.compile(r"\[[^\]]{1,200}\]")
marker_by_comp=collections.defaultdict(collections.Counter)
for comp,members in comp_members.items():
    for rid in members:
        marker_by_comp[comp].update(token_re.findall(row_map[rid]["text"]))
degree=collections.Counter()
for e in edges:
    if e["source"] in uf: degree[e["source"]]+=1
    if e["target"] in uf: degree[e["target"]]+=1
top=[]
for comp,members in sorted(comp_members.items(),key=lambda kv:(-len(kv[1]),str(kv[0])))[:100]:
    top.append({
      "rank":len(top)+1,
      "component_id":comp,
      "size":len(members),
      "edge_counts":dict(sorted(edge_counts[comp].items())),
      "mechanical_kinds":{k:v for k,v in sorted(collections.Counter(row_map[r]["kind"] for r in members).items())},
      "top_markers":marker_by_comp[comp].most_common(12),
      "top_hubs":[{"id":rid,"degree":degree[rid]} for rid in sorted(members,key=lambda r:degree[r],reverse=True)[:8]],
      "sample_members":sorted(members)[:12],
    })
import json as J
(RUN/"core/component_stats_top100.json").write_text(J.dumps(top,indent=2),encoding="utf-8")
md=["# Core graph metrics","","- Rows: %d; core edges: %d; components: %d; nontrivial: %d; largest: %d"%(len(rows),len(edges),len(comp_members),sum(len(v)>1 for v in comp_members.values()),max(map(len,comp_members.values()))),"","## Edge classes"]
for et,n in sorted(collections.Counter(e["edge_type"] for e in edges).items(),key=lambda x:-x[1]):
    md.append(f"- {et}: {n:,}")
md.append("\n## Top components")
for item in top[:25]:
    md.append(f"- Size {item['size']}: {item['edge_counts']}; kinds={item['mechanical_kinds']}; markers={item['top_markers'][:5]}")
(RUN/"graph_metrics.md").write_text("\n".join(md)+"\n",encoding="utf-8")
print("wrote",len(top),"components; largest",max(map(len,comp_members.values())))
