import os

ledger = '/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/deep_payload_ledger.md'
block = open('/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/block_121_160.md').read()
text = open(ledger).read()
needle = '\n## R0000161\n'
idx = text.find(needle)
if idx == -1:
    raise SystemExit('R0000161 header not found')
text = text[:idx] + '\n' + block.rstrip() + text[idx:]
open(ledger, 'w').write(text)
print('inserted before R0000161')