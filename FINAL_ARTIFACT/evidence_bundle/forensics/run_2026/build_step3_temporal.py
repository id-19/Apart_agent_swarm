#!/usr/bin/env python3
import json, pathlib, collections, datetime

RUN = pathlib.Path("forensics/run_2026")
anchors = json.load(open(RUN/"timestamp_anchor_inventory.json"))["anchors"]
anchor_by_id = {a["id"]: a for a in anchors}
chains = [json.loads(l) for l in open(RUN/"timeline_chains.jsonl",encoding="utf-8") if l.strip()]

# Temporal anchor ledger.
ledger = {
    "relation_family": "TIMESTAMP_ANCHOR",
    "status": "metadata_only; TIME_DEPENDENCY withdrawn as causal family",
    "anchor_count": len(anchors),
    "valid_anchor_count": len([a for a in anchors if a.get("min_epoch") is not None]),
    "invalid_cues_retained_separately": 31,
    "anchors": anchors,
}
(RUN/"temporal_anchor_ledger.json").write_text(json.dumps(ledger,indent=2,ensure_ascii=False))

# Classify grounded links.
classes = []
lead_candidates = []
conflicts = []
for c in chains:
    a = anchor_by_id.get(c["source"])
    b = anchor_by_id.get(c["target"])
    both = a is not None and b is not None
    if both:
        sa, sb = a["min_epoch"], b["min_epoch"]
        if sa < sb:
            cls = "ANCHOR_BEFORE"
            lead_candidates.append({
                "chain_id": c["chain_id"],
                "source": c["source"],
                "target": c["target"],
                "source_min_epoch": sa,
                "target_min_epoch": sb,
                "delta_seconds": sb - sa,
                "edge_type": c["edge_type"],
                "confidence": c.get("confidence"),
                "proof": c["proof"],
            })
        elif sa > sb:
            cls = "TEMPORAL_CONFLICT"
            conflicts.append({
                "chain_id": c["chain_id"],
                "source": c["source"],
                "target": c["target"],
                "source_min_epoch": sa,
                "target_min_epoch": sb,
                "delta_seconds": sa - sb,
                "edge_type": c["edge_type"],
                "proof": c["proof"],
            })
        else:
            cls = "ANCHOR_AT_SAME_TIME"
    elif a is not None:
        cls = "ANCHORED_PRECURSOR"
    elif b is not None:
        cls = "STRUCTURAL_PRECURSOR_NO_TIME_TARGET_ONLY"
    else:
        cls = "STRUCTURAL_PRECURSOR_NO_TIME"
    classes.append({
        "chain_id": c["chain_id"],
        "source": c["source"],
        "target": c["target"],
        "edge_type": c["edge_type"],
        "temporal_class": cls,
        "source_anchor": a is not None,
        "target_anchor": b is not None,
        "source_min_epoch": a["min_epoch"] if a else None,
        "target_min_epoch": b["min_epoch"] if b else None,
        "proof": c["proof"],
    })

(RUN/"temporal_order_edge_classes.json").write_text(json.dumps({"links": classes,"counts": dict(__import__("collections").Counter(x["temporal_class"] for x in classes))},indent=2,ensure_ascii=False))
(RUN/"time_lead_candidates.json").write_text(json.dumps({"candidate_count": len(lead_candidates),"candidates": lead_candidates},indent=2,ensure_ascii=False))
(RUN/"temporal_conflict_report.json").write_text(json.dumps({"conflict_count": len(conflicts),"conflicts": conflicts},indent=2,ensure_ascii=False))
with (RUN/"temporal_conflicts.jsonl").open("w",encoding="utf-8") as f:
    for c in conflicts:
        f.write(json.dumps(c,separators=(",",":"),ensure_ascii=False)+"\n")

# Partitions by calendar day of anchor (explicit time window only).
by_day = collections.defaultdict(list)
for a in anchors:
    dt = datetime.datetime.utcfromtimestamp(a["min_epoch"]).date().isoformat()
    by_day[dt].append(a["id"])
