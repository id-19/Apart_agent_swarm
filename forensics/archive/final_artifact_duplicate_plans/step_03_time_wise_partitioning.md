# Step 3 draft plan: time-wise partitions/DAG

Step 3 builds temporal ordering from high-confidence anchors, with probabilistic relative anchors and disputes; no literal search. Node analysis is precise.

## Anchor classes

- Valid dated cues with machine epoch.
- Calendar-only cues (low authority)
- Invalid calendar-only cues (non-anchor, retained evidence)
- Same timestamp/cue equality.
- Structural precursor (not time)
- Replay or echo matching, only simultaneous candidate
- Explicit external candidate.

## Temporal graph requirements

Deliver a time-wise DAG/class model of:
- before
- after
- same time within precision
- incomparable
- conflict
- structural precursor without temporal assertion
- probable partition only.

### Dataset requirements

- `temporal_anchor_ledger.json`
- `temporal_order_edge_classes.json`
- `time_reasoning.md`
- `time_reordered_sample_inventory.json`
- `temporal_conflicts.jsonl`
- `temporal_was_diagnosed.md`
- `temporal_learnings.md`

### Methods
1. inspect exact cue rows and component co-occurrence around those anchor rows.
2. Use validated pairs via explicit cues.
3. If no explicit time, assign structural partitions based on strongest grounded hints.
4. Build a DAG only for grounded relationships; otherwise leave as `time_unknown`.
5. Use external candidate chronology only as supportive/as rival.
6. Assess contradictory direction and confidence.

## Success condition
Step 3 is complete when a DAG/partition timeline can attach each relation rather than forcing chronology through unsupported precedence.
