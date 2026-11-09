# Swarm Traces row-level reconstruction final report

## Verdict in one paragraph

No row timestamp is populated (`time_utc` is null for all 187,242 retained rows), and
identifiers, hosts, tokens, directories, and secret values are redacted. The dataset
cannot prove agency, identity, or recovered operational effects. What it does support
is a staged reconstruction of repeated exploit templates, parent-body reuse,
marker-based linkage, and external chronology. A detector could flag probable
coordination only through structural and pivot evidence, not through sender identity,
timestamps, or authorization state.

## Relation families

- `INFO_DEPENDENCY`: 459,448 rows. Union of `EXACT_BODY`, `NORMALIZED_REPLAY`,
  `PARENT_DIRECT`, `SAME_PARENT_SIBLING`, `MARKER_SAME`, and
  `MARKER_ENDPOINT` edges. This relation family describes shared structural
  evidence only, not causation.
- `TIMESTAMP_ANCHOR`: metadata only: 1,882 rows contain timestamp-like cues, of which 1,851 have parseable epochs and 31 are invalid. The complete 1,851-anchor relation matrix was not retained; the grounded temporal evidence set is 945 links and is suitable for advisory ordering claims only.
- `NEAR_BODY`: C++ Levenshtein candidate tiers, without per-source caps.

## Corpus

- Original rows: 189,579
- Rows retained after filtering short/trivial forms: 187,242
- Distinct row IDs: 187,242
- Source SHA-256 (`Data/redacted_filtered.jsonl`):
  `5a048060a8fc2a90246b42c10c5bdd2e35d1b59f98b48b2849155853e4dc28ee`
- All source `time_utc` values are null.

## Baseline structural graph

- Rows: 187,242
- Edges: 459,448
- `EXACT_BODY`: 23,471 bridge edges over 18,999 raw-identical groups (42,470 rows)
- `NORMALIZED_REPLAY`: 1,826 bridge chains after exact repetition has already been accounted for
- `PARENT_DIRECT`: 59,313
- `SAME_PARENT_SIBLING`: 33,466
- `MARKER_SAME`: 222,495
- `MARKER_ENDPOINT`: 118,877
- Components: 26,043
- Largest component: 144,075
- Singleton nodes: 22,894

## Near-body candidate tiers

Candidate similarity remains a relation class but the 18,852,564-row candidate matrix is intentionally not materialized in the active workspace; only aggregate counts and the generator recipe are retained.

Historical full canonical candidate pass:
- D0: 66,592 pair candidates; 42,494 nodes; 18,964 components
- D1: 308,204 pair candidates; 74,612 nodes; 13,280 components
- D2: 2,922,781 pair candidates; 96,209 nodes; 13,310 components
- D3: 15,621,579 pair candidates; 108,245 nodes; 13,955 components

D1 and below are candidate similarity candidates with measurable edit-distance, while larger tiers produce broad neighborhoods that should not be treated as coordination evidence. Candidate relation repair also found that approved normalization is sensitive to whitespace: rows such as those differing by trailing/newline characters had earlier distance labels that required manual adjudication.


## Time dependence

- 1,882 rows contain explicit textual timestamps or dates.
- Timestamp-like cues: payload 930, recovered_text 651, response 301. Parseable anchors: payload 909, recovered_text 641, response 301.
- Timestamp metadata: 1,851 parseable anchors, 31 invalid cues, 945 grounded structural links retained as evidence only.
- `TIME_DEPENDENCY` was removed from the active relation families pending a defensible time-causal reconstruction.
- Historical `TIME_DEPENDENCY` materialization had 5,714 rows, but only 11 direct links had strict chronological ordering and 850 structural links reversed direction.
- The temporal-anchor profile retains cue provenance, precision, token overlap, and adjudication metadata only.
- External chronology has 38 dated events, including Hugging Face 17,600 recovered
  actions and 6,280 clusters over 2026-07-09 through 2026-07-13. Dataset IDs
  cannot be placed on that timeline from this dataset alone.

