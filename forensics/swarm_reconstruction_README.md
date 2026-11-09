# Swarm Traces Reconstruction Tool (release 1)

Tool: `forensics/swarm_reconstruct.py`

## What it does
Builds a read-only propagation graph from `Data/redacted.jsonl`:
- exact lineage (`parent_id` -> row),
- exact content echoes via SHA256,
- common pivot/marker buckets (when they are rare enough to be informative).

## Commands
```bash
cd /Users/id19/Programming/AI_research/Apart_agent_swarm

# Full empirical run
python3 forensics/swarm_reconstruct.py build \
  --input Data/redacted.jsonl \
  --out-dir forensics/swarm_reconstruction_full \
  --max-marker-freq 25 \
  --min-confidence 0.7

# Query one row's local blast radius
python3 forensics/swarm_reconstruct.py blast \
  --db forensics/swarm_reconstruction_full/swarm_reconstruction.sqlite3 \
  --from R0000617 --depth 2 --limit 100

# Early-warning replay (no timestamps, ID-order)
python3 forensics/swarm_early_flag_test.py
```

## Outputs
- `swarm_reconstruction.sqlite3`: authoritative local query API
- `nodes.ndjson`: row + synthetic atom records
- `edges.ndjson`: confidence-labelled relationship records
- `components.json`: largest connected components
- `viewer.html`: first 1,000 visual subgraph (local only)
- `observer_report.md`: what was found and what remains unprovable
- early-flag summary in scratchpad

## What it intentionally does **not** claim
- Converse chronology is not reconstructable: `time_utc` is null everywhere.
- Handles are redaction masks, not real people.
- Parent-child edges and hash echoes are evidence of data flow/recovery, not intent or exploitation.
- Cross-marker correlation is structural; cannot by itself establish collusion.
- Outer-channel signals (image beacons, proxy calls) are not retained as dataset rows.

## Result validation
- `python3 forensics/swarm_reconstruct.py blast --db ... --from R0000617 --depth 1`
- Inspect `first_10000_payload_audit.md` for structural baselining.
- `observer_report.md` retains the exact caveat list required for investigation reports.