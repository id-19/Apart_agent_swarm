import json

rows = [json.loads(line) for line in open('/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted.jsonl')]
text = rows[0]['text']

# State machine that treats backslash as escape inside strings.
i = 0
n = len(text)
in_single = False
in_double = False
in_back = False
escape = False
last_open_index = None
quote_opens = []

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
    if not (in_single or in_double or in_back):
        if c == '"':
            in_double = True
            last_open_index = i
        elif c == "'":
            in_single = True
            last_open_index = i
        elif c == '`':
            in_back = True
            last_open_index = i
    else:
        if in_double and c == '"':
            in_double = False
            quote_opens.append((last_open_index, i))
        elif in_single and c == "'":
            in_single = False
            quote_opens.append((last_open_index, i))
        elif in_back and c == '`':
            in_back = False
            quote_opens.append((last_open_index, i))
    i += 1

print('final state: in_double=%s in_single=%s in_back=%s' % (in_double, in_single, in_back))
print('last open index:', last_open_index)
print('context around last open:')
start = max(0, (last_open_index or 0) - 60)
end = min(n, (last_open_index or 0) + 120)
print(repr(text[start:end]))
print()
print('total paired double/single/backtick quote strings parsed:', len(quote_opens))