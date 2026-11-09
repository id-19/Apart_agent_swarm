#!/usr/bin/env python3
import collections, json, pathlib, random
ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
PROJ=ROOT/"forensics/projections"
TIMED={json.loads(l)["id"]:json.loads(l) for l in open("/Users/id19/scratchpad/temporal_subset/temporal_timestamps.jsonl")}

class DSU:
    def __init__(self):
        self.p={}
    def make(self,x):
        if x not in self.p: self.p[x]=x
    def find(self,x):
        self.make(x)
        # path compression iterative
        root=x
        while self.p[root]!=root: root=self.p[root]
        while self.p[x]!=root:
            self.p[x],x=root,self.p[x]
        return root
    def union(self,a,b):
        ra,rb=self.find(a),self.find(b)
        if ra!=rb: self.p[ra]=rb

graph_defs={
 "G_CORE": ["EXACT_BODY","SAME_PARENT_SIBLING","MARKER_SAME","MARKER_ENDPOINT"],
 "G_TEXT": ["EXACT_BODY","NORMALIZED_REPLAY","NEAR_BODY_D1","NEAR_BODY_D2","NEAR_BODY_D3"],
 "G_FUNCTION": ["PARENT_DIRECT","INTENT_SIGNATURE"],
 "G_TIMESTAMP": None, # special
}
report={}
for gname,classes in graph_defs.items():
    dsu=DSU()
    nodes=set()
    edge_count=0
    edge_mix=collections.Counter()
    degree=collections.Counter()
    if gname=="G_TIMESTAMP":
        # include temporal anchor + all edges with a timed endpoint
        for clsfile in PROJ.glob("*.ndjson"):
            with clsfile.open() as f:
                for line in f:
                    if not line.strip(): continue
                    e=json.loads(line)
                    if e["source_id"] in TIMED or e["destination_id"] in TIMED:
                        a,b=e["source_id"],e["destination_id"]
                        dsu.union(a,b); nodes.add(a); nodes.add(b)
                        edge_count+=1; edge_mix[e["edge_class"]]+=1
                        degree[a]+=1; degree[b]+=1
    else:
        for cname in classes:
            path=PROJ/(cname.lower()+".ndjson")
            if not path.exists(): continue
            with path.open() as f:
                for line in f:
                    if not line.strip(): continue
                    e=json.loads(line)
                    a,b=e["source_id"],e["destination_id"]
                    dsu.union(a,b); nodes.add(a); nodes.add(b)
                    edge_count+=1; edge_mix[e["edge_class"]]+=1
                    degree[a]+=1; degree[b]+=1
    # component sizes
    comp_counts=collections.Counter()
    for n in nodes:
        comp_counts[dsu.find(n)]+=1
    sizes=sorted(comp_counts.values(),reverse=True)
    report[gname]={
      "nodes":len(nodes),
      "edges":edge_count,
      "components":len(comp_counts),
      "singletons":sum(1 for v in comp_counts.values() if v==1),
      "largest_component":max(comp_counts.values()) if comp_counts else 0,
      "top_component_sizes":sizes[:20],
      "large_components_gt100":sum(1 for v in comp_counts.values() if v>100),
      "edge_class_mix":dict(edge_mix),
      "high_fan_nodes_top25":degree.most_common(25),
    }
    # save top component samples
    members_by_root=collections.defaultdict(list)
    for n in nodes:
        members_by_root[dsu.find(n)].append(n)
    topcomps=sorted(members_by_root.items(), key=lambda kv:-len(kv[1]))[:5]
    (ROOT/"forensics"/"components"/f"{gname}_components.json").write_text(json.dumps({
       "graph":gname,
       "top_components":[{"component_size":len(members),"members_sample":members[:20]} for root,members in topcomps],
    },indent=2))
    print(gname, report[gname]["nodes"], "nodes", report[gname]["edges"], "edges", report[gname]["components"], "components", "largest", report[gname]["largest_component"])

(ROOT/"forensics"/"component_summary.json").write_text(json.dumps(report,indent=2))
import csv
with open(ROOT/"forensics/high_fan_inventory.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["graph","rank","node","degree"])
    for gname,r in report.items():
        for rank,(nid,deg) in enumerate(r["high_fan_nodes_top25"],1):
            w.writerow([gname,rank,nid,deg])
print("wrote phase4")
