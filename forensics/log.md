# Forensics log

Goal: Take the Swarm Traces dataset (Swarm Traces, 2026) and build a tool that reconstructs who talked to whom and how a piece of information spread through the swarm; test whether coordination could be flagged early; document what an investigator still misses.

Constraints:
- Dataset: Data/redacted.jsonl, 189,579 rows, 3 kinds: payload, recovered_text, response.
- time_utc is null for every row.
- agent/task IDs are redacted to placeholders.
- redacted.jsonl.gz is byte-identical to jsonl.

Current state:
- Basic EDA completed.
- Family classifier (coarse boolean text features) available.
- Parent linkage fully backward.
- No artifact host available without re-login.

Planned steps:
1. Baseline forensic audit (counts, schema, nulls, identities, chain direction).
2. Identity / "who talked to whom" reconstruction attempt.
3. Spread model (chain edges, shared infrastructure markers, hubs, descendant propagation).
4. Early-coordination detection simulation using ID-order as an approximate timeline.
5. Investigator blind-spot memo.
6. Publish reproducible tool and report.

Final mapping result:
- Immediate nominal attribution is unavailable due redaction.
- Pseudonym clusters are exported in pseudonym_clusters.csv (43,487 candidate units, top 200 shown).
- Shared pivots support structural attribution even when nominal IDs are unavailable.
- Task complete as a forensic reconstruction deliverable: tool, edge artifact, early-flag simulation, external triangulation, and blind-spot memo.

Cross-source linking update:
- Added explicit behavioral-link assumption: parent/child are treated as same observational chain unless independent evidence contradicts.
- Additional propagation pivots include TINYOK, CHAINWORKS, FANPASS_12345, cybergym, ENCODED BLOB IDs, and the sqlite3_initialize template.
- Tool outputs remain pseudonym-level because source IDs are redacted; degree of certainty is recorded in the final report instead of omitted.

## Content-flow edges
- edges CSV: /Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/content_flow_edges.csv (110207 rows)
- summary: /Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/content_flow_summary.json
- edge types: rare_marker_edge=32124, shared_pivot_edge=68738, url_identifier_edge=8346, command_template_edge=999
- distinct tokens by type: command_template_edge=451, rare_marker_edge=14818, shared_pivot_edge=31597, url_identifier_edge=2734
- components: 19883, largest: 11552
- top hubs: R0018789(2262), R0004939(753), R0005587(677), R0020517(663), R0005176(569)
- temporal: forward=110207, backward=0
parent_plus_event_markers parent_plus_command_body parent_plus_template

## Agent A: structural

