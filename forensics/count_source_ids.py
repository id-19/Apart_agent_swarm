import json
import sys
import os
import re

root = '/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows = [json.loads(line) for line in open(os.path.join(root, 'Data', 'redacted.jsonl'))]

pattern = re.compile(r'source_identifier:([0-9]+)')
counts = {}
for row in rows:
    for match in pattern.finditer(row['text']):
        key = match.group(1)
        counts.setdefault(key, 0)
        counts[key] += 1

if len(sys.argv) == 1:
    # Print all counts in descending order.
    for key, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:40]:
        print(key, n)
else:
    for key in sys.argv[1:]:
        print(key, counts.get(key, 0))