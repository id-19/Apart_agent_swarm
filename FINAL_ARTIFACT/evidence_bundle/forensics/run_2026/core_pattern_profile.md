# Core Pattern Profile

Scope: read-only analysis of the local core graph and filtered sample corpus.

- Graph rows: `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/core/core_rows.ndjson`
- Graph edges: `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/core/core_edges.ndjson`
- Filtered source samples: `/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted_filtered.jsonl`
- Near-body statistics: `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/near_distance_stats.json`
- Pattern registry: `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/core_pattern_registry.tsv`
- Adversarial disproof set: `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/core_pattern_disproof_set.json`

No database, source file, or row data was modified. Interpretations below are limited to observed structural and marker evidence.

## 1. Dataset And Graph Summary

| Item | Value |
|---|---:|
| Filtered sample rows | 187,242 |
| Distinct sample IDs | 187,242 |
| Row kinds | payload 90,537; recovered_text 73,859; response 22,846 |
| Rows with stored parent | 59,313 |
| Unique parent IDs | 25,846 |
| Exact raw-body groups | 18,999 groups / 42,470 rows |
| Normalized replay groups | 1,794 groups / 6,611 rows |
| Distinct marker spellings | 228,450 |
| Marker spellings repeated | 79,653 |
| Core graph nodes with at least one edge | 169,729 |
| Nontrivial connected components | 2,061 |
| Singleton nodes | 17,514 |
| Total connected components | 19,575 |
| Largest connected component | 153,562 nodes |

## 2. Edge Class Inventory

| Edge class | Edges | Approx. endpoints | Components | Pattern meaning |
|---|---:|---:|---:|---|
| EXACT_BODY | 23,471 | 42,470 | 18,999 | Identical raw `text_sha256` across samples |
| NORMALIZED_REPLAY | 1,826 | 3,620 | 1,794 | Same canonical hash but different raw bodies |
| MARKER_SAME | 267,062 | 140,481 | 3,058 | Two samples share one marker spelling |
| MARKER_ENDPOINT | 121,104 | 103,993 | 7,697 | A trigger is a marker substring/endpoint in both samples |
| PARENT_DIRECT | 59,313 | 85,160 | 25,847 | Stored `parent_id` points from child sample to parent sample |
| SAME_PARENT_SIBLING | 33,466 | 43,102 | 9,636 | Samples share a stored parent ID |

Total edges: 506,242.

## 3. Deterministic Pattern Registry

The registry samples 10% of every edge class. The companion JSON stores 5% adversarial disproof edges. Both use the same seed and ordered edge-class traversal as the core verifier.

| Edge class | Total edges | 10% registry rows | 5% disproof rows |
|---|---:|---:|---:|
| EXACT_BODY | 23,471 | 2,347 | 1,173 |
| MARKER_ENDPOINT | 121,104 | 12,110 | 6,055 |
| MARKER_SAME | 267,062 | 26,706 | 13,353 |
| NORMALIZED_REPLAY | 1,826 | 182 | 91 |
| PARENT_DIRECT | 59,313 | 5,931 | 2,965 |
| SAME_PARENT_SIBLING | 33,466 | 3,346 | 1,673 |
| Total | 506,242 | 50,622 | 25,310 |

Deterministic edge matching was rechecked on all 25,310 disproof edges: 0 failures. The validation inventory also reports 0 loopholes for the 10% samples.

Newline and tab characters inside trigger strings are escaped as `\n` and `\t` in `core_pattern_registry.tsv` so each edge sample remains one physical TSV record. The JSON disproof set retains the original unescaped trigger strings.

## 4. Top 20 Combined Components And Interpretations

Component membership is from the union of all six edge classes. Sizes and markers are structural summaries, not behavioral classifications.

