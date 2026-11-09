import re
path='/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/deep_payload_ledger.md'
text=open(path).read()
parts=re.split(r'(?=^## R\d+\s*$)', text, flags=re.M)
# group: preamble (non-header) vs blocks keyed by id
blocks={}
preamble=parts[0]
for p in parts[1:]:
    h=re.match(r'## (R\d+)',p).group(1)
    if h not in blocks or len(p)>len(blocks[h]): blocks[h]=p
out=[preamble] + [blocks[h] for h in sorted(blocks)]
open(path,'w').write(''.join(out))
print('kept',len(blocks),'payload entries')