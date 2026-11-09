import json
rows = [json.loads(line) for line in open('Data/redacted.jsonl')]
text = rows[0]['text']
target = 492
start = max(0, target-20)
end = min(len(text), target+20)
print('length', len(text))
print('slice repr:', repr(text[start:end]))
for j in range(start, end):
    print(j, repr(text[j]))