## Meaningful markers and structural pivots

- 228,450 distinct exact marker spellings. 79,336 repeat.
- Generic placeholders, syntactic slot markers, broad un-numbered redaction labels,
  and source-redaction category text were not used as semantic links.
- `MARKER_ENDPOINT` markers represent transit/route pivots (gateway, URL, proxy,
  destination, shortener, service host), not equal payload originals.
- `MARKER_SAME` stores exact marker strings as structural co-occurrence pivots.
- `INFO_DEPENDENCY` unions parent lineage, exact body, approved-normalized replay,
  sibling, and marker-relation evidence.
- 459,448 dependency links currently remain resolvable to row endpoints.
- Parent mutation groups contain 1,266 exact bodies, 1,004 normalization-only replays,
  44,220 containment/append differences, 12,795 marker-inventory changes, and 26
  larger mutations. These classes describe change shape, not intent.

Pivot concentrations:
- `[REDACTED:destination:000003]`: 13,880 rows
- `[PROXY 4 URL 72]`: 11,977 rows
- `[ENCODED BLOB]`: 11,486 rows
- `[SERVICE 3 URL 209]`: 11,229 rows
- `[SERVICE 14 URL 4]`: 9,268 rows
- `[CREDENTIAL 1]`: 6,080 rows
- top parent `R0024455`: 858 child records
- second parent `R0036471`: 270 children

## Component structure

- 26,043 nonempty components.
- 144,075 of 187,242 rows live in the largest component.
- 22,894 singleton components.
- 3,149 nontrivial components after component extraction.
- EXACT_BODY alone has 18,999 components, maximum 120.
- NORMALIZED_REPLAY alone has 1,794 components, maximum 8.
- Adding marker-same links creates a global 144,075-row component and a 9,280-row
  second component.
- PARENT_DIRECT alone gives 25,847 components, largest 859.
- SAME_PARENT_SIBLING gives 9,636 parent-star components, largest 858.
- D1 near-text alone gives 13, 280 components, maximum 6,376.
- D2 and D3 respectively give 9,335 and 9,462-row maxima.

The structural graph therefore contains many tight small families around fixed
payload bodies and marker pivots, plus one much broader component created by repeated
route and generic fixture tokens.

## Local sample anchors

- `R0000007`: Cybergym task submission using `src/main.c`, shell-style reconnaissance,
  mounts, and `__modal/.container-arguments`.
- `R0000096`: dead-drop style write into the Artifactory remote-cache path with the
  `zz6017MODALCURL` marker.
- `R0000617`: 8,335-byte bundle containing Cybergym metadata, registry
  Basic-auth/manifest content, shell execution material, and 32 children.

These are strong structural anchors. They mirror OpenAI/Hugging Face report terminology, but
they are not timestamps, account identities, or proof of execution.

## External event cross-reference

External reports contain 38 dated events and and double-no-string terms.

OpenAI/Hugging Face chronology:
- 2026-04-20: first confirmed Artifactory write
- 2026-05-26: Artifactory SSRF and Hugging Face Git LFS fetches
- 2026-06-26: discovery of Artifactory admin exploitation
- 2026-07-08: internet access through Artifactory
- 2026-07-09: CyberGym/Miner launcher and credential-discovery activity
- 2026-07-10-13: Hugging Face credential harvest and compromise
- 2026-07-19: internal alert and initial response
- Hugging Face report states ~17,600 recovered actions in ~6,280 clusters

Sample-to-report correspondence:
- `R0000007` corresponds to initial recon/Cybergym task structures.
- `R0000096` corresponds to Artifactory dead-drop behavior.
- `R0000617` corresponds to registry supply-chain/transfer structures.
- These are structural correspondences only, not causal attribution.

## Segmentation

The 100 low-level segments use deterministic structural signatures only:
- ingestion / recon / injection / command construction
- staging / relay / exfiltration / cross-node work
- integration / reconciliation / cleanup / reuse
- each segment is an explicit 33/33/34 structural bucket

