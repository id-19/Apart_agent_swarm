import json, re, os, hashlib, subprocess
import sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
# Parse deep ledger header entries (only first 200 IDs):
ledger=open(root+'/forensics/deep_payload_ledger.md').read()
ids=[m.group(1) for m in re.finditer(r'^## (R\d+)$', ledger, flags=re.M)]
# If a header appears multiple times, it will still be listed; we check uniqueness.
print('ledger exact-header IDs:', len(ids), 'unique:', len(set(ids)))
print('duplicate headers:', [i for i,x in enumerate(ids) if ids.count(x)>1])
print()
# choose first 200 unique ordered IDs by integer; expect R0000001...
ordered=sorted(set(ids), key=lambda x:int(x[1:]))
limit=int(sys.argv[1]) if len(sys.argv)>1 else 200
target=ordered[:limit]
# children map
children_by_parent={}
for r in rows:
    children_by_parent.setdefault(r.get('parent_id'),[]).append(r['id'])
# source handle counts
alltext={r['id']:r for r in rows}
from collections import Counter
all_handles=Counter()
for r in rows:
    for m in re.finditer(r'runtime_identifier:(\d+)',r['text']):
        all_handles['runtime_identifier:'+m.group(1)] += 1
source_handles=Counter()
for r in rows:
    for m in re.finditer(r'source_identifier:(\d+)',r['text']):
        source_handles['source_identifier:'+m.group(1)] += 1
print('TARGET rows:',len(target),'first=',target[0],'last=',target[-1])
out=[]
for rid in target:
    row=byid[rid]
    # verify cite hash
    rhash=hashlib.sha256(row['text'].encode()).hexdigest()[:8]
    cite_ok = rhash == row['cite'].split(':')[1]
    parse_file='/tmp/'+rid+'.js'
    open(parse_file,'w').write(row['text'])
    p=subprocess.run(['node','--check',parse_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    parse_ok=(p.returncode==0)
    kids=children_by_parent.get(rid,[])
    # child byte relation with parent
    cont_markers=[]
    for c in kids:
        ct=alltext[c]['text']
        # count how many stripped substrings of length 20 from parent occur in child
        mm=0
        for i in range(0,len(row['text'])-19,random_step:=197):
            if row['text'][i:i+20] in ct: mm+=1
        cont_markers.append('%s=%d'% (c,mm))
    hs=re.findall(r'runtime_identifier:\d+',row['text'])
    hs2=re.findall(r'source_identifier:\d+',row['text'])
    corr={
    'id':rid,
    'line':rows.index(row)+1,
    'cite_suffix_ok':cite_ok,
    'node_parse_ok':parse_ok,
    'kind':row['kind'],
    'parent_id':row.get('parent_id'),
    'children':kids,
    'child_overlap_score': '/'.join(cont_markers) if cont_markers else 'none',
    'task_handles': sorted(set(hs)),
    'source_ids': sorted(set(hs2)),
    'handle_globals':[(h,all_handles.get(h)) for h in set(hs)],
    'source_globals':[(h,source_handles.get(h)) for h in set(hs2)],
    'credential_placeholders': row['text'].count('CREDENTIAL'),
    'has_zzer?': any(m.startswith('zz') or 'zz' in m for m in re.findall(r'zz[A-Za-z0-9._-]{6,}',row['text'])),
    'zz_markers': re.findall(r'zz[A-Za-z0-9._-]{6,}',row['text']),
    }
    out.append(corr)
    print(rid,'cite',cite_ok,'parse',parse_ok,'children',len(kids))
# Write JSON summary (small)
import json as J
J.dump(out, open(root+'/forensics/adversarial_validation_200.json','w'), indent=2)
print('wrote json with',len(out),'rows')