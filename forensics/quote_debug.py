import json
import sys
import os

root = '/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows = [json.loads(line) for line in open(os.path.join(root, 'Data', 'redacted.jsonl'))]
target = sys.argv[1]
text = {r['id']: r for r in rows}[target]['text']

# quote-aware state machine
i = 0
n = len(text)
in_single = in_double = in_back = False
escape = False
quote_events = []
while i < n:
    c = text[i]
    if escape:
        escape = False
        i += 1
        continue
    if c == '\\':
        escape = True
        i += 1
        continue
    if c == '"' or c == "'" or c == '`':
        quote_events.append((i, c, (in_single, in_double, in_back)))
    if not (in_single or in_double or in_back):
        if c == '"':
            in_double = True
        elif c == "'":
            in_single = True
        elif c == '`':
            in_back = True
    else:
        if in_double and c == '"':
            in_double = False
        elif in_single and c == "'":
            in_single = False
        elif in_back and c == '`':
            in_back = False
    i += 1

print('id:', target, 'len:', n)
print('final state: in_single=%s in_double=%s in_back=%s' % (in_single, in_double, in_back))
print('last 12 quote events:')
for item in quote_events[-12:]:
    print(item)
# print last 30 chars with indices
start = max(0, n-35)
for j in range(start, n):
    print(j, repr(text[j]))
