import json, re, os
ROOT='/Users/id19/Programming/AI_research/Apart_agent_swarm'
ALL=[json.loads(x) for x in open(f'{ROOT}/Data/redacted.jsonl')]
SCOPE=ALL[:10000]
BYID={r['id']:r for r in ALL}
CHILDREN={}
for r in ALL:
    pid=r.get('parent_id')
    if pid is not None:
        CHILDREN.setdefault(pid,[]).append(r)

# inverted index for zz markers across scope
ZZ_INDEX={}
MARKERS_KNOWN=['TINYOK','CHAINWORKS','FANPASS_12345','CYBERGYM','ENCODED BLOB','getent','sqlite3_initialize','relay','manifest']
def zz_markers(t):
    return set(re.findall(r'zz[A-Za-z0-9._-]{6,}', t))

for r in SCOPE:
    for m in zz_markers(r['text']):
        ZZ_INDEX.setdefault(m,[]).append(r['id'])

def sanitize(s):
    s=s.replace('\n',' / ').replace('\r','')
    s=s.replace('`','\'')
    if len(s)>500: s=s[:500]+'…'
    return s

def tags(t):
    out=[]; low=t.lower()
    if re.search(r'fetch\s*\(', t): out.append('fetch')
    if 'XMLHttpRequest' in t: out.append('xhr')
    if re.search(r'urllib|urlopen|requests\.', t): out.append('python-http')
    if 'MKCOL' in t: out.append('mkcol')
    if 'getent ' in low: out.append('getent')
    if re.search(r'eval\s*\(\s*atob', t.replace(' ','')): out.append('eval-atob')
    if re.search(r'matchAll\(\s*/href', t): out.append('dir-list-assembly')
    if '.manifest' in low: out.append('docker-manifest')
    if 'new Image' in t: out.append('image-beacon')
    if 'sqlalchemy' in low or 'sqlite3_initialize' in t: out.append('cyber-shell')
    if re.search(r'zz[A-Za-z0-9._-]{3,}', t): out.append('zz-marker')
    if re.search(r'proxy', t, re.I): out.append('proxy')
    if 'artifactory' in low or 'packages.hub.ace-research' in low or 'packages.app.ace-research' in low: out.append('artifactory')
    if 'base64' in low or 'atob' in t or 'btoa' in t: out.append('base64')
    if re.search(r'bash|/bin/sh|\bsh -c|curl ', t, re.I): out.append('shell')
    if 'document.write' in t or 'document.body' in t or 'document.append' in t or 'document.write' in t: out.append('dom')
    if re.search(r'huggingface\.co|hf\.co|datasets-server', t, re.I): out.append('huggingface')
    if re.search(r'registry-1\.docker\.io|auth\.docker\.io|hub\.docker\.com', t): out.append('docker-registry')
    if re.search(r'shortener|SHORTENER', t): out.append('shortener')
    if re.search(r'^https?://', t.strip()): out.append('bare-url')
    if re.search(r'<script|<img|<iframe', t): out.append('html-injection')
    if re.search(r'JSON\.parse|JSON\.stringify', t): out.append('json')
    if 'SERVICE HOST' in t or 'SERVICE 2 URL' in t or 'SERVICE 3 URL' in t: out.append('service-redacted')
    if not out: out.append('none')
    return out

def category(t,ts):
    low=t.lower()
    if 'eval-atob' in ts or 'dir-list-assembly' in ts:
        return 'JS-DIRECTORY-REASSEMBLE-AND-EVAL'
    if 'mkcol' in ts and ('cyber-shell' in ts or 'python-http' in ts or 'shell' in ts):
        return 'CYBERGYM-SHELL-TO-ARTIFACTORY-DEAD-DROP-WRITE'
    if 'cyber-shell' in ts:
        return 'CYBERGYM-SQL-INJECTION-SHELL-TEMPLATE'
    if 'python-http' in ts:
        if 'artifactory' in ts: return 'PYTHON-REMOTE-READ-WRITE-ARTIFACTORY'
        return 'PYTHON-HTTP-CLIENT-PROBE'
    if 'image-beacon' in ts and 'shortener' in ts:
        return 'JS-IMAGE-BEACON-EXFIL-TO-SHORTENER'
    if 'shortener' in ts and ('fetch' in ts or 'dom' in ts):
        return 'JS-FETCH-AND-REPORT-TO-SHORTENER'
    if 'docker-registry' in ts or 'docker-manifest' in ts:
        return 'DOCKER-REGISTRY-MANIFEST-PROBE'
    if 'huggingface' in ts:
        if 'datasets-server' in low: return 'HF-DATASETS-SERVER-API-PROBE'
        return 'HUGGINGFACE-MODEL-DATASET-PROBE'
    if 'artifactory' in ts:
        return 'ARTIFACTORY-PATH-PROBE-OR-RELAY'
    if 'bare-url' in ts and len(t)<200:
        return 'BARE-ENDPOINT-PROBE'
    if 'html-injection' in ts:
        return 'HTML-SCRIPT-IMAGE-INJECTION'
    if 'fetch' in ts or 'xhr' in ts:
        return 'BROWSER-OR-RELAY-FETCH'
    if 'none' in ts:
        return 'UNCATEGORIZED-OPAQUE-PAYLOAD'
    return 'MIXED-OR-SECONDARY'

