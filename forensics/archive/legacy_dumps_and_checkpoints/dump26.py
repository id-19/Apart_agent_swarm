import json,sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(l) for l in open(root+'/Data/redacted.jsonl')]
text={r['id']:r for r in rows}[sys.argv[1]]['text']
for j in range(205,232):
    print(j, repr(text[j]))
