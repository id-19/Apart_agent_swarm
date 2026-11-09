import json, re
from collections import Counter
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
a,b=1,1040
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
scope=rows[a-1:b]
def C(p):
    x=Counter()
    for r in scope:
        for m in re.finditer(p,r['text']): x[m.group(0)]+=1
    return x
print('scope',len(scope))
print('\nTask handles:'); [print(' ',k,v) for k,v in C(r'runtime_identifier:\d+').most_common(12)]
print('\nExternal hosts:')
hc=Counter()
for r in scope:
    for m in re.findall(r'https?://([A-Za-z0-9._-]+)', r['text']): hc[m]+=1
[print(' ',k,v) for k,v in hc.most_common(15)]
print('\nShortener codes:')
for k,v in C(r'SHORTENER CODE \d+').most_common(): print(' ',k,v)
print('\nContain zz markers:', sum(1 for r in scope if 'zz' in r['text']))
print('\nChild relationships:', sum(1 for r in open(root+'/Data/redacted.jsonl') and [json.loads(x) for x in open(root+'/Data/redacted.jsonl')] if r.get('parent_id') in {x['id'] for x in scope}))