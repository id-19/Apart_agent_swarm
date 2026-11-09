import json
from collections import defaultdict
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
scope_ids={r['id'] for r in rows[:1040]}
children=defaultdict(list)
for r in rows:
    pid=r.get('parent_id')
    if pid in scope_ids: children[pid].append(r)
print('roots in first 1040 with >=5 children:')
for pid in sorted(children,key=lambda p:-len(children[p])):
    if len(children[pid])>=5:
        print(pid, len(children[pid]), 'len', len(byid[pid]['text']), 'excerpt:', byid[pid]['text'][:80].replace(chr(10),' '))
