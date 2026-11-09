import json, sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(l) for l in open(root+'/Data/redacted.jsonl')]
text={r['id']:r for r in rows}[sys.argv[1]]['text']
# rebuild events with indices
i=0;n=len(text);is_=id_=ib=False;esc=False;ev=[]
while i<n:
    c=text[i]
    if esc: esc=False;i+=1;continue
    if c=='\\': esc=True;i+=1;continue
    if c in ('"',"'",'`'): ev.append((i,c,(is_,id_,ib)))
    if not (is_ or id_ or ib):
        if c=='"': id_=True
        elif c=="'": is_=True
        elif c=='`': ib=True
    else:
        if id_ and c=='"': id_=False
        elif is_ and c=="'": is_=False
        elif ib and c=='`': ib=False
    i+=1
for e in ev:
    if 195 <= e[0] <= 430:
        print(e)