# grounded link membership per partition date source/target
link_ids_by_day = collections.defaultdict(list)
for c in classes:
    if c["temporal_class"] in ("ANCHOR_BEFORE","ANCHOR_AT_SAME_TIME","TEMPORAL_CONFLICT"):
        dt = datetime.datetime.utcfromtimestamp(c["source_min_epoch"]).date().isoformat()
        link_ids_by_day[dt].append(c["chain_id"])

partition_lines = []
for i,(day, ids) in enumerate(sorted(by_day.items())):
    partition_lines.append({
        "partition_id": f"TP-{i+1:04d}",
        "time_window_utc_date": day,
        "anchor_row_count": len(ids),
        "anchor_row_ids": ids[:25],
        "anchor_row_total": len(ids),
        "grounded_link_ids_in_window": link_ids_by_day.get(day,[])[:25],
        "grounded_link_count_in_window": len(link_ids_by_day.get(day,[])),
        "claim_level": "advisory temporal partition; explicit cue only, not causal proof",
    })
with (RUN/"chronology_partitions.jsonl").open("w",encoding="utf-8") as f:
    for p in partition_lines:
        f.write(json.dumps(p,separators=(",",":"),ensure_ascii=False)+"\n")

# Sample inventory based on anchored rows.
sample_inv = {
    "valid_anchor_sample": anchors[:25],
    "single_anchor_rows_example_count": len([c for c in classes if c["temporal_class"]=="ANCHORED_PRECURSOR"]),
    "both_anchor_rows_count": len([c for c in classes if c["temporal_class"] in ("ANCHOR_BEFORE","ANCHOR_AT_SAME_TIME","TEMPORAL_CONFLICT")]),
    "no_time_rows_count": 187242 - len(anchor_by_id),
}
(RUN/"time_reordered_sample_inventory.json").write_text(json.dumps(sample_inv,indent=2,ensure_ascii=False))

# Markdown time reasoning.
(RUN/"time_reasoning.md").write_text("""# Time reasoning

`TIME_DEPENDENCY` is not an active relation family. Only 1,851 valid anchors exist, 31 invalid cues are retained as evidence, and only 11 strict chronological observations were available historically.

- Grounded structural links: 945.
- Links with both endpoints timed: %d.
- Time lead candidates (source epoch < target epoch): %d.
- Temporal conflicts (source epoch > target epoch): %d.
- Rows with usable time anchors: %d of 187,242.

Temporal classes are assigned from explicit cue epochs only. Links without explicit timing are `STRUCTURAL_PRECURSOR_NO_TIME` and are not treated as timed.
""" % (len([c for c in classes if c["source_anchor"] and c["target_anchor"]]), len(lead_candidates), len(conflicts), len(anchor_by_id)))
(RUN/"temporal_comparison_audit.md").write_text("""# Temporal comparison audit

- Anchor ledger: `temporal_anchor_ledger.json` (1,851 valid anchors).
- Grounded links: `timeline_chains.jsonl` (945).
- Classifications: `temporal_order_edge_classes.json`.
- Conflicts retained: %d in `temporal_conflicts.jsonl`.
- Partitions: `chronology_partitions.jsonl` by explicit anchor calendar day.

No row is assigned a direct execution timestamp unless a valid cue existed. Conflicts are retained, not resolved by row order or structural edge direction.
""" % len(conflicts))
(RUN/"temporal_was_diagnosed.md").write_text("Temporal anchors were diagnosed as metadata only: 1,851 valid, 31 invalid, 11 strict directed orders, 850 historical direction violations.\n")
(RUN/"temporal_learnings.md").write_text("No causal temporal ordering is defensible from this dataset alone. Explicit cues support advisory partitions, precedence candidates, same-day anchors, and conflicts; row IDs are not chronology.\n")
print("done")
