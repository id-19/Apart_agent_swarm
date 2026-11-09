import json, sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
scope={r['id'] for r in rows[:690]}
children={}
for r in rows:
    if r.get('parent_id') in scope:
        children.setdefault(r['parent_id'],[]).append(r['id'])
print('roots with >=5 children:')
for pid in sorted(children, key=lambda p: -len(children[p])):
    if len(children[pid])>=5:
        print(pid, len(children[pid]))
print('\nroots with 3+ and <=? sorted first 30 overall:')
for pid in sorted(children, key=lambda p: -len(children[p]))[:35]:
    print(pid, len(children[pid]))