import csv, os, sys
root='/Users/id19/Programming/AI_research/Apart_agent_swarm'
inp=os.path.join(root,'forensics','first_10000_payload_audit.tsv')
out=os.path.join(root,'forensics','per_payload_index_10000.md')
# also read raw snippet separately from the audit json/text not available here;
# each row contains the TSV fields only. Use source redacted text to obtain 50-char sanitized snippet.
rows=[r for r in csv.DictReader(open(inp), delimiter='\t')]
# Map id->row in Data by line numbers? Data IDs sequential, so line index = int(id_suffix)-1, text present under redacted JSON
import json
data=[json.loads(line) for line in open(root+'/Data/redacted.jsonl')]
filemap={r['id']:r for r in data[:10000]}
# redacted snippet sanitizer
def san(s):
    s=s.replace('\n',' / ').replace('`','"')
    if len(s)>180: s=s[:180]+'...'
    return s
with open(out,'w') as w:
    w.write('# Per-payload index for all 10,000 IDs (R0000001–R0010000)\n\n')
    w.write('This is a concise, payload-level index generated from the existing per-ID structural audit; \n')
    w.write('it records every ID separately. Fully human-deep rows remain identifiable by the workspace\n')
    w.write('ledger: deep_payload_ledger.md begins exact rows through R0000001–R00000200.\n\n')
    for r in rows:
        rid=r['id']
        t=filemap[rid]['text']
        w.write('## {}\n'.format(rid))
        w.write('- structural category: {}\n'.format(r['category']))
        w.write('- tags: {}\n'.format(r['tags']))
        w.write('- language: {}\n'.format(r['language']))
        w.write('- structural validity: {}\n'.format(r['validity']))
        w.write('- credential placeholder present: {}\n'.format(r['cred']=='True'))
        w.write('- text length: {}\n'.format(r['text length' ] if 'text length ' in r else ('text_length' in r and r.get('text length')) or r.get('len')))
        # The TSV field name has \tsafe? Handle both supported names.
        ln = r.get('text_length') or r.get('text length') or r.get('len')
        if ln is not None:
            w.write('- text length (verified from TSV): {}\n'.format(ln))
        else:
            w  # no-op
        w.write('- external hosts: {}\n'.format(r['hosts'] or '(none)'))
        w.write('- pivot markers: {}\n'.format(r['pivots'] or '(none)'))
        w.write('- child rows: {}\n'.format(r['children_ids'] or '(none)'))
        w.write('- shared zz markers: {}\n'.format(r['shared_zz_count']))
        w.write('- payload snippet: `{}`\n'.format(san(t)))
        w.write('\n')
print('wrote', out)