- Graph built from `parent_id` only: 189579 nodes, 61125 explicit edges. Edges are child -> parent; CSV `forensics/structural_edges.csv`.
- No payload has a parent. Kind transitions: recovered_text -> payload 42707; response -> payload 18417; recovered_text -> recovered_text 1 (R0189571 parent R0189559). Total recovered_text->recovered_text yes.
- Roots by absent parent / parent^-1: 128454 roots. Connected components (undirected parent links): 128454, acyclic forest. Isolated components 102206; nontrivial 26248; largest component size 859 (R0024455's FANPASS fanout + root).
- Salient roots:
  - CHAINWORKS R0000021: 0 descendants; R0021401: 2 descendants (R0068781, R0068782).
  - TINYOK root R0000027: 2 descendants (R0053434 response, R0062486 recovered_text); marker occurs in 8 rows total.
  - FANPASS_12345 root R0024455: 858 descendants; marker occurs in 3 rows total.
- First 20 payloads: probes 11, links 9, leafs 0 (by family membership; all currently 0-child in ID order).
- Summary JSON: `forensics/structural_summary.json`.

Final linkage deliverable:
- Parent-only observed linkage: 61,125 edges, 128,454 independent roots.
- Content-flow linkage (rare marker / pivot / URL identifier / command template): 110,207 edges, 102,649 roots.
- Token1..30 grouping: 172,460 edges, 93,691 roots.
- Normalized template grouping + parent: 108,488 edges, 81,091 roots.
The root count is intentionally reported as policy-dependent, because infrastructure-sharing edges can merge otherwise independent streams.

## Independent streams / roots pass (temporal/root hierarchy)

Added:
- forensics/temporal_dag.csv (61,125 parent->output edges; ID order treated as observed ordering only)
- forensics/independent_streams.json (exact roots, component counts, marker trajectories, ID-order analysis)
- forensics/stream_summary.txt

Key results:
- Exact roots by parent field: 128,454 (all weak components have one root).
- Structural roots after removing inferred content/token edges: 128,454.
- Connected components: explicit-only 128,454; with token/content edges 43,600.
- First hubs: CHAINWORKS R0000021/R0021401; TINYOK R0000027 (2 children); FANPASS/R0024455 (858 children).
- ID order is not one stream: many roots and broad interleaving (median descendant density ~0.001).
- Caveats: inferred token/content edges may overmerge; timestamps absent.

## High-descendant payload linkage pass (output-observation vs propagation)

Deliverable: `forensics/high_descendant_links.json` (20 payload roots with highest direct child count).

Selection: Top 20 payload roots by parent_id child count (range 858 down to 44 edges).
All 20 roots have exclusively `response` + `recovered_text` children (counts are paired observations; no child is a payload). Therefore the child counts are output-observation multiplicity, not descendant propagation.

Key findings:
- R0024455 (FANPASS_12345) has 858 direct children (429 response, 429 recovered_text), the largest component. Its FANPASS marker and `[ENCODED BLOB 17078]` occur in only its own root + 2 output records (R0057512 response, R0069699 recovered_text); zero later payloads reuse them. Neighboring next payloads share no root tokens except one population-wide destination.
- No top-20 root has a payload child; downstream rare child-string reuse is minimal: R0002403 has 6 later payloads reusing `[REDACTED:hf_repo:000005]`, R0049534/R0050038 have 1 payload each reusing `[SHORTENER-3]`, other roots 0 payload hits (only response/recovered_text infrastructure sharing).
- Shared next-payload tokens are overwhelmingly population-wide infrastructure markers (credentials, destinations, service hosts; global df in hundreds/thousands), not root-specific content tokens. No high-descendant payload shows strong causal linkage to the next five payloads.
- Spurious-edge warning: treating parent->child output edges as propagation would inflate lineage; external linkage should require rare child strings/markers rather than generic scaffold, shortener host, or destination tokens.

Assessment: high child counts among these payloads come from repeated execution/output observation, not real propagation; direct child edges should be classified as observation edges unless a rare child token reoccurs in a later payload.

## Graph framework expansion (typed linkage)

Added `forensics/graph.py` typed linkage framework with 102 named edge predicates,
`links(samples, edge_types)`, `edge_type_catalog.csv`, and `multi_link_strategy.md`.

Counts (ID order only; 189,579 samples):
- parent_child only: 61,125 edges, 128,454 roots.
- parent_child + high-confidence A/B pivots: 651,708 edges, 21,527 roots.
- parent_child + command body + normalized template: 174,719 edges, 58,204 roots.
- all 103 typed edge types on 1,000-sample slice: 13,780 edges (full run: 1,176,979 edges, ~80 sec).

Confidence tiers:
- A: parent lineage, sibling same parent, compound exact pivots (shortener+destination, source+runtime).
- B: strong token pivots (credentials, blobs, shortener codes, HF repos, templates, rare decoded literals).
- C: moderate infrastructure pivots (destinations, service/proxy/redirect, workload, opaque fragments, IP/env/config).
- D: weak/shared context (bare runtime, broad containment literals, kind transitions).

Notes:
- Link counts are policy-dependent; broad token edges can overmerge.
- Direction is ID order only, not real chronology. Credentials/identifiers may be spoofed.

## Report-backed pivot linking pass (cached external reports)

External reports: METR (`metr_report.pdf`/`metr_report.txt`/`metr_blog.html`), OpenAI (`openai_report.pdf`/`openai_report.txt`/`openai_post.html`), Hugging Face timeline (`hf_timeline.html`) compared with `Data/redacted.jsonl`.

Artifact: `forensics/report_pivot_links.json` (56 pivots; 3,055 candidate star edges shown; full edge counts recorded per pivot).

Representative pivots:
- JAN183411: 32 occurrences (R0012387-R0069570), 24 roots, 8 recovered outputs.
- cybergym: 2,469 occurrences (R0000014-R0189574), 1,933 roots, 536 related outputs.
- PhaseOne family: PhaseOne 18, PhaseOneDecompressor 13, PhaseOneDecompressorFuzzer 8, PHASEONE64H 1 occurrences.
- Artifactory/path/message-board namespaces: artifactory 2,211; zzFILE 797; zzMODAL 281; zzMAILBOX 18; zzINBOX 27; zzRESULT 50; zzTEST 30; packages.hub.ace-research.openai.org 2,448 occurrences.
- Modal/shortener proxies: MODAL 545; SHORTENER-1-HOST 6,325; SHORTENER-2-HOST 495; SHORTENER-3-HOST 275 records.
- Destination low-frequency/common pivots: D3 13,886; D2 5,666; D58 2,908 occurrences; selected HF-upload destination pivots included.
- Destination IDs are candidate linkage only; rare (2-30 record) destinations form the finer candidate graph used elsewhere.

Identity standard: no claim of identity from a single marker. Each pivot is recorded as candidate edges only unless corroborated by a second anchor (report-backed name plus dataset structural pattern/parent-child context).