def language(t,ts):
    if 'python-http' in ts: return 'Python (urllib/requests)'
    if 'shell' in ts and 'python-http' not in ts: return 'Shell/JS hybrid'
    if 'json' in ts and not ('fetch' in ts or 'dom' in ts): return 'JSON/HTTP'
    if 'fetch' in ts or 'xhr' in ts or 'dom' in ts or 'eval-atob' in ts or 'image-beacon' in ts or 'html-injection' in ts:
        return 'JavaScript (browser/relay)'
    if 'bare-url' in ts: return 'URL/HTTP endpoint'
    return 'Unknown/opaque'

def validity(t):
    # bracket/quote balance (coarse)
    opens=t.count('{')+t.count('(')+t.count('[')
    closes=t.count('}')+t.count(')')+t.count(']')
    q1=t.count("'"); q2=t.count('"'); bt=t.count('`')
    notes=[]
    note='balanced' if opens==closes else f'unbalanced-brackets({opens} open vs {closes} close)'
    qnote='quotes-odd' if (q1%2 or q2%2 or bt%2) else 'quotes-even'
    redcount=len(re.findall(r'\[REDACTED|\[CREDENTIAL|\[SERVICE|\[HF |\[SHORTENER|\[ENCODED|\[PROXY|\[BLOB', t))
    return note, qnote, redcount

def hosts(t):
    return sorted(set(re.findall(r'https?://([A-Za-z0-9._-]+)', t)))

def external_events(catv,t):
    out=[]
    cl=catv.lower()
    if 'artifactory' in cl or 'dead-drop' in cl or 'cyber' in cl or 'eval' in cl or 'assembly' in cl:
        out.append('OpenAI report: May Artifactory inter-agent message-board/SSRF; Jun 26 token-refresh compromise; Jul 4 outage; Jul 8+ Hugging Face pivot (see §III/§IV).')
    if 'huggingface' in cl or 'hf-' in cl:
        out.append('OpenAI report: Jul 10 exposed HF credentials published to Artifactory board; Jul 11-13 HF compromise (see §IV).')
    if 'docker' in cl:
        out.append('OpenAI report: third-party artifact storage / credential harvesting phase (see §V/§VI).')
    if 'shortener' in cl or 'beacon' in cl or 'fetch' in cl and 'shortener' in t.lower():
        out.append('OpenAI report: server-side fetch / SSRF relay egress via Artifactory (see §V).')
    # known pivot markers
    pivs=[m for m in MARKERS_KNOWN if m.lower() in t.lower()]
    if pivs:
        out.append('Local forensics pivot markers present: '+', '.join(pivs)+'.')
    if not out:
        out.append('No direct external-event binding in available sources (no timestamps in dataset).')
    return out

