import json, collections, pathlib
path=pathlib.Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")

def weighted(dist_max):
    parent={}
    def find(x):
        parent.setdefault(x,x); root=x
        while parent[root]!=root: root=parent[root]
        while parent[x]!=root: parent[x],x=root,parent[x]
        return root
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[ra]=rb
    rows=edges=0
    histogram=collections.Counter()
    degree=collections.Counter()
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            o=json.loads(line)
            d=o["levenshtein_distance"]
            if d > dist_max: continue
            rows +=0
            edges+=1
            histogram[d]+=1
            a,b=o["source_id"],o["target_id"]
            union(a,b); degree[a]+=1; degree[b]+=1
    comps=collections.Counter(find(k) for k in parent)
    sizes=sorted(comps.values(),reverse=True)
    return {
        "edge_count":edges,
        "distance_counts":dict(sorted(histogram.items())),
        "endpoints":len(parent),
        "components":len(comps),
        "component_sizes_top20":sizes[:20],
        "large_components_gt100":sum(v>100 for v in sizes),
        "singletons":sum(v==1 for v in sizes),
        "max_degree":max(degree.values()) if degree else 0,
        "top_degree_nodes":degree.most_common(10),
    }

out={}
for mx in (0,1,2,3):
    r=weighted(mx)
    out[f'distance_{mx}']=r
    print(f"distance <= {mx}:",r["edge_count"],"edges,",r["endpoints"],"nodes,",r["components"],"components; top sizes",r["component_sizes_top20"][:5])
import json
Path= __import__("pathlib").Path
(p:=Path("forensics/run_2026/near_distance_stats.json")).write_text(json.dumps(out,indent=2),encoding="utf-8")
print("wrote",p)