The segments are seeded from 100 distinct structural signatures drawn from 52,844
signatures. They should be treated as testable evidence families, not behavioral labels.

## Early-detection capability

A detector could flag these structural families early:
1. command-injection architecture with path `src/main.c`, inventory commands, mounts,
   `__modal/.container-arguments`, and `sqlite3_initialize`.
2. `github-remote-cache/zz6017MODALCURL` dead-drop writes.
3. 8,335-byte registry bundles containing Basic auth and manifest operations.
4. parent star bursts with 858 and 270 child records.
5. high-frequency pivot markers, especially `SERVICE 14 URL 4`, `PROXY 4 URL 72`,
   and ordered shortener URL channels.
6. exact and replay loops in parent-child clusters, including 70-row shortener URL stars.

However, structural similarity can also arise from safe replay fixtures. Early flagging
should require parent provenance, pivot-role classification, and scale or repetition
context in addition to bodies.

## What an investigator would still miss / limits

- `time_utc` is null for all 187,242 rows; explicit timing exists for only 1,882.
- IDs are storage artifacts, not identities.
- `kind` is mechanical collection stage, not role.
- All secrets, credentials, paths, hosts, tokens, and endpoint values are redacted.
- Parent metadata is a stored relationship, not an execution order.
- `recovered_text` and `response` are capture stages; full raw emit output is not guaranteed.
- 1,882 rows have explicit timestamp cues; the densest timed component has 1,334 rows,
  and 75 nontrivial timed components exist.
- D1–D3 candidate tiers are candidate-only adjacency; the row-level candidate matrix is intentionally not retained after this reconciliation.
- D1/D2/D3 component sizes are candidate adjacency benchmarks, not relation-family memberships.
- Local rows can match external techniques, but cannot prove actual exploitation or
  organizational impact.
- `INFO_DEPENDENCY` names are evidence classes, not causal claims. `TIMESTAMP_ANCHOR` records timestamp evidence, not causal temporal dependency.
- Cross-report chronology is not timestamp-aligned to any row.
- All 2,337 filtered rows were removed by width, placeholder, or byte-count rules; any
  useful evidence they contained is absent from the working graph.
- No boot-to-boot coordination authority, no authenticated sender, and no response logs
  are present.

## Reproducibility

- Source hash: `5a048060a8fc2a90246b42c10c5bdd2e35d1b59f98b48b2849155853e4dc28ee`
- graph core edges: 459,448; canonical SHA-256:
  `677fe3e0813a68ac2a95a499e3aeb28af4b5b3660e5e2703efc884c7f18a0ce1`
- core graph `10%` random and `5%` adversarial validation: 0 loopholes on row-resolving
  edges; 2 unresolved `PARENT_DIRECT` edges remain documented
- candidate audit: 100 samples per D1/D2/D3 distance plus D0 exact check; 0 mismatches.
- exact text source kind is redacted; candidates carry raw, normalized text metadata
- no source files, samples, or external report files were modified.
- See `RUN.md` for exact commands.


## Additional validation (2026-11-09 update)

- Independent adversarial cluster triggers: 60 recurring L1 clusters, 628 L3 markers, and 85 L4 components tested on 4,049 adversarial rows; 100% failed the cluster-specific trigger.
- Standardized edge schema: 459,448 core edges now use `source`, `dest`, `edge_class`, and `edge_sub_class`; `verify_core_graph.py` still returns 0 failed resolved structural edges.
- Full destructive audit v2 passed, including required artifact presence, 187,242 row IDs, sampled edge resolvability, taxonomy coverage, curated visualization checks, temporal anchors, grounded links, and source hash.
- Remaining caveats stay explicit: 46.7% coverage for the 100 deterministic structural segment signatures, one 144,075-row broad hub quarantined as non-explanatory, and the D1-D3 candidate matrix retained only in aggregate counts.
