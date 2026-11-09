# INTENT_SIGNATURE levels report

## Scope

Rebuilt `forensics/run_2026/build_phase1_nonnear.py` INTENT_SIGNATURE emission to use operation-level adjacent signature groups, then rebuilt projections through `forensics/run_2026/build_phase2_unified.py`. Near-body candidate rows were not materialized.

## Signature levels

Trigger text prefixes identify the level. Each group is emitted only once as an adjacent ordered chain (`zip(members, members[1:])`), matching the existing INTENT_SIGNATURE adjacency policy.

1. `coarse_archetype=<label>`: broad exact operation archetype such as `fetch_initiated_request`, `xmlhttprequest`, `base64_atob_decode_and_post`, `urllib_dead_drop`, `registry_authentication`, `curl_gcs_access`, and `sql_command_staging`.
2. `endpoint_signature=<marker set>`: exact co-occurrence set of endpoint/destination/service/proxy markers in a sample.
3. `function_name=<name>`: shared function name syntax, with escaped JSON/JS/Python syntax support.
4. `command_syntax=<token set>`: shared command or operation syntax such as `sqlite3_initialize`, `proc_status_check`, `base64_d_pipe`, and `dead_drop_write`.
5. `combined_structural=...`: co-occurrence of function or archetype, endpoint marker set, and command token set.
6. `operation_skeleton=<120 chars>`: retained fallback only for rows with no recognized archetype, endpoint marker, function name, or command token.

## Edge counts in `forensics/projections/intent_signature.ndjson`

| Signature level | Unique groups (>=2 rows) | Edges |
|---|---:|---:|
| coarse_archetype | 18 | 134,862 |
| endpoint_signature | 15,013 | 66,989 |
| function_name | 11 | 7,169 |
| command_syntax | 103 | 25,990 |
| combined_structural | 2,130 | 9,527 |
| operation_skeleton | 2,303 | 4,515 |
| total | - | 249,052 |

## Top examples

- Coarse: `js_fetch_and_report_shortener` (43,971 rows), `tar_blob_derived_archive` (32,194 rows), `fetch_initiated_request` (15,656 rows).
- Endpoint: `[PROXY 4 URL 72]` (7,617 rows), `[REDACTED:destination:000003]` (5,669 rows), and multi-marker exact sets such as `[PROXY 4 URL 1];[REDACTED:destination:000002]`.
- Function: `sqlite3_initialize` (7,133 edge rows in the largest function-name group).
- Command: `urllib_call` (7,917 rows), `atob_decode` (5,480 rows), and `shell_command_chain;sqlite3_initialize` (2,403 rows).
- Combined: repeated co-occurrence such as registry authentication with `[REDACTED:destination:000058]` and urllib/atob command tokens.

## Repeated marker interactions

Representative repeated interactions include:

- `urllib_dead_drop` with `urllib_call` (7,036 rows) and mixed `shell_command_chain;sqlite3_initialize;urllib_call` (1,451 rows).
- `sql_command_staging` with endpoint `[REDACTED:destination:000002]` and token combination `shell_command_chain;sqlite3_initialize`.
- `registry_authentication` with `[REDACTED:destination:000058]` plus `atob_decode` or `urllib_call`.
- `base64_atob_decode_and_post` with `[REDACTED:destination:000002]` or `[SERVICE HOST 1]` and `atob_decode`.
- `js_fetch_and_report_shortener` with repeated proxy/shortener markers such as `[PROXY 4 URL 72]` and `[PROXY 4 URL 325]`.
- `tar_blob_derived_archive` with `[SERVICE HOST 25]` and `base64_d_pipe` or `atob_decode`.

## False-positive risks

- Archetype labels are structural-text groups, not identities or intent claims; rows sharing a broad token such as `fetch(` may be unrelated routines.
- Exact endpoint marker sets can still represent shared routing or staging infrastructure rather than sample identity.
- Shared `urllib_call`, `atob_decode`, or `shell_command_chain` tokens can connect heterogeneous rows that merely use the same utility.
- Function-name and fallback skeleton groups may include mutation or partial-name variants, so they are candidates for corroboration rather than standalone identity.
- Near-body candidate edges remain unmaterialized by design; this rebuild does not alter that status.

## Reproducibility and artifacts

- Rebuilt `forensics/projections/intent_signature.ndjson` (249,052 edges), `forensics/graph_edges_v2.jsonl` (1,505,515 edges), and `forensics/graph_class_stats.json`.
- `forensics/edge_class_acceptance.json` INTENT_SIGNATURE population was refreshed via `build_phase3_validation.py` (249,052 sampled population, 1,000 samples, 100% acceptance).
- Candidate outputs and archives were preserved.
