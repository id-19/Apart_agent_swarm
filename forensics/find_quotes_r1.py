import json
rows = [json.loads(line) for line in open('Data/redacted.jsonl')]
text = rows[0]['text']

# Reproduce state machine but record each quote and its estado.
i = 0
n = len(text)
in_single = in_double = in_back = False
escape = False
in_string_state_before = []
events = []
while i < n:
    c = text[i]
    pre = (in_single, in_double, in_back)
    if escape:
        escape = False
        i += 1
        continue
    if c == '\\':
        escape = True
        i += 1
        continue
    if c == '"' or c == "'" or c == '`':
        events.append((i, c, pre, (in_single, in_double, in_back)))
    # update state
    if not (in_single or in_double or in_back):
        if c == '"': in_double = True
        elif c == "'": in_single = True
        elif c == '`': in_back = True
    else:
        if in_double and c == '"': in_double = False
        elif in_single and c == "'": in_single = False
        elif in_back and c == '`': in_back = False
    i += 1

# Print events near the task id
for idx, ch, pre, post in events:
    if 360 <= idx <= 495:
        print(idx, repr(ch), 'pre=', pre, 'post=', post)
print('total events', len(events))