| Rank | Size | Kinds | Representative hubs (degree) | Triggering markers (count) |
|---:|---:|---|---|---|
| 1 | 153,562 | payload 75,828; response 20,825; recovered_text 56,908 | R0024455 (862), R0036471 (293), R0080310 (158), R0029223 (135), R0036645 (134) | [REDACTED SENSITIVE CONTENT] (15,109), [REDACTED:runtime_identifier] (14,745), [REDACTED:destination:000003] (13,880), [PROXY 4 URL 72] (11,977), [ENCODED BLOB] (11,486) |
| 2 | 9,280 | payload 12; recovered_text 9,268 | R0081078 (5), R0080574 (5), R0080538 (5), R0080160 (5), R0080874 (5) | [SERVICE 14 URL 4] (9,268), [REDACTED:destination:009642] (3) |
| 3 | 253 | payload 252; recovered_text 1 | R0114390 (5), R0187986 (4), R0114248 (2) | [ENCODED BLOB 65714] (253), [REDACTED:opaque_fragment:001349] (2) |
| 4 | 51 | payload 50; recovered_text 1 | R0026695 (3), R0070508 (3), R0012239 (2) | [Uint8Array.from(atob(...reverse...))] (51), [ENCODED BLOB 5107] (1) |
| 5 | 44 | payload 1; response 22; recovered_text 21 | R0117640 (55), R0154675 (35), R0172746 (34) | [REDACTED:destination:026091] (5), [REDACTED:destination:026092] (5), ... |
| 6 | 42 | payload 14; response 14; recovered_text 14 | R0059020 (6), R0059186 (6), R0057485 (6) | [REDACTED:destination:003436] (42), [REDACTED:query_value:001004] (3) |
| 7 | 32 | recovered_text 32 | R0092027 (4), R0095076 (3), R0095143 (3) | [REDACTED:destination:013669] (15), [REDACTED:destination:011989] (10) |
| 8 | 30 | payload 12; recovered_text 18 | R0053167 (9), R0052877 (6), R0078535 (5) | [REDACTED:destination:008415] (12), [REDACTED:destination:008416] (8), [REDACTED:secret_key:000291] (4) |
| 9 | 27 | payload 15; recovered_text 12 | R0124335 (4), R0121027 (4), R0121804 (4) | [SERVICE 25 URL 431] (15), [REDACTED:destination:027403] (2) |
| 10 | 26 | recovered_text 26 | R0103256 (4), R0103309 (4), R0105462 (4) | [REDACTED:URL_CHAIN] (26) |
| 11 | 24 | payload 8; response 8; recovered_text 8 | R0055417 (6), R0055419 (6), R0055483 (6) | [REDACTED:destination:001380] (24), [REDACTED:query_value:000329] (3) |
| 12 | 20 | payload 6; response 7; recovered_text 7 | R0056713 (6), R0056847 (6), R0056239 (6) | [REDACTED:destination:001570] (20), [REDACTED:query_value:000364] (3) |
| 13 | 19 | payload 9; response 1; recovered_text 9 | R0126311 (6), R0126512 (6), R0159263 (5) | [SHORTENER URL 151986] (15), [REDACTED:destination:028324] (8) |
| 14 | 18 | payload 6; response 6; recovered_text 6 | R0057118 (6), R0057115 (6), R0057119 (6) | [REDACTED:destination:002964] (18), [REDACTED:query_value:000882] (3) |
| 15 | 18 | payload 6; response 6; recovered_text 6 | R0057135 (6), R0057132 (6), R0057134 (6) | [REDACTED:query_value:000889] (18), [REDACTED:destination:002977] (3) |
| 16 | 18 | payload 10; recovered_text 8 | R0081157 (3), R0096806 (3), R0081201 (3) | [SERVICE 121 URL 19] (18) |
| 17 | 15 | payload 5; response 5; recovered_text 5 | R0055643 (4), R0055642 (4), R0055644 (4) | [REDACTED:query_value:000405] (15) |
| 18 | 15 | payload 5; response 5; recovered_text 5 | R0057126 (6), R0060836 (6), R0060831 (6) | [REDACTED:query_value:000888] (15), [REDACTED:destination:002973] (3) |
| 19 | 15 | payload 5; response 5; recovered_text 5 | R0058144 (6), R0057989 (6), R0057454 (6) | [REDACTED:destination:003295] (15), [REDACTED:query_value:000988] (3) |
| 20 | 15 | payload 5; response 5; recovered_text 5 | R0056765 (6), R0056817 (6), R0056815 (6) | [REDACTED:destination:002711] (15), [REDACTED:query_value:000766] (3) |

Plain-English interpretations:

