import json, os, subprocess, sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
a,b=int(sys.argv[1]),int(sys.argv[2])
ok=fail=0
for i in range(a,b+1):
    rid='R%07d'%i
    out='/tmp/'+rid+'.js'
    open(out,'w').write(byid[rid]['text'])
    p=subprocess.run(['node','--check',out],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if p.returncode==0: ok+=1
    else: fail+=1
print('range',rid if False else '%d-%d'%(a,b),'OK=%d FAIL=%d total=%d'%(ok,fail,(b-a+1)))