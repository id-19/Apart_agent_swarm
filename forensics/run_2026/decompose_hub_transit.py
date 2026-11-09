#!/usr/bin/env python3
"""Decompose broad hub SC-L4-COMP-00001 rows by exact transit-marker signature."""
import json
import pathlib
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
RUN = ROOT / "forensics" / "run_2026"
LABELS = RUN / "node_taxonomy_labels.jsonl"
CORE_ROWS = RUN / "core" / "core_rows.ndjson"
OUT = RUN / "hub_transit_decomposition.json"
COVERAGE = RUN / "hub_transit_coverage.json"

HUB_ID = "SC-L4-COMP-00001"
TRANSIT_PREFIXES = [
    "[REDACTED:destination:",
    "[SERVICE ",
    "[PROXY ",
    "[SHORTENER URL ",
    "[IP ADDRESS ",
    "[REDACTED:network_address:",
]


def is_transit(marker: str) -> bool:
    return any(marker.startswith(prefix) for prefix in TRANSIT_PREFIXES)


def main() -> None:
    # Rows belonging to the broad hub.
    hub_row_ids = set()
    with LABELS.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("L4_component_cluster_id") == HUB_ID:
                hub_row_ids.add(rec["row_id"])

    # Group hub rows by sorted unique transit-marker signature.
    groups = defaultdict(list)
    with CORE_ROWS.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = rec["id"]
            if rid not in hub_row_ids:
                continue
            sig = sorted(set(m for m in rec.get("markers", []) if is_transit(m)))
            groups[tuple(sig)].append(rid)

    total_hub_rows = len(hub_row_ids)
    matched_rows = sum(len(v) for v in groups.values())
    # Any hub row absent from core_rows would be dropped from aggregation;
    # fail loudly rather than silently skip rows.
    assert matched_rows == total_hub_rows, (matched_rows, total_hub_rows)

    decomposition = []
    for sig, ids in groups.items():
        sig_list = list(sig)
        reps = sorted(ids, key=lambda x: int(x[1:]))[:8]
        decomposition.append({
            "transit_signature": sig_list,
            "exact_marker_count": len(sig_list),
            "row_count": len(ids),
            "row_share_of_hub": len(ids) / total_hub_rows,
            "representative_ids": reps,
            "status": "quarantined_non_explanatory" if not sig_list else "descriptive pivot family",
        })

    # Deterministic order: largest families first, then signature text.
    decomposition.sort(key=lambda o: (-o["row_count"], o["transit_signature"]))

    OUT.write_text(json.dumps(decomposition, ensure_ascii=False, indent=2), encoding="utf-8")

    coverage = {
        "total_hub_rows": total_hub_rows,
        "number_of_signatures": len(decomposition),
        "matched_rows": matched_rows,
    }
    COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    # Extra compatible filenames for the coverage summary.
    for extra_name in ("hub_transit_coverage_summary.json",):
        (RUN / extra_name).write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")

    # Verify JSON and counts.
    loaded = json.loads(OUT.read_text(encoding="utf-8"))
    assert isinstance(loaded, list)
    assert sum(o["row_count"] for o in loaded) == total_hub_rows
    assert len(loaded) == len(decomposition)
    for o in loaded:
        assert set(o.keys()) == {
            "transit_signature", "exact_marker_count", "row_count",
            "row_share_of_hub", "representative_ids", "status",
        }
        assert o["exact_marker_count"] == len(o["transit_signature"])
        assert len(o["representative_ids"]) <= 8
        if not o["transit_signature"]:
            assert o["status"] == "quarantined_non_explanatory"
        else:
            assert o["status"] == "descriptive pivot family"

    print(f"hub_rows={total_hub_rows}")
    print(f"signatures={len(decomposition)}")
    print(f"matched_rows={matched_rows}")
    print(f"empty_signatures={sum(1 for o in decomposition if not o['transit_signature'])}")
    print(f"verified_json={OUT}")

    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script": "forensics/run_2026/decompose_hub_transit.py",
        "action": "hub_transit_decomposition_written",
        "total_hub_rows": total_hub_rows,
        "signatures": len(decomposition),
        "output": "forensics/run_2026/hub_transit_decomposition.json",
        "status": "complete",
    }
    with (RUN / "reconstruction_log.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":"), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