1. Component 1 is a dense, corpus-spanning linkage class rather than one artifact chain. It connects most payload, response, and recovered_text samples through ubiquitous markers such as sensitive-content, runtime IDs, common destinations, proxy path 4/72, encoded blobs, service endpoints, shortener host 1, and credential 1. Its parent hubs are bridge nodes with very high degree. It is best interpreted as a shared global pool produced by cross-linking markers and proxy endpoints, not as a single parent-child process.
2. Component 2 is a large recovered_text-only field of sibling samples that share `[SERVICE 14 URL 4]`. Nearly every member is recovered_text, and the destinations are distinct numbered generics, so it reads as a recovery/render family bound by one service marker rather than repeated raw text.
3. Component 3 is a payload cluster bound by one opaque carrier marker repeated in all 253 members. It is a near-uniform content template with almost no kind mixing.
4. Component 4 is a small payload cluster linked by a reverse-atob template and a single encoded-blob ID. It represents one obfuscation/render routine propagated to multiple sample wrappers.
5. Component 5 mixes payload, response, and recovered_text around repeated destination IDs 026091 onward. It is a response/recovery triad family rather than one body.
6. Component 6 is a perfectly balanced 14/14/14 triad family keyed by destination 003436 and query values. The balance suggests paired request, response, and recovered forms for the same destination.
7. Component 7 is recovered_text-only nodes keyed by overlapping destination IDs. Its links are by destination marker, especially 013669 and 011989.
8. Component 8 is a payload/recovered_text cluster with secret-key and source-identifier material. It links several wrappers around common destination IDs, with a single secret key marker repeated four times.
9. Component 9 is a payload/recovered_text family bound by service endpoint URL 25/431 and destination IDs. It represents repeated endpoint use across sample wrappers.
10. Component 10 is a recovered_text-only chain keyed by `[REDACTED:URL_CHAIN]`. This is a short chain/pivot marker rather than a shared common service.
11. Component 11 is an 8/8/8 triad family with one destination repeated in all 24 members and query values split among them. It resembles paired request/response/recovery for a single destination.
12. Component 12 is a mixed payload/response/recovered_text family with one repeated destination and intermittent query-value markers. It indicates row-level reuse around destination 001570.
13. Component 13 combines shortener URL markers and destination IDs across payload, one response, and recovered_text. It is a shortener-to-destination pivot chain.
14. Component 14 is a balanced triad family around destination 002964, with query-value markers spread across members.
15. Component 15 is a complementary balanced triad family: query values are present in all 18 members while the repeated destination appears in only three members per subset.
16. Component 16 is a service-endpoint family keyed by `[SERVICE 121 URL 19]`. It links payload and recovered_text samples without strong destination markers.
17. Component 17 is a small triad family tied to one query-value marker, with all other markers shard-like.
18. Component 18 is a small triad family keyed by query value 000888 and destination shards.
19. Component 19 is a small triad family keyed by destination 003295 and query shards.
20. Component 20 is a small triad family keyed by destination 002711 and query shards.

The dominant combined pattern is: global component 1 is held together by recurring generic markers, while smaller components are mostly small destination-keyed triads or single-marker recovered_text/service families.

## 5. Component Structures By Graph Class

### 5.1 EXACT_BODY

- 18,999 components, 42,470 nodes.
- Largest sizes: 120, 103, 86, 83, 65, 55, 54, 51, 45, 43.
- Marker patterns: exact shared body templates include `[ORIGINAL ENCODED CONTENT-RETRIEVAL TEST...]`, `[SHORTENER URL 18537]`, and mixed service/credential templates such as `[0]`, `[1]`, `[CREDENTIAL 1]`, destination, runtime identifier, service URL, and `[r.status,t]`.
- Interpretation: EXACT_BODY identifies repeated literal payload bodies or rendering wrappers. The 120-row cluster is an identical opaque carrier template, while 86-row clusters are mixed service/credential templates.

### 5.2 NORMALIZED_REPLAY

- 1,794 components, 3,620 nodes.
- Largest sizes: 8, 8, 7, 7, 4, 4, 3, 3, 3, 3.
- Member rows are usually payload-only and link rows whose raw bodies differ while canonical body hash agrees.
- Interpretation: normalized replay separates superficially different wrappers that collapse to the same canonical payload after redaction/normalization. Components are deliberately small compared with raw-body matches.

### 5.3 PARENT_DIRECT

- 25,847 components, 85,160 nodes.
- Largest parent-centered components: 859, 271, 135, 109, 103, 89, 85, 71, 71, 71, ...
- Hub pattern: each large component is a star with one payload root ID as parent and many response/recovered_text children. The two largest are R0024455 with 858 children and R0036471 with 270 children.
- Repeated markers inside parent components include sensitive content, cookie value, shortener 1, encoded base64 blocks, proxy path 4/72, AWS auth values, shortener 3, and ordered shortener URL lists.
- Interpretation: stored parent IDs represent producer-to-derived-fragment chains. A root payload is linked to a response and recovered_text sibling set, making parent chains the main row-level derivation path.

### 5.4 SAME_PARENT_SIBLING