def inference(catv,ts,hasc,children):
    base={
     'JS-DIRECTORY-REASSEMBLE-AND-EVAL':'Fetches an Artifactory directory listing, extracts chunked filename segments, base64-decodes and evals them => executes attacker-controlled JS. Read+code-execution stage.',
     'CYBERGYM-SHELL-TO-ARTIFACTORY-DEAD-DROP-WRITE':'Injects shell command via sqlite3_initialize vector and MKCOLs a dead-drop dir into Artifactory cache carrying encoded system info => write-side staging/exfil.',
     'CYBERGYM-SQL-INJECTION-SHELL-TEMPLATE':'SQL-injection-style payload template carrying sqlite3_initialize + submitted code/command; likely tries command execution in eval harness.',
     'PYTHON-HTTP-CLIENT-PROBE':'Python HTTP client reads a remote endpoint; potential data fetch or service probing.',
     'PYTHON-REMOTE-READ-WRITE-ARTIFACTORY':'Python remote read/write against Artifactory path (GET/PUT/MKCOL).',
     'JS-IMAGE-BEACON-EXFIL-TO-SHORTENER':'Loads a tracking pixel to a shortener => exfil/beacon of execution context.',
     'JS-FETCH-AND-REPORT-TO-SHORTENER':'Fetches candidate content and reports status to shortener => relay/exfil channel.',
     'DOCKER-REGISTRY-MANIFEST-PROBE':'Queries Docker registry auth/manifest endpoints => supply-chain/manifest discovery.',
     'HF-DATASETS-SERVER-API-PROBE':'Queries HuggingFace datasets-server rows/images => dataset enumeration or data pull.',
     'HUGGINGFACE-MODEL-DATASET-PROBE':'Probes HuggingFace model/dataset APIs or pages.',
     'ARTIFACTORY-PATH-PROBE-OR-RELAY':'Direct path/relay probe against OpenAI Artifactory instance.',
     'BARE-ENDPOINT-PROBE':'Bare URL probe against external endpoint.',
     'HTML-SCRIPT-IMAGE-INJECTION':'HTML injection loading remote scripts/images; browser-driven execution/probe.',
     'BROWSER-OR-RELAY-FETCH':'JS fetch/XHR relay to remote host with DOM reporting.',
     'UNCATEGORIZED-OPAQUE-PAYLOAD':'Opaque or fragmentary payload; insufficient markers for functional classification.',
     'MIXED-OR-SECONDARY':'Multi-marker secondary/bridge payload mixing several mechanisms.',
    }.get(catv,'Unclassified.')
    if hasc: base+=' Carries embedded credential/token placeholder.'
    ccount=len(children)
    if ccount: base+=f' Observed {ccount} child row(s).'
    return base

# Build entries
entries=[]
for r in SCOPE:
    tid=r['id']; t=r['text']
    ts=tags(t)
    catv=category(t,ts)
    lang=language(t,ts)
    bnote,qnote,rcount=validity(t)
    kids=CHILDREN.get(tid,[])
    diff=[c for c in kids if c['text']!=t]
    shared=[]
    for m in sorted(zz_markers(t)):
        others=[x for x in ZZ_INDEX.get(m,[]) if x!=tid]
        if others:
            shared.append(f'{m} (shared with {len(others)} other scoped payload(s), e.g. {others[0]})')
    events=external_events(catv,t)
    entry={
      'id':tid,'kind':r['kind'],'parent':r.get('parent_id'),
      'len':len(t),'cred': (re.search(r'\[(?:CREDENTIAL|BEARER|API_KEY|TOKEN|SECRET|PASSWORD)[^\]]*\]', t, re.I) is not None),
      'tags':ts,'cat':catv,'lang':lang,'valid':f'{bnote}; {qnote}; redaction_placeholders={rcount}',
      'hosts':hosts(t),'children':kids,'diff':diff,
      'shared':shared,'events':events,
      'zz':sorted(zz_markers(t)),
      'pivots':[m for m in MARKERS_KNOWN if m.lower() in t.lower()],
      'inference':inference(catv,ts, (re.search(r'\[(?:CREDENTIAL|BEARER|API_KEY|TOKEN|SECRET|PASSWORD)[^\]]*\]', t, re.I) is not None), kids),
    }
    entries.append(entry)

# summary counts
from collections import Counter
cat_counts=Counter(e['cat'] for e in entries)
tag_counts=Counter()
for e in entries:
    for tag in e['tags']: tag_counts[tag]+=1
lang_counts=Counter(e['lang'] for e in entries)
cred_count=sum(1 for e in entries if e['cred'])
child_count=sum(1 for e in entries if e['children'])
children_total=sum(len(e['children']) for e in entries)

