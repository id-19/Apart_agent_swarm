#!/usr/bin/env python3
import collections,json,re,hashlib,pathlib
ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
EDGES=ROOT/"forensics/run_2026/core/core_edges.ndjson"
NODES=ROOT/"forensics/run_2026/core/core_rows.ndjson"
SRC=ROOT/"Data/redacted_filtered.jsonl"
OUT=ROOT/"forensics/run_2026/core"
SRC_MAP={json.loads(l)["id"]:json.loads(l) for l in SRC.open() if l.strip()}
rows=[json.loads(l) for l in NODES.open() if l.strip()]
edges=[json.loads(l) for l in EDGES.open() if l.strip()]
rows_by_id={r["id"]:r for r in rows}
uf={r["id"]:r["id"] for r in rows}
def find(x):
    uf.setdefault(x,x); root=x
    while uf[root]!=root: root=uf[root]
    while uf[x]!=root:
        uf[x],x=root,uf[x]
    return root
def union(a,b):
    if a in uf and b in uf:
        ra,rb=find(a),find(b)
        if ra!=rb: uf[ra]=rb
for e in edges:
    if e["source"] in uf and e["target"] in uf:
        union(e["source"],e["target"])
for rid in uf: find(rid)
# component index
comp_members=collections.defaultdict(list)
for r in rows: comp_members[find(r["id"])].append(r["id"])
comp_edges=collections.defaultdict(collections.Counter)
for e in edges:
    if e["source"] in uf and e["target"] in uf:
        comp_edges[find(e["source"])].update([e["edge_type"]])
# top hubs
degree=collections.Counter()
for e in edges:
    if e["source"] in uf: degree[e["source"]]+=1
    if e["target"] in uf: degree[e["target"]]+=1
# top components report
top=[]
for comp,size in sorted(map(lambda c:(c,len(comp_members[c])),comp_members.items()),key=lambda x:-x[1])[:40]:
    member_rows=[src_map[rid] for rid in comp_members[comp]]
    marker_counts=collections.Counter()
    for rid in comp_members[comp]:
        marker_counts.update(man:=re.findall(r"\[[^\]]{1,200}\]", src_map[rid]["text"]))
    top.append({
      "component_id":comp,
      "size":size,
      "sample_ids":sorted(comp_members[comp])[:20],
      "edge_counts":dict(sorted(comp_edges[comp].items())),
      "mechanical_kinds":dict(collections.Counter(src_map[rid]["kind"] for rid in comp_members[comp])),
      "top_marker_strings":marker_counts.most_common(12),
      "top_hubs": sorted(((rid,degree[rid]) for rid in comp_members[comp]),key=lambda x:-x[1])[:8],
    })
# pattern registry tuples
pat=collections.Counter()
examples={}
for e in edges:
    if e["edge_type"].startswith("MARKER"):
        key=(e["edge_type"],e["proof"].rsplit(" rows=",1)[0])
    elif e["edge_type"] in ("EXACT_BODY","NORMALIZED_REPLAY"):
        key=(e["edge_type"], e["proof"].split("=",1)[1].rsplit(" rows=",1)[0])
    else:
        key=(e["edge_type"], e["proof"].split("= ",1)[0] if "=" in e["proof"] else e["proof"])
    pat[key]+=1
    examples.setdefault(key, (e["source"],e["target"]))
patterns=[{"edge_class":k[0],"trigger":k[1],"count":n,"example_source":examples[k][0],"example_target":examples[k][1]} for k,n in pat.items()]
patterns.sort(key=lambda x:(-x["count"],x["edge_class"],x["trigger"]))
# write JSON.
(OUT/"graph_core_components_top40.json").write_text(json.dumps(top,indent=2),encoding="utf-8")
(OUT/"graph_core_pattern_counts.json").write_text(json.dumps(patterns[:1000],indent=2),encoding="utf-8")
# markdown
md=[]
md.append("# Core sample graph audit\n")
md.append(f"Rows: {len(rows)}; edges: {len(edges)}; components: {len(comp_members)}; largest: {max(map(len,comp_members.values()))}")
md.append("## Top components")
for p in top[:15]:
    md.append(f"- Size {p['size']}: edge mix {p['edge_counts']}; kinds {p['mechanical_kinds']}; hubs {p['top_hubs']}; markers {p['top_marker_strings'][:6]}")
md.append("\n## Top link pattern tuples")
for p in patterns[:30]:
    md.append(f"- {p['edge_class']} / `{p['trigger'][:120]}` count={p['count']}, example={p['example_source']}->{p['example_target']}")
(OUT/"graph_core_summary.md").write_text("\n".join(md)+"\n",encoding="utf-8")
print((OUT/"graph_core_summary.md").read_text()[:4000])
