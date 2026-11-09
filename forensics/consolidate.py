import json, re, sys
from collections import Counter
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
scope_rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
scope_ids={r['id'] for r in scope_rows[:200]}
all_rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
scope=scope_rows[:200]
def counter_for(pat, source=None):
    src=source or scope
    c=Counter()
    for r in src:
        for m in re.finditer(pat, r['text']):
            c[m.group(0)] += 1
    return c
print('scope size:', len(scope))
print('\nTASK HANDLES (runtime_identifier:NNNNNN):')
for k,v in counter_for(r'runtime_identifier:\d+').most_common():
    print(' ', k, v)
print('\nSOURCE/CHECKSUM IDENTIFIERS:')
for k,v in counter_for(r'source_identifier:\d+').most_common():
    print(' ', k, v)
print('\nREDACTION DESTINATIONS (destination:N):')
for k,v in counter_for(r'destination:\d+').most_common(14):
    print(' ', k, v)
print('\nSHORTENER CODES (invoked or referenced):')
for k,v in counter_for(r'SHORTENER CODE \d+').most_common():
    print(' ', k, v)
print('\nHOSTS IN https/ URLS:')
hostc=Counter()
for r in scope:
    for m in re.findall(r'https?://([A-Za-z0-9._-]+)', r['text']):
        hostc[m]+=1
for k,v in hostc.most_common(20):
    print(' ', k, v)
print('\nZZ MARKERS (top):')
zz=Counter()
for r in scope:
    for m in re.findall(r'zz[A-Za-z0-9._-]{6,}',r['text']):
        zz[m]+=1
for k,v in zz.most_common(12):
    print(' ', k, v)
print('\nCHILD LINKS:')
children=[r for r in all_rows if r.get('parent_id') in scope_ids]
print('children linked to R0000001-R00000200 roots:', len(children))
for c in children:
    print('  ', c['id'], c['kind'], 'parent', c['parent_id'], 'len', len(c['text']))