import json
rows = [json.loads(line) for line in open('Data/redacted.jsonl')]
text = rows[0]['text']
k = text.rfind('task_id')
print('task_id pos', k)
start=max(0,k-10); end=min(len(text),k+60)
for j in range(start,end):
    print(j, repr(text[j]))
