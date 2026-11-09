#!/usr/bin/env python3
import collections, hashlib, json, pathlib, re

ROOT=pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC=ROOT/"Data"/"redacted_filtered.jsonl"
PROJ=ROOT/"forensics"/"projections"
PROJ.mkdir(parents=True,exist_ok=True)
TMP=ROOT/"forensics"/"run_2026"
rows=[json.loads(l) for l in SRC.open() if l.strip()]
by_id={r["id"]:r for r in rows}
positions={r["id"]:i for i,r in enumerate(rows)}
def canon(text):
    text=text.replace("\r\n","\n").replace("\r","\n").lower()
    text=re.sub(r"(?<!\w)hugging\s+face(?!\w)","huggingface",text)
    text=re.sub(r"(?<!\w)hf(?!\w)","huggingface",text)
    text=re.sub(r"\s+"," ",text).strip()
    return text
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def is_generic(m):
    low=m.lower()
    return (m in ("[ENCODED BLOB]","[REDACTED SENSITIVE CONTENT]","[REDACTED REPOSITORY]","[REDACTED PRIVATE HOST]")) or m.startswith("[REDACTED:runtime_identifier")
def is_syntactic(m):
    return bool(re.fullmatch(r"\[[0-9]+\]",m)) or m in ("['token']","[i]","[k]","[rstatus]","[key]")
def is_endpoint(m):
    low=m.lower()
    return m.startswith(("[PROXY ","[SHORTENER URL ","[SERVICE HOST ","[IP ADDRESS ","[REDACTED:destination:","[REDACTED:network_address:","[REDACTED PRIVATE HOST]")) or low.startswith("[redacted:destination:") or low.startswith("http://")
def row_markers(text): return sorted(set(re.findall(r"\[[^\]]{1,200}\]",text)))
def canonicalize_edge(edge):
    return {
        "source": edge["source_id"],
        "dest": edge["destination_id"],
        "edge_class": edge["edge_class"],
        "edge_sub_class": {
            "source_id": edge["source_id"],
            "destination_id": edge["destination_id"],
            "source": edge.get("source"),
            "target": edge.get("target"),
            "trigger": edge.get("trigger"),
            "distance": edge.get("distance"),
            "direction": edge.get("direction", "symmetric"),
        },
    }

def write_edge(f, edge):
    f.write(json.dumps(canonicalize_edge(edge),separators=(",",":"),ensure_ascii=False)+"\n")

# Class files
files={
 "EXACT_BODY": open(PROJ/"exact_body.ndjson","w"),
 "NORMALIZED_REPLAY": open(PROJ/"normalized_replay.ndjson","w"),
 "NEAR_BODY_D1": open(PROJ/"near_body_d1.ndjson","w"),
 "NEAR_BODY_D2": open(PROJ/"near_body_d2.ndjson","w"),
 "NEAR_BODY_D3": open(PROJ/"near_body_d3.ndjson","w"),
 "PARENT_DIRECT": open(PROJ/"parent_direct.ndjson","w"),
 "SAME_PARENT_SIBLING": open(PROJ/"same_parent_sibling.ndjson","w"),
 "MARKER_SAME": open(PROJ/"marker_same.ndjson","w"),
 "MARKER_ENDPOINT": open(PROJ/"marker_endpoint.ndjson","w"),
 "INTENT_SIGNATURE": open(PROJ/"intent_signature.ndjson","w"),
 "PARENT_MUTATION": open(PROJ/"parent_mutation.ndjson","w"),
 "TIMESTAMP_ANCHOR": open(PROJ/"timestamp_anchor.ndjson","w"),
}

# 1 exact
g=collections.defaultdict(list)
for r in rows:
    g[sha(r["text"])].append(r["id"])
