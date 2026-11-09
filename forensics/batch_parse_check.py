import json, os, subprocess, sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
start=int(sys.argv[1]); end=int(sys.argv[2])
for i in range(start, end+1):
    rid='R%07d'%i
    text=byid[rid]['text']
    out='/tmp/'+rid+'.js'
    open(out,'w').write(text)
    p=subprocess.run(['node','--check',out], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    status='PARSE_OK' if p.returncode==0 else 'PARSE_FAIL'
    print(rid, status)
    if p.returncode!=0:
        print('  ', p.stderr.strip().splitlines()[-1][:120])