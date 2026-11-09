# Temporal comparison audit

- Anchor ledger: `temporal_anchor_ledger.json` (1,851 valid anchors).
- Grounded links: `timeline_chains.jsonl` (945).
- Classifications: `temporal_order_edge_classes.json`.
- Conflicts retained: 0 in `temporal_conflicts.jsonl`.
- Partitions: `chronology_partitions.jsonl` by explicit anchor calendar day.

No row is assigned a direct execution timestamp unless a valid cue existed. Conflicts are retained, not resolved by row order or structural edge direction.
