import json, re
from collections import Counter, defaultdict
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
children=defaultdict(list)
for r in rows:
    pid=r.get('parent_id')
    if pid: children[pid].append(r)
print('Top 30 roots by child count:')
for pid in sorted(children,key=lambda p:-len(children[p]))[:30]:
    print(pid,'children',len(children[pid]),'len',len(byid[pid]['text']),'text[:80]='+byid[pid]['text'][:80].replace(chr(10),' '))
