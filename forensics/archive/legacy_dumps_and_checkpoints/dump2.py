import json
rows = [json.loads(line) for line in open('Data/redacted.jsonl')]
text = rows[0]['text']
for j in range(455, 496):
    print(j, repr(text[j]))
