import collections, json, pathlib
path=pathlib.Path("/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson")
result={}
for mx in range(4):
    parent={}
    def find(x):
        parent.setdefault(x,x); root=x
        while parent[root]!=root: root=parent[root]
        while parent[x]!=root: parent[x],x=root,parent[x]
        return root
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[ra]=rb
    counts=collections.Counter()
    degrees=collections.Counter()
    rows=0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            o=json.loads(line)
            d=o["levenshtein_distance"]
            if d <= mx:
                rows+=1; counts[d]+=1
                a,b=o["source_id"],o["target_id"]
                union(a,b); degrees[a]+=1; degrees[b]+=1
    comps=collections.Counter(find(n) for n in parent)
    sizes=sorted(comps.values(),reverse=True)
    result[f"distance_<=_{mx}"]={
        "candidate_edges": rows,
        "distance_counts_within_cutoff": dict(sorted(counts.items())),
        "unique_sample_nodes": len(parent),
        "components": len(comps),
        "singletons": sum(v==1 for v in comps.values()),
        "components_over_100": sum(v>100 for v in comps.values()),
        "nontrivial_nodes": sum(v for v in comps.values() if v>1),
        "component_sizes_top50": sizes[:50],
        "component_sizes_gt100": [v for v in sizes if v>100][:25],
        "max_degree": max(degrees.values()) if degrees else 0,
        "top_degree_nodes": degrees.most_common(10),
        "average_degree": (2*rows/len(parent)) if parent else 0,
    }
    print(mx, rows, len(parent), len(comps), sizes[:10])
out=json.dumps(result,indent=2)
pathlib.Path("forensics/run_2026/near_distance_summary_v2.json").write_text(out,encoding="utf-8")
print("wrote")
