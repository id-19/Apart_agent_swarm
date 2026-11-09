import json,sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
rows=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
byid={r['id']:r for r in rows}
parent_ids={'R%07d'%i for i in range(int(sys.argv[1]),int(sys.argv[2])+1)}
children={}
for r in rows:
    if r.get('parent_id') in parent_ids:
        children.setdefault(r['parent_id'],[]).append(r['id']+'('+r['kind']+')')
for pid in ['R%07d'%i for i in range(int(sys.argv[1]),int(sys.argv[2])+1)]:
    print(pid, ', '.join(children.get(pid,[])) if children.get(pid) else '(none)')