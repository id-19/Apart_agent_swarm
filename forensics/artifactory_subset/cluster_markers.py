import json, re, collections
rows=[json.loads(l) for l in open('/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/artifactory_subset/rows.jsonl')]
def markers(t):
    ms=set()
    for m in re.findall(r'zz[A-Za-z0-9_-]{3,}', t): ms.add(('zz',m))
    for m in re.findall(r'github-remote(?:-cache)?/[A-Za-z0-9._-]+', t): ms.add(('path',m))
    for m in re.findall(r'/github-remote(?:-cache)?/[A-Za-z0-9._-]+', t): ms.add(('path',m))
    return ms
# invert marker -> rows
idx=collections.defaultdict(set)
for i,r in enumerate(rows):
    for m in markers(r['text']):
        idx[m].add(i)
# clusters: only markers with >1 row
clusters=[ (m,sorted(rs)) for m,rs in idx.items() if len(rs)>1]
# write human report
out='/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/artifactory_subset/marker_clusters.md'
with open(out,'w') as w:
    w.write('# Marker clusters (rows sharing >=1 marker)\n\n')
    for m,rs in sorted(clusters, key=lambda x:-len(x[1]))[:60]:
        w.write(f'## Marker {m} — {len(rs)} rows\n')
        for ridx in rs:
            rr=rows[ridx]
            w.write(f"- {rr['id']} tags={rr.get('_bucket',[])} len={len(rr['text'])}\n")
        w.write('\n')
    w.write(f'\nTotal distinct markers (cross-linking)>1 (sliced): {len(clusters)}\n')
print('clusters written:', len(clusters))
