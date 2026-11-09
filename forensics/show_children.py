import json,sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
pid=sys.argv[1]
kids=[r for r in rows if r.get('parent_id')==pid]
print('parent',pid,'child_count',len(kids))
for c in kids:
    print('---',c['id'],c['kind'],'len',len(c['text']))
    print(c['text'][:1500])