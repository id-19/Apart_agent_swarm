import json,sys,os
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
needle=sys.argv[1]
matches=[r for r in rows if needle in r['text']]
print('needle',needle,'count',len(matches))
for r in matches[:25]:
    print(r['id'], 'kind=',r['kind'],'parent=',r['parent_id'])
