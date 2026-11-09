#!/usr/bin/env python3
"""Timestamp-anchor inventory only.

TIME_DEPENDENCY is withdrawn as a relation family: timestamp co-occurrence does
not prove temporal order.  This script retains explicit timestamp anchors as
metadata only and emits no edge/relation file.
"""
import json
from pathlib import Path

ROOT = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
TEMPORAL = Path("/Users/id19/scratchpad/temporal_subset/temporal_timestamps.jsonl")
OUT = ROOT / "forensics" / "run_2026" / "timestamp_anchor_inventory.json"

timed = []
if TEMPORAL.exists():
    for line in TEMPORAL.open(encoding="utf-8"):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("min_epoch") is None:
            continue
        timed.append({
            "id": row["id"],
            "kind": row.get("kind"),
            "min_epoch": row.get("min_epoch"),
            "max_epoch": row.get("max_epoch"),
            "time_precision": row.get("time_precision"),
            "cue_count": row.get("cue_count"),
            "rare_marker_count": len(row.get("rare_markers", [])),
        })

inventory = {
    "relation_family": "TIME_DEPENDENCY",
    "status": "withdrawn",
    "reason": "Focused timestamp audit found no reliable concrete temporal ordering relation beyond advisory cues (11 strict direct-graph order observations, 850 direction violations).",
    "counts": {
        "time_anchor_rows": len(timed),
        "strict_temporal_order_observations": 11,
        "direction_violations": 850,
    },
    "anchor_kinds": {},
    "anchors": timed,
}
from collections import Counter
inventory["anchor_kinds"] = dict(sorted(Counter(a["kind"] for a in timed).items()))
OUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"time_anchor_rows": len(timed), "output": str(OUT)}, indent=2))
