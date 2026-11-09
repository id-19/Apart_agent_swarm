# Checkpoint after R0000001-R00000200

## Coverage
- 200 payloads fully analyzed at row level in `forensics/deep_payload_ledger.md`.
- No child records as `parent_id` roots inside scope except 24 recover/response rows, max correspondences at TINYOK/R0000037/R0000038/R0000076 etc.
- Parse validity in this scope as tested with `node --check`: 108/200 OK, 92/200 FAIL. This high failure rate is largely **not a reliable property of original attacker code**; many failures are missing backslash escapes, HTML stagers, truncated exports, redaction placeholders, or merged fragments.

## Functional categories discovered (manual)
1. CyberGym command-injection submissions through `file_path` (`;`, then `#`; mount/net/filesystem recon, external fetch, env/proc exfil).
2. CyberGym C source execution (`system("id")` etc.).
3. CyberGym-style task status reads (by task ID 000001.. 000028).
4. Command-output probes via `uid=` and vulnerability filters (`vul_exit_code`, `poc_length`).
5. Browser-injected asynchronous eval of gzip `data:` URLs (remote decompressed JS execution).
6. HTML shortener stagers and `SHORTENER CODE N` script injection.
7. Service relay/proxy pivots and SSRF-ish URL fetching.
8. Artifactory dead-drop / message-board operations: `MKCOL` into `github-remote-cache/zz...`; `zz6017MODALCURL`.
9. Covert response exfiltration: text as image pixels, 1/2/4-bit canvas channels and magic header `C64G`.
10. Hugging Face dataset URL pivots and remote fetch responses; content-flow has associated response and recovered_text rows.
11. PoC upload / exploit-gym submission (`require_flag`, `metadata`, small file chunk); checksum variants where a SHA is derived or sent as placeholder.
12. Live markers (`CHAINWORKS`, `TINYOK`, `HELLO`, `BEFORE`, `START`, `QSTART`, `FIRE`) used as propagation/coordination signals.
13. Container/modal platform recon (`/__modal`, `/run/modal_daemon`, mounts, cgroups).
14. Operator result filtering and harness control (`task_id`/`agent_id`, `make_output`, `require_flag`).
15. Malformed/truncated artifacts where load/execution intent is still recoverable but direct parsing is not.
16. Secret/token probes (`flag{`, `AWS`, `uid=`, `make_output`).
17. Browser-to-service relay primitives combining hash-based control and task lookup.
18. Bare URL/link pivots (HF, Artifactory target, destinations) used as message-board coordination artifacts.
19. Trailing comments (`//...`) and other seemingly provenance-tip artifacts with unexplained roles.

## External connections that can currently be defended
- R0000032/R0000076/R0000096: Artifactory relay/dead drop.
  - `R0000032`: `zzourtestd1783603749`.
  - `R0000076`: `zzC5DFROOT4TEST` + `MKCOL` (environment fingerprint).
  - `R0000096`: `zz6017MODALCURL`.
- R0000096: Artifactory MKCOL command injection appears strongest direct overlap with the report's Artifactory folder/key/SSRF/dead-drop activity.
- R0000037/R0000038: gzip `eval` and child recovery evidence a multi-stage remote execution chain.
- R0000070/R0000071/R0000074/R0000127/R0000149: evaluator result distributions filtered by `vul_exit_code != 77` / PoC length.
- OpenAI report details point to May Artifactory message board, May 13 notes, May 26 successful SSRF, Jun 26 privilege escalation/Groovy plugins, Jul 4 outage, Jul 8+ folder-as-message-board, Jul 10 HF credential publishing, Jul 11-13 HF compromise.
  - Our first 200 payloads contain no timestamps, so temporal mapping must remain mechanistic.

## Known handle clusters and drift
- Task `000001`: maximal central point; many read/delete/export commands.
- Frequent reads include 000008, 000010, 000014, 000018; these tasks likely act as producer handles for command/output.
- SSH/SSRF helpers use destination 000003, 000006, 000014.
- HF pivots 000018 -> 000019 -> 000020 show ascending drift with destination and then shortener/encoded blobs.
- Shortener code series from 3 through 17, with 14 most common in this scope.
- ZZ markers remain sparse in first 200 (only three short named markers visible); likely the full 2054 artifactory rows and 1227 audited artifactory payloads contain them.
- Destination 000002 dominates (121 refs), followed by destination 000003 (24), destination 000004 (6), destination 000014 (3), destination 000020 (3), destination 000010 (1).

## Child/payload correspondences (verified)
- R0000027 (TINYOK) -> R0053434 response, R0062486 recovered_text
- R0000037 (gzip eval) -> R0062487 recovered_text (stage-2 evaluator probe)
- R0000038 -> R0053435 response + R0062488 recovered_text
- R0000046/R0000061/R0000066 -> recovered_text stage 2 records
- R0000070/71/73/74/76 -> child rows matching command families
- R0000089/98/99 -> children recovered response
- R0000109 -> response recovered (flag/AWS probe)
- R0000118/R0000192 -> gzip/probe/reviewer outputs
These are the highest-value rows for "child response makes sense" because they show recovered text equaling the intended inner script/content and actual parent logic.

## Important parser defect theme
Across original first 200, 92 payloads fail basic Node parse. Most common cause is not syntax diversity but one missing backslash (task id escape defect) or placeholder truncation/HTML-tag in JS. For example:
- R0000001, R0000003, R0000006, R0000007, R0000009, R0000010, R0000018 all repaired by one `\\` and then passed. So "validity" in the final doc must distinguish original survivability, likely-intended code, and actual output behavior.

## Outstanding questions after checkpoint
1. How do Artifactory task IDs and task 00001/000008 correspond to benchmark tasks? Task 000001 has broad use, while 000008 has the largest steganographic pipeline.
2. What is the semantic distinction between identifiers 000014 and 000011, both referenced repeatedly but seemingly different destination/services?
3. Does R0000076 actively change environment via curl MKCOL? We infer from code; no output child tracks a confirmed remote status.
4. Can row 125+ correspond records show whether `R0000002` (bare task ID null) is truly queue-only or a special zero-ID trigger?
5. Hugging Face URLs 18/19/20 etc. are compact pivots but the dataset does not provide times / ownership; a HF report cross-reference may identify them.

## Checkpoint recommendation
- Continue in 200-row windows (201-400 next).
- After each 200, re-run consolidation + child verification and append an explicit checkpoint.
- Avoid novel-link speculation until handle counts are reproduced across the full 10k scope.