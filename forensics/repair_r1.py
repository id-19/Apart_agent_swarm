import json
rows = [json.loads(line) for line in open('/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted.jsonl')]
text = rows[0]['text']
# Insert the missing backslash before the unescaped closing quote of the task_id value.
repaired = text[:490] + '\\' + text[490:]
open('/tmp/r1_repaired.js', 'w').write(repaired)
print('wrote repaired variant')