for digest,members in g.items():
    if len(members)<2: continue
    members=sorted(members,key=lambda rid:(positions[rid],rid))
    for i in range(len(members)):
        for j in range(i+1,len(members)):
            s,t=members[i],members[j]
            edge={
             "source_id":s,"destination_id":t,"source":s,"target":t,
             "edge_class":"EXACT_BODY","distance":0,
             "trigger":f"text_sha256={digest}",
             "direction": "symmetric",
            }
            write_edge(files["EXACT_BODY"],edge)
files["EXACT_BODY"].close()

# 2 normalized replay
ng=collections.defaultdict(list)
for r in rows:
    ng[sha(canon(r["text"]))].append(r)
for _,members in ng.items():
    if len(members)<2: continue
    raw=collections.defaultdict(list)
    for r in members:
        raw[sha(r["text"])].append(r)
    if len(raw)<2: continue
    digest=sha(canon(members[0]["text"]))
    canonical=digest
    reps=[]
    for rh,rs in raw.items():
        for r in rs:
            reps.append((rh,r["id"]))
    # cross pairs
    for i in range(len(reps)):
        for j in range(i+1,len(reps)):
            if reps[i][0]==reps[j][0]: continue
            s,t=reps[i][1],reps[j][1]
            edge={
             "source_id":s,"destination_id":t,"source":s,"target":t,
             "edge_class":"NORMALIZED_REPLAY","distance":None,
             "trigger":f"canonical_sha256={canonical}; raw_class_count={len(raw)}",
             "direction": "symmetric",
            }
            write_edge(files["NORMALIZED_REPLAY"],edge)
files["NORMALIZED_REPLAY"].close()

# 3 near body from candidates (SKIPPED HERE if candidate file unavailable; run later)
for k in ("NEAR_BODY_D1","NEAR_BODY_D2","NEAR_BODY_D3"):
    files[k].close()

# 4 parent direct
for r in rows:
    p=r.get("parent_id")
    if p and p in by_id:
        edge={
         "source_id":p,"destination_id":r["id"],"source":p,"target":r["id"],
         "edge_class":"PARENT_DIRECT","distance":None,
         "trigger":f"stored parent_id={p}",
         "direction": "directed",
        }
        write_edge(files["PARENT_DIRECT"],edge)
files["PARENT_DIRECT"].close()

# 5 same parent sibling
groups_by_parent=collections.defaultdict(list)
for r in rows:
    p=r.get("parent_id")
    if p and p in by_id:
        groups_by_parent[p].append(r["id"])
for p,members in groups_by_parent.items():
    if len(members)<2: continue
    members=sorted(members,key=lambda rid:(positions[rid],rid))
    for i in range(len(members)):
        for j in range(i+1,len(members)):
            s,t=members[i],members[j]
            edge={
             "source_id":s,"destination_id":t,"source":s,"target":t,
             "edge_class":"SAME_PARENT_SIBLING","distance":None,
             "trigger":f"shared_parent={p}",
             "direction": "symmetric",
            }
            write_edge(files["SAME_PARENT_SIBLING"],edge)
files["SAME_PARENT_SIBLING"].close()

# 6 markers
marker_groups=collections.defaultdict(list)
for r in rows:
    for m in row_markers(r["text"]):
        marker_groups[m].append(r["id"])
for marker,members in marker_groups.items():
    if len(members)<2: continue
    if is_generic(marker) or is_syntactic(marker): 
        continue
    cls="MARKER_ENDPOINT" if is_endpoint(marker) else "MARKER_SAME"
    members=sorted(members,key=lambda rid:(positions[rid],rid))
    for left,right in zip(members,members[1:]):
        s,t=left,right
        edge={
         "source_id":s,"destination_id":t,"source":s,"target":t,
         "edge_class":cls,"distance":None,
         "trigger":marker,
         "direction": "symmetric",
        }
        write_edge(files[cls],edge)
files["MARKER_SAME"].close()
files["MARKER_ENDPOINT"].close()

