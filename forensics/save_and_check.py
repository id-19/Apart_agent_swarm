import json
import sys
import os

root = '/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows = [json.loads(line) for line in open(os.path.join(root, 'Data', 'redacted.jsonl'))]
target = sys.argv[1]
byid = {r['id']: r for r in rows}
row = byid[target]
text = row['text']
out = '/tmp/' + target + '.js'
open(out, 'w').write(text)

children = [r for r in rows if r.get('parent_id') == target]
print('id:', target)
print('kind:', row['kind'])
print('parent_id:', row.get('parent_id'))
print('text_len:', len(text))
print('child_count:', len(children))
print('children:', ', '.join(c['id'] + '(' + c['kind'] + ')' for c in children) if children else '(none)')
print('saved_to:', out)