import json,sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
text={r['id']:r for r in rows}[sys.argv[1]]['text']
print('len',len(text))
for j in range(0,40):
    print(j, repr(text[j]))