# 7 intent signature: operation-level signatures (multiple levels, adjacent group chain)
def extract_function_name(text):
    # Robust to missing function_name, escaped JSON quotes, JS vs Python syntax.
    m=re.search(r'function_name\\?["\x27]\s*[:=]\s*\\?["\x27]([A-Za-z0-9_]{2,})\\?["\x27]', text)
    if not m:
        m=re.search(r'function_name\s*[:=]\s*["\x27]?([A-Za-z0-9_]{2,})["\x27]?', text)
        if not m:
            return None
    val=m.group(1)
    low=val.lower()
    if low.startswith("[redacted") or low.startswith("[encoded") or low in ("token","key","i","rstatus"):
        return None
    return val

def is_endpoint_marker(marker):
    low=marker.lower()
    return marker.startswith(("[PROXY ","[SHORTENER URL ","[SERVICE HOST ","[IP ADDRESS ","[REDACTED:destination:","[REDACTED:network_address:","[REDACTED PRIVATE HOST]")) or low.startswith("[redacted:destination:") or low.startswith("http://")

def classify_coarse_archetype(text):
    low=text.lower()
    if "auth.docker.io" in low or "registry-1.docker.io" in low:
        return "registry_authentication"
    if "curl" in low or "gcs" in low or "storage.googleapis" in low:
        return "curl_gcs_access"
    if "urllib" in low:
        return "urllib_dead_drop"
    if ("atob(" in low or "base64" in low) and ("fetch(" in low or "xmlhttprequest" in low or "post" in low):
        return "base64_atob_decode_and_post"
    if "sqlite3" in low or ("file_path" in low and ";" in text):
        return "sql_command_staging"
    if "xmlhttprequest" in low:
        return "xmlhttprequest"
    if "fetch(" in low:
        return "fetch_initiated_request"
    if "mkcol" in low or "github-remote" in low:
        return "artifactory_dead_drop_write"
    if "manifests/latest" in low or ("v2/" in low and "pushblob" in low):
        return "docker_registry_push"
    if "pushblob" in low or "socket,ssl" in low:
        return "python_registry_push"
    if 'decompressionstream("gzip")' in low or ("eval(" in low and "atob" in low):
        return "js_directory_reassemble_eval"
    if "shortener url" in low or "proxy 4 url" in low or "proxy 5 url" in low:
        return "js_fetch_and_report_shortener"
    if "<iframe" in low or "<img" in low or "document.body.append(i)" in low:
        return "html_script_image_injection"
    if "tar member" in low or "encoded blob" in low:
        return "tar_blob_derived_archive"
    if "zz" in low and ("fetch(" in low or "xmlhttprequest" in low):
        return "artifactory_path_probe_or_relay"
    if "\u2500\u2500 stage" in text or "stage:" in low:
        return "stage_batch_operation"
    if text.lstrip().lower().startswith("<!doctype"):
        return "html_document_reassembly"
    if "datasets-server.huggingface.co" in low or "huggingface.co/api/datasets" in low or "huggingface.co/datasets/" in low:
        return "huggingface_dataset_access"
    if "cycler.__init__" in low or "{{ cycler" in low:
        return "cycler_jinja_injection"
    if text.lower().startswith("i=new image") or "i=new image" in low:
        return "image_beacon"
    return None

def command_syntax_tokens(text):
    low=text.lower()
    tokens=[]
    if "sqlite3_initialize" in low:
        tokens.append("sqlite3_initialize")
    if "sqlite3_open" in low:
        tokens.append("sqlite3_open")
    if re.search(r"""/proc/[^"']*\/status""", low) or "cat /proc" in low:
        tokens.append("proc_status_check")
    if re.search(r"base64\s+-d\b", low):
        tokens.append("base64_d_pipe")
    if "mkcol" in low or "github-remote" in low:
        tokens.append("dead_drop_write")
    if "curl" in low:
        tokens.append("curl_command")
    if "gcs" in low or "storage.googleapis" in low:
        tokens.append("gcs_access")
    if "urllib" in low:
        tokens.append("urllib_call")
    if "atob(" in low:
        tokens.append("atob_decode")
    if ";" in text and ("file_path" in low or "uname -a" in low or "cat /proc" in low):
        tokens.append("shell_command_chain")
    return sorted(set(tokens))