- 9,636 components, 43,102 nodes.
- Sizes track PARENT_DIRECT (858, 270, 134, 108, 102, ...).
- Members are response/recovered_text rows sharing one parent root; parents themselves are not included.
- Interpretation: SAME_PARENT_SIBLING captures sibling derivations generated from the same payload root. Compared with PARENT_DIRECT, it removes the root and preserves the peer group.

### 5.5 MARKER_SAME

- 3,058 components, 140,481 nodes.
- Largest: 121,571, 9,268, 253, 120, 87, 69, 66, 56, 51, 36.
- Broad recurring markers include sensitive content, runtime identifiers, encoded blobs, service URL 209, proxy path 4/72, shortener-1 host, and credential 1.
- Smaller 9,268-row family is almost entirely recovered_text sharing `[SERVICE 14 URL 4]`.
- Global component result: 121,571 nodes connect through overlapping marker spellings.
- Interpretation: MARKER_SAME is the widest union mechanism; generic shared tokens bridge otherwise separate body, destination, service, and proxy markers.

### 5.6 MARKER_ENDPOINT

- 7,697 components, 103,993 nodes.
- Largest: 79,691, 744, 268, 235, 136, 102, ...
- Endpoint-style markers include destination 000003, proxy 4/72, encoded blobs, sensitive content, runtime identifiers, shortener-1 host, and service host 1.
- Second-largest family (744 rows) mixes payload, response, and recovered_text around service 25 and destination 024756 markers.
- Interpretation: MARKER_ENDPOINT captures cases where the trigger appears inside the sample body or embedded JSON rather than as an exact equality relation. It pulls together service-endpoint and proxy families.

## 6. Near-Body Component Structures

Near-body relationships are candidate-level Levenshtein results, not verified edges. Counts below are from `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/near_distance_stats.json`.

| Distance cutoff | Candidate edges | Sample nodes | Components | Largest sizes | Components >100 |
|---|---:|---:|---:|---|---:|
| Exactly 0 | 66,592 | 42,494 | 18,964 | 120, 103, 86, 83, 65 | 2 |
| <=1 | 367,859 | 74,612 | 13,280 | 6,376, 6,209, 3,080, 3,036, 1,617 | 47 |
| <=2 | 3,182,877 | 96,209 | 13,310 | 9,335, 9,198, 3,430, 3,173, 2,581 | 65 |
| <=3 | 18,359,221 | 108,245 | 13,955 | 9,462, 9,212, 3,456, 3,259, 2,655 | 82 |

Interpretation: exact bodies alone remain decomposed into many small components. A single-edit tolerance connects five orders of magnitude more candidate edges and merges components into a handful of multi-thousand-node families. By distance 3, most observed samples belong to a giant 9,462-node cluster. A reliable near-body classification should therefore use tight distance 0/1 evidence plus endpoint provenance, since distance 2-3 comparisons collapse unrelated families.

## 7. Likely Data-Flow And Pivot Patterns

### 7.1 Broad Common Markers And Archives

Most frequent repeated markers:

| Marker | Rows |
|---|---:|
| [REDACTED SENSITIVE CONTENT] | 15,109 |
| [REDACTED:runtime_identifier] | 14,745 |
| [REDACTED:destination:000003] | 13,880 |
| [PROXY 4 URL 72] | 11,977 |
| [ENCODED BLOB] | 11,486 |
| [SERVICE 3 URL 209] | 11,229 |
| [SERVICE 14 URL 4] | 9,268 |
| [REDACTED:opaque_marker_tail:000008] | 7,165 |
| [SHORTENER-1-HOST] | 6,314 |
| [CREDENTIAL 1] | 6,080 |
| [SERVICE HOST 1] | 5,952 |
| [REDACTED:destination:000002] | 5,663 |

Archives and chain markers appear but are small: `[REDACTED:URL_CHAIN]` occurs in 26 rows and all 26 rows form combined component 10; archive-labeled markers appear in fewer than 100 marker strings. Common marker density, rather than archive labels, is the structural pivot in this corpus.

### 7.2 Proxy Paths

Proxy markers are commonly structured as `[PROXY <n> URL <m>]`.

| Proxy marker | Rows |
|---|---:|
| [PROXY 4 URL 72] | 11,977 |
| [PROXY 4 URL 1] | 1,548 |
| [PROXY 4 URL 325] | 1,316 |
| [PROXY 5 URL 1] | 924 |
| [PROXY 37 URL 26] | 141 |
| [PROXY 4 URL 8] | 130-scale variants |

Proxy 4 markers, especially URL 72, are among the largest single common triggers across MARKER_ENDPOINT and combined component 1. Component 5 (44 rows) shows rows being grouped via proxy 4/72 alongside AWS auth values and shortener 3. The proxy marker therefore acts as a broad hub in the giant component and as an endpoint marker in several smaller proxy-linked families.

