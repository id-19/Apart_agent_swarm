# Payload Taxonomy: Iterative Movement Roles

Dataset: `Data/redacted.jsonl` (189,579 rows; read-only).

## Taxonomy Principle

Families are named by **operational movement role**, not by surface language or payload boilerplate. A family says what the payload does in the chain: dead-drop write, registry engine, replayed echo, command-injection recon, etc. Surface text similarities are only supporting signals.

Three cross-cutting grouping dimensions are used:

- Shared referential information: `zz...` namespaces, credential roles, proxy URLs, chunk markers, command templates.
- Same operational functionality: task submission, chunk reassembly, registry push, proxy readback, echo/recovery.
- Provenance/campaign grouping: CyberGym/Modal injection, Artifactory message board, registry supply chain, Hugging Face data access/exfil, relay coordination.

## Deterministic Sampling

- Seeds: `42`, `73`, `2026`.
- Sample size: 250 each.
- Stratified by `kind`: approximately 120 `payload`, 100 `recovered_text`, 30 `response`.
- Three samples are disjoint.
- Sample IDs and helper classifier are retained outside the dataset.

## Final Family Table

| Family | Rows | Share | Defining movement |
|---|---:|---:|---|
| replayed-echo-derived | 98,542 | 51.98% | Replayed or reconstructed observation. |
| shortener-indirection-stager | 27,085 | 14.29% | Loader staging through shortener indirection. |
| opaque-fragment | 20,486 | 10.81% | Fragment without sufficient role signal. |
| hf-data-access-exfil | 14,812 | 7.81% | Hugging Face route read/upload/exfil. |
| other-unresolved | 12,805 | 6.75% | Mixed or underspecified. |
| service-relay-readback | 5,471 | 2.89% | Proxy/service fetch with reported result. |
| directory-assembly-stager | 3,477 | 1.83% | Listing-to-exec reassembly. |
| registry-engine | 2,587 | 1.36% | Docker/OCI registry auth and push. |
| cybergym-shell-injection | 1,658 | 0.87% | CyberGym field converted to shell. |
| steganographic-render-channel | 1,061 | 0.56% | Service output rendered as bitmap. |
| chunked-exfil-bridge | 438 | 0.23% | Numbered browser exfil bridge. |
| data-uri-bootstrap-exec | 354 | 0.19% | gzip data URI bootstrap. |
| dead-drop-write | 347 | 0.18% | MKCOL/cache write. |
| beacon-marker-propagation | 233 | 0.12% | Liveness/coordination marker. |
| command-injection-recon | 180 | 0.09% | CyberGym injection used for recon. |
| network-service-recon | 43 | 0.02% | Name/service resolution recon. |

## Family Tests

1. `MKCOL` present -> `dead-drop-write`.
2. `sqlite3_initialize` plus explicit recon markers -> `command-injection-recon`.
3. `sqlite3_initialize` with `;...;#` but no explicit recon -> `cybergym-shell-injection`.
4. Numbered `href`/chunk reassembly plus `eval`/`exec` -> `directory-assembly-stager`.
5. Docker Registry V2 sequence -> `registry-engine`.
6. `SHORTENER URL`/`SHORTENER CODE`, without stronger write/registry signal -> `shortener-indirection-stager`.
7. `recovered_text` or `response` kind -> `replayed-echo-derived`.

## Anchor Validation

- R0000007 -> `command-injection-recon`.
- R0000096 -> `dead-drop-write`.
- R0000617 -> `registry-engine`. Its 32 children are all `replayed-echo-derived` (17 recovered_text, 15 response).
- R0003357 -> `shortener-indirection-stager`.
- R0053917 -> `replayed-echo-derived`.
- R0063641 -> `replayed-echo-derived`.

R0003357, R0053917, and R0063641 all refer to the same operational marker, `[REDACTED:destination:000003][SHORTENER URL 3550]`, with minor leading-whitespace differences. They form a provenance group through shared referential information, not exact byte equality.

## Ambiguous Cases

- R0000617 is composite: registry engine primary; assembly and CyberGym are secondary roles.
- Rows with `MKCOL` plus HF/registry references remain `dead-drop-write` because the write is the terminal movement.
- Fragments under roughly 120 characters are `opaque-fragment` unless an explicit marker string exists.
- R0000614/R0000650-class payloads keep the role that starts the chain; downstream assembly is secondary.
- Partial samples with 4.4%-10.8% unresolved share are evidence of intentionally underspecified records, not taxonomy failure.

## Summary Statement

The iterative taxonomy reduced the initial 42% unclassified share to 6.75% residual uncertainty, produced 16 operational movement families, validated all required anchors, and remained stable across three disjoint 250-row samples using seeds 42, 73, and 2026.

## Decision Tree

Local interactive tree: `/Users/id19/scratchpad/decision_tree.html`

Attribute tuple (15 booleans):
`replayed_kind`, `mkcol`, `registry_v2`, `data_uri_bootstrap`, `assembly`,
`cybergym`, `recon`, `hf`, `chunk_bridge`, `canvas`, `network_recon`,
`beacon_marker`, `shortener`, `service_relay`, `low_fragment`.

Ordered rules classify one sample into exactly one family; unmatched rows fall into
`other-unresolved`. Each node exposes its accumulated sample count and sample IDs.
