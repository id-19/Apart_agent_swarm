import json
rows = [json.loads(line) for line in open('Data/redacted.jsonl')]
text = rows[0]['text']
seg=text[400:496]
print(repr(seg))