### 7.3 Shortener Chains

Shortener markers use host/URL/code forms:

| Shortener form | Representative evidence |
|---|---|
| [SHORTENER-1-HOST] | 6,314 rows; appears in giant combined component 1 |
| [SHORTENER-3] / [SHORTENER-3-HOST] | appears in proxy/shortener family component 5 and PARENT_DIRECT component 6 |
| [SHORTENER URL <n>] | ordered URL lists in parent components 8-14 (70-row clusters) |
| [SHORTENER CODE <n>] | high-cardinality code markers embedded in JSON/query structures |

Shortener behavior evidence includes ordered `SHORTENER URL` lists in parent-centered 70-row components. These are structured as five shortener URLs plus response/recovered_text pairs, suggesting one parent payload fans out to sibling derivations through shortener endpoints. Shortener host markers also bridge the giant global component.

### 7.4 Credential Sets

Credential markers are high cardinality: 2,617 distinct `[CREDENTIAL ...]` spellings and about 40,952 rows across payload, response, and recovered_text positions.

| Evidence | Detail |
|---|---|
| Frequent forms | [CREDENTIAL 1] in 6,080 rows; [CREDENTIAL 169] in 5,056; [CREDENTIAL 170] in 4,738; [CREDENTIAL 220] in 4,646 |
| Broad containment | Credential markers appear in combined component 1 (6,080 rows for credential 1 alone) |
| Parent sets | PARENT_DIRECT component 2 has `[CREDENTIAL 169]` and `(destination, enced blob)` patterns over 132 parent-child derivations |
| Mixed form | `[CREDENTIAL [ENCODED BLOB]` appears as a mixed spelling in 1,917 rows |

Credential placeholders are used as cross-node triggers because repeated constants let rows link through MARKER_SAME and MARKER_ENDPOINT. The evidence supports treating credential markers as structural linkage keys, not as recovered secrets.

### 7.5 Parent Chains

Parent IDs form explicit directional chains:

- 59,313 PARENT_DIRECT edges; 33,466 SAME_PARENT_SIBLING edges.
- 25,846 unique parents, of which 25,846 are stored IDs and 1 is outside the row index.
- Large parent stars: R0024455 (858 children), R0036471 (270), R0080310 (134), R0036645 (108), R0049534 (102), R0050038 (88), R0017410 (84), and many 70-row shortener URL stars.
- Parent stores one root payload and paired response/recovered_text children. The matching SAME_PARENT_SIBLING component shows the same sizes with the root removed.
- Interpretation: the strongest row-level derivation evidence in this corpus is parent ID structure, not body similarity or marker sharing. It is also the cleanest support for producer-to-derived-fragment chains.

## 8. Top 100 Components By Class

Top 100 components by each graph class were computed for the combined graph and for each edge class. The per-class top component sizes and representative hubs are as follows:

| Class | Component count | Top 10 sizes |
|---|---:|---|
| Combined | 2,061 nontrivial | 153562, 9280, 253, 51, 44, 42, 32, 30, 27, 26 |
| EXACT_BODY | 18,999 | 120, 103, 86, 83, 65, 55, 54, 51, 45, 43 |
| NORMALIZED_REPLAY | 1,794 | 8, 8, 7, 7, 4, 4, 3, 3, 3, 3 |
| PARENT_DIRECT | 25,847 | 859, 271, 135, 109, 103, 89, 85, 71, 71, 71 |
| SAME_PARENT_SIBLING | 9,636 | 858, 270, 134, 108, 102, 88, 84, 70, 70, 70 |
| MARKER_SAME | 3,058 | 121571, 9268, 253, 120, 87, 69, 66, 56, 51, 36 |
| MARKER_ENDPOINT | 7,697 | 79691, 744, 268, 235, 136, 102, 89, 72, 55, 54 |

Priority ordering for interpretation should put explicit parent edges first, then exact/normalized replay, then marker endpoint, then broad marker-same components. Components containing explicit parent roots plus shortener URL lists have higher chain fidelity than generic global marker components.

## 9. Boundaries And Caveats

- IDs are sequential export IDs and are not known to be chronological.
- Parent links are interpreted as stored producer-to-derived-fragment relationships; the source data does not independently prove conversation order.
- Marker equivalence proves shared token text only; it does not prove semantic intent.
- Near-body links are candidates, not verified edges.
- No behavioral label was assigned beyond the observed structural and marker evidence.
