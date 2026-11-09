import json,sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
target=sys.argv[1]
r={x['id']:x for x in rows}[target]
print('id',r['id'])
print('cite',r['cite'])
print('len',len(r['text']))
print('children', [x['id']+'('+x['kind']+')' for x in rows if x.get('parent_id')==target])
print('text preview:\n'+r['text'][:1200])