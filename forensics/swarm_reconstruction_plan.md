# Swarm Traces Reconstruction Plan

## Overall targets

1. Build and adversarially verify a row-level graph from the Swarm Traces dataset without dropping provenance or hiding linkage criteria.
2. Segment the graph into at least 3 high-level operational phases and 100 nested, justified working sets.
3. Use the 1,882 timestamp-bearing rows as time anchors to reconstruct plausible propagation paths.
4. Produce a highly detailed report answering whether coordination could have been flagged early and what an investigator would still miss.

## Operating rules

- `sample` means one row. `body` means the `text` field.
- Record profiles are metadata, not behavior evidence.
- Every reported claim must cite sample IDs and concise supporting evidence.
- Every edge has a literal trigger and provenance.
- No arbitrary truncation or cap during edge construction.
- No sample ordering may be treated as time unless an explicit time appears in source text.
- Repeated markers stay linked at any occurrence count.
- only approved semantic synonyms may collapse text:
  - `huggingface` / `hugging face` / `hf`
  - Python invocation aliases in otherwise exact code structures
  - University behavior-equivalent whitespace and punctuation wrappers.
- Marker identifiers stay exact, including numbers and IDs.
- Reproducible scripts and logs are required.
- Three active agents minimum, with one builder, one adversary, and one independent adjudicator.
- Start every phase with exploration of raw samples and completed outputs, then scale.
- Maintain a running `forensics/reconstruction_log.jsonl` of files produced, edge-class definitions used, samples changed, and rejected claims.

## Agent protocol

- `BUILDER`: implements, derives signatures, creates graph artifacts.
- `ADVERSARY`: tries to break every link, segmentation, and timeline claim.
- `ADJUDICATOR`: reconciles differences against row evidence.
- Each agent submits a verifier report, not just affirmations.
- Disagreements are recorded as `open_disputes.jsonl` until a row-evidence winner is selected.
- No commit, push, release, or artifact deletion without explicit user approval.

## Phase 0 — Pilot and instrument setup

1. Create one reproducible driver script for each edge class.
2. Run a 10,000-sample pilot before the full 187,242-row pass.
3. Build a row dictionary with sample IDs, position, mechanical kind, parent ID, text length, and hashes.
4. Save the pilot row subset and all edge outputs under `forensics/pilot/`.
5. Test parser, hash, and citation generation before scaling.

Gate:
- random sampled source lines re-read by a process that did not generate them
- 100% round-trip citation coverage

## Phase 1 — Core evidence-preserving edge classes

Start with these classes, then extend whenever sampling or linked components reveal gaps:

- `EXACT_BODY`: byte-identical `text` rows.
- `NORMALIZED_REPLAY`: rows exact only after approved synonym rewrites and whitespace handling.
- `NEAR_BODY_D1`, `NEAR_BODY_D2`, `NEAR_BODY_D3`: rows at Levenshtein limits of 1, 2, or 3, with actual distance per edge.
- `PARENT_DIRECT`: sample to exact `parent_id` links.
- `SAME_PARENT_SIBLING`: samples sharing one parent.
- `MARKER_SAME`: each sampled pair sharing one or more exact bracketed markers.
- `MARKER_ENDPOINT`: transit-style markers such as proxies, router URLs, service URLs, and shorteners, reported separately.
- `INTENT_SIGNATURE`: exact shared operation signature from body content rather than broad language profile.
- `PARENT_MUTATION`: linked sample pairs with textual additions, substitutions, chunk changes, or routing changes.
- `TIMESTAMP_ANCHOR`: every discovered time-bearing edge from rows holding explicit time.

All edges store:
- source ID
- destination ID
- edge class
- trigger string
- evidence snippet
- bucket/hash when applicable

Gate:
- every edge resolves both endpoint sample IDs
- no duplicate source-target key within a class
- protected anchor rows are present
- no class loses provenance to compression

## Phase 2 — Full-graph construction

1. Run every Phase 1 edge generator over all filtered rows.
2. Keep raw, normalized, marker, parent, function, and timestamp projections separate.
3. Build combined projections only after class-level validation passes.
4. Track edge counts and class overlap.
5. Preserve rejected and disputed edges with reasons.

Deliverables:
- `forensics/graph_edges_v2.jsonl`
- `forensics/graph_rows_index.json`
- `forensics/graph_class_stats.json`

Gate:
- 10% random adversarial sample from each edge class passes row-level acceptance
- over-linkage rate below 2%
- under-linkage rate below 2%
- all unexplained edges equal 0

## Phase 3 — Adversarial edge quality

Each edge class requires two independent random samples:
- at least 10% accepted review
- up to 5% adversarial disproof review

Each dispute resolves to one of:
- accepted
- corrected
- rejected
- needs new edge class

Whenever sampling reveals a gap, create a new class rather than forcing it into an existing one.
Repeatedly transcribe every accepted class into the running log.

