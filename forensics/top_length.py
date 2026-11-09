import json
from collections import Counter
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
kids={}
for r in rows:
    pid=r.get('parent_id')
    if pid is not None: kids[pid]=kids.get(pid,0)+1
# Top by text length, note child counts and broad markers
order=sorted(rows,key=lambda r:-len(r['text']))
print('Top 50 payloads by text length (up to 1000):')
for r in order[:75]:
    rid=r['id']
    markers=[]
    if len(r['text'])>2000: markers.append('large')
    if 'base64.b64decode' in r['text']: markers.append('python-b64')
    if r['text'].count('exec(')>0: markers.append('exec')
    if 'gzip.decompress' in r['text'] or 'DecompressionStream' in r['text']: markers.append('gzip')
    if 'bash' in r['text']: markers.append('bash')
    if 'curl ' in r['text']: markers.append('curl')
    if 'MKCOL' in r['text']: markers.append('mkcol')
    if 'canvas' in r['text']: markers.append('canvas')
    if r['text'].count('fetch')>1: markers.append('multi-fetch')
    print('%8s %6d children=%2d %s'%(rid,len(r['text']),kids.get(rid,0), ','.join(markers) if markers else '-'))