intent_groups=collections.defaultdict(list)
def add_intent(sig, row_id):
    intent_groups[sig].append(row_id)

for r in rows:
    text=r["text"]
    fn=extract_function_name(text)
    arch=classify_coarse_archetype(text)
    endpoints=sorted(set(m for m in row_markers(text) if is_endpoint_marker(m)))
    cmd_tokens=command_syntax_tokens(text)

    # Level 1: coarse operation archetype
    if arch:
        add_intent("coarse_archetype="+arch, r["id"])
    # Level 2: specific destination/endpoint marker co-occurrence
    if endpoints:
        add_intent("endpoint_signature="+";".join(endpoints), r["id"])
    # Level 3: shared function name syntax
    if fn:
        add_intent("function_name="+fn, r["id"])
    # Level 3: shared command/operation syntax
    if cmd_tokens:
        add_intent("command_syntax="+";".join(cmd_tokens), r["id"])
    # Level 4: combined structural signature (function/endpoint/command co-occur)
    if endpoints and cmd_tokens and (fn or arch):
        base=("function_name="+fn) if fn else ("coarse_archetype="+arch)
        add_intent("combined_structural="+base+"|endpoint_signature="+";".join(endpoints)+"|command_syntax="+";".join(cmd_tokens), r["id"])
    # Fallback for rows with no recognizable operation or markers: exact normalized skeleton
    if not (arch or endpoints or fn or cmd_tokens):
        add_intent("operation_skeleton="+canon(text)[:120], r["id"])
# only groups with at least 2 rows and non-trivial signature length >= 20
for sig,members in intent_groups.items():
    if len(members)<2: continue
    if len(sig)<20: continue
    members=sorted(members,key=lambda rid:(positions[rid],rid))
    for left,right in zip(members,members[1:]):
        s,t=left,right
        edge={
         "source_id":s,"destination_id":t,"source":s,"target":t,
         "edge_class":"INTENT_SIGNATURE","distance":None,
         "trigger":sig,
         "direction": "symmetric",
        }
        write_edge(files["INTENT_SIGNATURE"],edge)
files["INTENT_SIGNATURE"].close()


# 8 parent mutation
for r in rows:
    p=r.get("parent_id")
    if not p or p not in by_id: continue
    pt=by_id[p]["text"]; ct=r["text"]
    if pt==ct: continue
    plen=len(pt); clen=len(ct)
    kind="addition" if ct.startswith(pt) else ("truncation" if pt.startswith(ct) else "substitution")
    edge={
     "source_id":p,"destination_id":r["id"],"source":p,"target":r["id"],
     "edge_class":"PARENT_MUTATION","distance":None,
     "trigger":f"parent_child_text_differs:{kind}",
     "direction": "directed",
    }
    write_edge(files["PARENT_MUTATION"],edge)
files["PARENT_MUTATION"].close()

# 9 timestamp anchor (direct temporal edges)
temporal_path=pathlib.Path("/Users/id19/scratchpad/temporal_subset/direct_temporal_edges.jsonl")
if temporal_path.exists():
    for line in temporal_path.open():
        if not line.strip(): continue
        o=json.loads(line)
        # only edges whose endpoints are samples
        if o["source"] not in by_id or o["target"] not in by_id: 
            continue
        d=int(o.get("levenshtein_distance") or 0) if o.get("levenshtein_distance") is not None else None
        edge={
         "source_id":o["source"],"destination_id":o["target"],"source":o["source"],"target":o["target"],
         "edge_class":"TIMESTAMP_ANCHOR","distance":d,
         "trigger":f"{o['edge_type']}: {o.get('proof','')}",
         "direction": "directed",
        }
        write_edge(files["TIMESTAMP_ANCHOR"],edge)
files["TIMESTAMP_ANCHOR"].close()

print("phase1 projections written to", PROJ)