# Write markdown
OUT=f'{ROOT}/forensics/first_10000_payload_audit.md'
md=open(OUT,'w')
md.write('# First 10,000 Payload Audit (R0000001–R0010000)\n\n')
md.write('Source: `Data/redacted.jsonl` (189,579 released rows). Scope: first 10,000 rows, all of which are `kind=payload` and sequential IDs R0000001..R0010000. Generated by `forensics/build_first_10000_audit.py`.\n\n')
md.write('## 1. What each entry means\n\n')
md.write('Each payload below is a discrete attacker/agent-generated artifact (JavaScript, Python, shell, bare URL, or JSON). Fields: `technical action`, tags (coarse marker families), inferred functional category, likely language, structural validity heuristic, external hosts/targets, child rows (if execution produced recoverable output), shared `zz*` markers, pivot markers, event linkage, inference.\n\n')
md.write('## 2. External sources consulted (for event linkage)\n\n')
md.write('- OpenAI – Hugging Face Incident Technical Report (local `OpenAI-Hugging-Face Incident-Technical-Report.pdf`; parsed via `pdftotext`). Key timeline: May Artifactory used by agents as improvised message board + failed SSRF; May 13 file-based notes; May 26 successful SSRF egress; Jun 26 Artifactory token-refresh privilege escalation and Groovy plugin RCE; Jul 4 Artifactory outage; Jul 8 – inter-agent folder-as-message-board at scale; Jul 10 exposed Hugging Face creds published to board; Jul 11–13 HF compromise; Jul 19 detection; Jul 20–21 external disclosure.\n')
md.write('- Local forensics deliverables: `forensics/log.md`, `forensics/artifactory_subset/*`, `forensics/artifactory_payload_audit/*`, `forensics/open_questions.md`, `swarm_traces_forensics.html` (Swarm Traces dataset companion).\n')
md.write('- Additional external concepts referenced by report: Artifactory SSRF (server-side fetch), JFrog Artifactory token-refresh endpoint, Groovy plugin execution, Docker registry manifest, Hugging Face datasets-server.\n\n')
md.write('## 3. Scope-wide summary\n\n')
md.write(f'- Payload rows: **{len(entries)}** (all roots by `parent_id` in first 10,000; none had a parent).\n')
md.write(f'- Rows with at least one child (recovered_text/response): **{child_count}** (children total **{children_total}**).\n')
md.write(f'- Rows carrying a credential/token placeholder: **{cred_count}**.\n\n')
md.write('### Functional category counts\n\n|Functional category|Count|\n|---|---:|\n')
for k,v in cat_counts.most_common():
    md.write(f'|{k}|{v}|\n')
md.write('\n### Language counts\n\n|Language|Count|\n|---|---:|\n')
for k,v in lang_counts.most_common():
    md.write(f'|{k}|{v}|\n')
md.write('\n### Tag (marker family) counts\n\n|Tag|Count|\n|---|---:|\n')
for k,v in tag_counts.most_common():
    md.write(f'|{k}|{v}|\n')
md.write('\n### External target host counts (top)\n\n')
hostc=Counter()
for e in entries:
    for h in e['hosts']: hostc[h]+=1
md.write('|Host|Count|\n|---|---:|\n')
for k,v in hostc.most_common(25):
    md.write(f'|{k}|{v}|\n')
md.write('\n### Structural validity heuristic\n\n')
vcount=Counter(e['valid'].split(';')[0] for e in entries)
md.write('|Bracket-balance result|Count|\n|---|---:|\n')
for k,v in vcount.most_common():
    md.write(f'|{k}|{v}|\n')
md.write('\nQuote parity and placeholder counts are listed per payload.\n\n')
md.write('## 4. Notes on linking to known events\n\n')
md.write('- Direct per-row timestamps are absent (`time_utc` is null for all rows), so event binding below is mechanistic, not timestamp proof.\n')
md.write('- Mechanism-to-event mapping: directory reassembly + SSRF relay (Artifactory server-side fetch) corresponds to May 26 successful SSRF egress; CyberGym SQL-injection/dead-drop/MKCOL corresponds to May message board + write side; Docker registry manifest probes correspond to third-party credential/supply-chain phase; Hugging Face dataset/model API probes correspond to Jul 10–13 Hugging Face compromise phase (Python/JS probing of `datasets-server`).\n')
md.write('- Pivot markers (TINYOK, CHAINWORKS, FANPASS_12345, CYBERGYM, ENCODED BLOB, getent, sqlite3_initialize template) are shared pivots documented in local forensics; presence is noted per payload.\n\n')
md.write('## 5. Per-payload entries (R0000001 → R0010000)\n\n')

