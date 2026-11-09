# Step 3 draft plan: temporal partitions and dependency DAG

## Purpose

Construct a time-wise reconstruction graph without treating row order or graph links as time causation. Step 3 takes inventory of every temporal anchor and every grounded structural link, then chooses only defensible before/after/same-time relations and produces a partition DAG plus temporal isolation.

## Why Step 2 comes first

Temporal clustering cannot be created before meaningful clusters. Time must be attached only to already tested structural evidence.

## Inputs

- Timestamp-bearing rows and explicit decoded cues.
- Valid machine-epoch cues where available.
- Calendar-only cues kept as evidence but not absolute anchors.
- Invalid cues such as month 44/45 kept as audited non-anchors.
- Direct structural links.
- Reports as candidate influences, not authoritative assignment.

## Temporal classifications

- `ANCHOR_AT_SAME_TIME`: explicit equal valid cue.
- `ANCHOR_BEFORE`: explicit real time order.
- `ANCHOR_AFTER`: explicit real time order.
- `TEMPORAL_CONFLICT`: links observed by cues and structural edge directions disagree.
- `ANCHORED_PRECURSOR`: temporal cue supports a possible temporal lead; not proof.
- `STRUCTURAL_PRECURSOR_NO_TIME`: structure implies possible relevance but no time support.
- `UNCOMPARABLE`: missing or weak time evidence.
- `partition`: probable event windows or movement groups not strictly ordered.

## Rules

1. Time comes only from visible temporal text, not row sequence.
2. `Temporal lead` from reports, manually observed links, and explicit script-recovered cues can suggest order, but must stand as low-confidence unless corroborated.
3. Every structural edge that participates in a temporal partition gets both:
   - `base relation`
   - `temporal verdict`
4. Forward only explicit evidence:
   - strict cue order
   - equality
   - documented tie where both endpoints are anchored and the tie can be computed
5. No reverse-direction invention.
6. The graph is partition/DAG: each suspected cluster can be early, parallel, or unrelated, and contradiction blocks forced ordering.
7. Direct temporal evidence should not swamp structural cues.

## Intermediate graph classes

- `TIME_AT_SAME_ANCHOR`
- `TIME_LEAD_EXPLICIT`
- `STRUCTURAL_PRECURSOR`
- `TEMPORAL_CONTRADICTION`
- `TIME_UNKNOWN`
- `TIME_PARTITION_PRECURSOR`

## Procedure

1. Build cue ledger with valid dates, machine epochs, invalid expressions, tie classes.
2. Build direct temporal graph over only valid anchor events.
3. Add structural candidate links and compare.
4. If a link direction conflicts with timestamp observations, flag it as contradiction.
5. Repeat per family:
   - parent mutation chains
   - exact body descendants
   - marker strings
   - shorteners/destinations
   - registry payloads
   - proxy chains
6. Partition structurally/temporally connected groups where valid anchors are absent.
7. Only mass-label when structural partitions have disproof sample support and temporal edge provenance.

## Deliverables

- `time_reasoning.md`
- `temporal_anchor_ledger.json`
- `time_lead_candidates.json`
- `temporal_comparison_audit.md`
- `chronology_partitions.jsonl`
- `time_evidence.csv`
- `temporal_conflict_report.json`

## Success condition

Step 3 succeeds when:
- temporal assertions are valid where claimed,
- conflicts are retained,
- rows without usable timing are explicitly unanchored,
- partitions are reproducible,
- and delays are not inferred from external reports alone.