Deliverables:
- `forensics/edge_validation_report.md`
- `forensics/disputed_edges.jsonl`
- `forensics/edge_class_acceptance.json`

Gate:
- every edge class has adjudicated verdict data
- unresolved disputes are marked, not silently ignored

## Phase 4 — Deep sampling and graph component analysis

1. Build `G_CORE`: exact body + parent same + marker same.
2. Build `G_TEXT`: exact body + replay + near body at distances 1, 2, and 3.
3. Build `G_FUNCTION`: parent + function signatures.
4. Build `G_TIMESTAMP`: timed rows plus every approved multi-hop edge.
5. Investigate each large component manually before attempting statistical summaries.
6. Record marker and mutation roles in human-readable language.
7. Try linked high-resolution segments through direct graph neighborhoods.

Deliverables:
- component summaries by graph
- high-fan node inventories by graph
- component edge-mix profiles
- plain-language cluster explanations

Gate:
- all large components have at least 3 exemplar rows cited
- each component outer change evidence has sample pairs

## Phase 5 — Segment construction with plain-English justification

Create at least 3 high-level phases and 100 nested low-level segments.

Examples of segment families:
- ingestion and command construction
- database and exfiltration of snippets
- multi-stage proxy routing
- payload cleanup and redirect handling
- timestamped operational activity
- changes across parent chains

For each segment, state:
- definition
- structurally exact trigger
- rows
- edges
- plain-English purpose
- supporting report or sample evidence

Validation loop:
1. sample at least 10% of members
2. build an adversarial disproof set
3. reject or split poor segments
4. rerun both checks on any changed segment.

Deliverables:
- `forensics/segments/high_level_segments.json`
- `forensics/segments/low_level_segments.json`
- `forensics/segment_validation_report.md`

Gate:
- at least 3 high-level and 100 low-level segment definitions accepted
- each definition yields human-explainable purpose and row evidence

## Phase 6 — Timeline reconstruction

1. Identify all rows containing explicit time strings or directly extractable dates.
2. Link only grounded edges out from those anchors.
3. Derive mutation, staging, exfiltration, cleanup, and retry signals.
4. Produce candidate agent paths, distinct tests, and shared information use.
5. Mark low-confidence chains and suspected gaps.

Deliverables:
- `forensics/timeline_evidence.csv`
- `forensics/timestamp_marker_profile.json`
- `forensics/timeline_chains.jsonl`

Gate:
- no time inference from row order
- every timeline edge is supported by actual sample-to-parent, marker, text, or function evidence

## Phase 7 — External-source mapping

1. Read local reports and evidence HTML in detail.
2. Map segments, pivots, credentials, URLs, proxies, and service IDs to incident narrative events.
3. Keep external claims separately from internal findings.
4. Report explicitly when a perceived report detail lacks local sample evidence.

Deliverables:
- `forensics/timeline_external_mapping.md`
- a row-to-report citation table

Gate:
- every report event claim either maps to sample evidence or is marked unverified

## Phase 8 — Final reconstruction graph

1. Apply post-pilot corrections to all phases before final execution.
2. Produce one clean graph assembled from accepted edges.
3. Attach to each row:
   - raw body
   - direct evidence links
   - segment and phase memberships
   - time-anchor relationships
   - mutation summaries
4. Build row-relevant reachability and phase flow summaries.

Deliverables:
- `forensics/reconstruction_graph_v1.jsonl`
- `forensics/reconstruction_components.csv`
- `forensics/row_flow_summary.json`

Gate:
- reconstruction phase explains at least the majority of large components
- all unresolved samples are explicitly enumerated

## Phase 9 — Key findings and blind-spot analysis

1. Identify primary sources of information in the graph.
2. distinguish:
   - one agent repeating tests
   - multiple agents reusing communicated information
   - independent discovery of same route, target, or vulnerability signal
3. For each activity class identify which markers are merely infrastructural and which are data-bearing.
4. Identify:
   - early coordinated evidence
   - misleadingly huge infrastructure components
   - missing rows or untracked transitions
   - rules or documents that cannot be recovered.

Deliverables:
- `forensics/findings/core_findings.md`
- `forensics/findings/blind_spots.md`
- `forensics/findings/early_detection_verdict.md`

Gate:
- every finding has both a narrative and a machine-readable support file
- every blind spot states why the dataset cannot answer it

## Phase 10 — Repro tools and cleanup

1. Keep only scripts needed for reproduction and major results.
2. Write a short, exact run order.
3. Maintain a concise results summary and a verbose audit log.
4. Clean temporary exploratory files.
5. Produce final highly detailed answer addressing:
   - spread reconstruction
   - early detection
   - investigator limits

Deliverables:
- `forensics/RUN.md`
- `forensics/FINAL_summary.md`
- `forensics/reconstruction_log.jsonl`
- output manifests and all validated graph artifacts.

Explicit non-goals until later:
- no code repo generalization work
- no destructive git actions
- no push or release actions without direct user approval

Once this plan is approved, it should remain unchanged until completion.