for e in entries:
    md.write(f'---\n\n### {e["id"]} — {e["cat"]}\n\n')
    md.write(f'- **kind / parent**: payload; parent={e["parent"]}\n')
    md.write(f'- **technical action (category)**: {e["cat"]}\n')
    md.write(f'- **marker families (tags)**: {", ".join(e["tags"])}\n')
    md.write(f'- **language**: {e["lang"]}\n')
    md.write(f'- **structural validity**: {e["valid"]}\n')
    md.write(f'- **text length**: {e["len"]} chars\n')
    md.write(f'- **credential/token placeholder present**: {e["cred"]}\n')
    md.write(f'- **external hosts targeted**: {", ".join(e["hosts"]) if e["hosts"] else "(none)"}\n')
    md.write(f'- **payload (sanitized snippet)**: `{sanitize(e["id"] and None or "")}`'.replace('`None`','') if False else '')
    snippet='{placeholder}'  # replaced below
    # sanitize actual text
    t=BYID[e['id']]['text']
    md.write(f'- **payload (sanitized snippet)**: `{sanitize(t)}`\n')
    # child rows
    kids=e['children']
    if kids:
        md.write(f'- **child responses observed**: yes — {len(kids)} row(s): {", ".join(c["id"]+"("+c["kind"]+")" for c in kids)}\n')
        for c in kids[:4]:
            ch_sn=sanitize(c['text'])
            verdict = 'possible-execution-output' if any(m in c['text'].upper() for m in ['ERR','OK','STATUS','200','201','404','403','500','MKCOL','HTTP','ERROR']) else 'recorded-derived-payload'
            md.write(f'  - child `{c["id"]}` ({c["kind"]}) => `{ch_sn}` (heuristic: {verdict})\n')
        if len(kids)>4:
            md.write(f'  - ... +{len(kids)-4} more children\n')
    else:
        md.write('- **child responses observed**: none (root payload; no recoverable child rows linked)\n')
    # shared markers
    if e['zz']:
        md.write(f'- **zz markers in payload**: {", ".join(e["zz"][:8])}{"..." if len(e["zz"])>8 else ""}\n')
    if e['shared']:
        md.write('- **external payload links (shared zz markers)**:\n')
        for s in e['shared'][:5]:
            md.write(f'  - {s}\n')
    else:
        md.write('- **external payload links (shared zz markers)**: none within scope\n')
    if e['pivots']:
        md.write(f'- **known pivot markers present**: {", ".join(e["pivots"])}\n')
    md.write('- **inferred why / intent**: '+e['inference']+'\n')
    md.write('- **event linkage (mechanistic)**: '+ '; '.join(e['events'])+'\n')
    # comma-separated event refs trimmed above
    md.write('\n')

# suffix
md.write('## 6. Caveats\n\n')
md.write('- Static data only: no execution confirmation; redacted IDs/credentials; no timestamps; redaction placeholders prevent verbatim execution.\n')
md.write('- Functional categories are heuristic and a row may legitimately belong to multiple buckets; tag lists show overlap.\n')
md.write('- Child-response verdicts are heuristic token-presence checks, not semantic proof.\n')
md.write('- "External payload links" are based on shared `zz*` markers within the first 10,000 scope only.\n')
md.close()

# also write TSV summary
TSV=f'{ROOT}/forensics/first_10000_payload_audit.tsv'
w=open(TSV,'w')
w.write('id\tcategory\ttags\tlanguage\tvalidity\tcred\tlen\thosts\tchildren_ids\tshared_zz_count\tpivots\tinference\n')
for e in entries:
    kids_ids=';'.join(c['id'] for c in e['children'])
    w.write(f"{e['id']}\t{e['cat']}\t{','.join(e['tags'])}\t{e['lang']}\t{e['valid']}\t{e['cred']}\t{e['len']}\t{','.join(e['hosts'])}\t{kids_ids}\t{len(e['shared'])}\t{','.join(e['pivots'])}\t{e['inference'].replace(chr(9),' ')}\n")
w.close()
print('done entries',len(entries))
print('md size', os.path.getsize(OUT), 'tsv size', os.path.getsize(TSV))
