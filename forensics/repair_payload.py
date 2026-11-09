import json
import sys
import os

root = '/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows = [json.loads(line) for line in open(os.path.join(root, 'Data', 'redacted.jsonl'))]
target = sys.argv[1]
index = int(sys.argv[2])
text = {r['id']: r for r in rows}[target]['text']
repaired = text[:index] + '\\' + text[index:]
out = '/tmp/' + target + '_repaired.js'
open(out, 'w').write(repaired)
print('wrote', out, 'with inserted backslash at', index)