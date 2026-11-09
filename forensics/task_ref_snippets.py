import json,sys,os
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
needle=sys.argv[1]
for r in rows:
    if needle in r['text']:
        idx=r['text'].find(needle)
        snippet=r['text'][max(0,idx-80):idx+120].replace('\n',' / ')
        print(r['id'], r['kind'], 'parent=',r.get('parent_id'))
        print('  ...'+snippet+'...')