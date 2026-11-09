#!/usr/bin/env python3
"""Build a row-level evidence graph from Swarm Traces filtered data.

Rows are the only graph entities. Marker, parent, exact-text, normalized text,
and endpoint links are retained as row-to-row bridge edges with explicit
triggers. Structural normalization is deliberately auditable and does not strip
or collapse numeric identifiers.
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import time

ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SOURCE = ROOT / "Data" / "redacted_filtered.jsonl"
OUT_DIR = ROOT / "forensics" / "run_2026" / "core"
LOG = ROOT / "forensics" / "run_2026" / "reconstruction_log.jsonl"
TOKEN_RE = re.compile(r"\[[^\]]{1,200}\]")


def canonical_text(text: str) -> str:
    # Approved dtype/alias normalizations only.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.lower()
    text = re.sub(r"(?<!\w)hugging\s+face(?!\w)", "huggingface", text)
    text = re.sub(r"(?<!\w)hf(?!\w)", "huggingface", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generic_marker(marker: str) -> bool:
    low = marker.lower().strip("[]").strip()
    return (
        marker in ("[ENCODED BLOB]", "[REDACTED SENSITIVE CONTENT]")
        or marker == "[REDACTED REPOSITORY]"
        or marker == "[REDACTED PRIVATE HOST]"
        or low.startswith("redacted:runtime_identifier")
    )

def syntactic_slot_marker(marker: str) -> bool:
    return bool(re.fullmatch(r"\[\d+\]", marker)) or marker in ("['token']", "[i]", "[k]", "[rstatus]", "[key]")

def is_endpoint_marker(marker: str) -> bool:
    low = marker.lower()
    return (
        marker.startswith(("[PROXY ", "[SHORTENER URL ", "[SERVICE HOST ", "[IP ADDRESS ", "[REDACTED:destination:", "[REDACTED:network_address:", "[REDACTED PRIVATE HOST]"))
        or low.startswith("[REDACTED:destination:")
        or low.startswith("http://")
    )



report = {
    "source": str(SOURCE),
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "rows_processed": 0,
    "distinct_ids": 0,
    "duplicate_ids": 0,
    "rows_with_parent": 0,
    "parents_in_scope": 0,
    "exact_text_groups": 0,
    "exact_text_rows": 0,
    "exact_bridge_edges": 0,
    "normalized_groups": 0,
    "normalized_bridge_rows": 0,
    "normalized_bridge_edges": 0,
    "marker_spelling_groups": 0,
    "marker_groups_with_repeats": 0,
    "marker_bridge_edges": 0,
    "parent_direct_edges": 0,
    "parent_sibling_edges": 0,
    "total_edges": 0,
    "components": 0,
    "singletons": 0,
    "largest_component": 0,
    "component_top_25": [],
    "edge_type_counts": {},
}

rows_by_id = {}
positions = {}
text_groups = {}
norm_groups = {}
marker_groups = {}
seen_edges = set()
edges_written = 0
union_parent = {}


def find(x):
    union_parent.setdefault(x, x)
    while union_parent[x] != x:
        union_parent[x] = union_parent[union_parent[x]]
        x = union_parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        union_parent[ra] = rb


def write_edge(f, source, target, edge_type, proof):
    global edges_written
    if source == target:
        return False
    key = (source, target, edge_type)
    if key in seen_edges:
        return False
    seen_edges.add(key)
    obj = {
        "source": source,
        "target": target,
        "edge_type": edge_type,
        "proof": proof,
    }
    f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
    edges_written += 1
    if source in union_parent and target not in union_parent:
        pass
    return True


def bridge_group(f, members, edge_type, trigger_prefix):
    members = sorted(members, key=lambda rid: (positions[rid] if rid in positions else 0, rid))
    for left, right in zip(members, members[1:]):
        write_edge(
            f,
            left,
            right,
            edge_type,
            f"{trigger_prefix} rows={len(members)}",
        )


# Read filtered source and index it.
with SOURCE.open("r", encoding="utf-8") as f:
    for position, raw in enumerate(f):
        if not raw.strip():
            continue
        row = json.loads(raw, strict=False)
        rid = row["id"]
        if rid in rows_by_id:
            raise RuntimeError(f"duplicate sample ID: {rid}")
        text = row.get("text", "")
        nodes = {
            "id": rid,
            "position": position,
            "mechanical_kind": row.get("kind"),
            "parent_id": row.get("parent_id"),
            "text_length": len(text),
            "text_sha256": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(),
            "canonical_sha256": hashlib.sha256(
                canonical_text(text).encode("utf-8", "replace")
            ).hexdigest(),
            "markers": sorted(set(re.findall(r"\[[^\]]{1,200}\]", text))),
        }
        rows_by_id[rid] = nodes
        positions[rid] = position
        text_groups.setdefault(nodes["text_sha256"], []).append(rid)
        norm_groups.setdefault(nodes["canonical_sha256"], []).append(rid)
        for marker in nodes["markers"]:
            marker_groups.setdefault(marker, []).append(rid)

report["rows_processed"] = len(rows_by_id)
report["distinct_ids"] = len(rows_by_id)
report["rows_with_parent"] = sum(bool(v["parent_id"]) for v in rows_by_id.values())

OUT_DIR.mkdir(parents=True, exist_ok=True)
nodes_path = OUT_DIR / "core_rows.ndjson"
edges_path = OUT_DIR / "core_edges.ndjson"

# Write small row index.
with nodes_path.open("w", encoding="utf-8") as out:
    for rid in sorted(rows_by_id, key=lambda x: (positions[x], x)):
        out.write(json.dumps(rows_by_id[rid], ensure_ascii=False, separators=(",", ":")) + "\n")

# Build row-to-row graph.
with edges_path.open("w", encoding="utf-8") as out_edges:
    # Parent chains.
    groups_by_parent = collections.defaultdict(list)
    for rid in rows_by_id:
        parent_id = rows_by_id[rid]["parent_id"]
        if parent_id is not None:
            write_edge(out_edges, parent_id, rid, "PARENT_DIRECT", f"stored parent_id={parent_id}")

    for rid in rows_by_id:
        parent_id = rows_by_id[rid]["parent_id"]
        if parent_id is not None:
            groups_by_parent[parent_id].append(rid)

    for parent_id, members in sorted(groups_by_parent.items(), key=lambda kv: str(kv[0])):
        if len(members) >= 2:
            bridge_group(out_edges, members, "SAME_PARENT_SIBLING", f"shared_parent={parent_id}")

    # Exact body links. Every exact duplicate group becomes a chain of
    # direct row edges, which preserves component reachability.
    exact_groups = 0
    exact_rows = 0
    for digest, members in sorted(
        text_groups.items(), key=lambda kv: (-len(kv[1]), kv[0])
    ):
        if len(members) >= 2:
            exact_groups += 1
            exact_rows += len(members)
            bridge_group(
                out_edges,
                members,
                "EXACT_BODY",
                f"text_sha256={digest}",
            )
    report["exact_text_groups"] = exact_groups
    report["exact_text_rows"] = exact_rows
    report["exact_bridge_edges"] = None

    # Normalized replay: same approved normalized text, different raw bodies.
    replay_groups = 0
    replay_rows = 0
    for digest, members in sorted(
        norm_groups.items(), key=lambda kv: (-len(kv[1]), kv[0])
    ):
        if len(members) < 2:
            continue
        raw_classes = {}
        for rid in members:
            raw_classes.setdefault(rows_by_id[rid]["text_sha256"], []).append(rid)
        if len(raw_classes) < 2:
            continue
        replay_groups += 1
        replay_rows += sum(len(v) for v in raw_classes.values())
        representatives = sorted([raw_classes[k][0] for k in raw_classes], key=lambda r: (positions[r], r))
        bridge_group(
            out_edges,
            representatives,
            "NORMALIZED_REPLAY",
            f"canonical_sha256={digest}; raw_class_count={len(raw_classes)}",
        )
    report["normalized_groups"] = replay_groups
    report["normalized_bridge_rows"] = replay_rows

    # Marker links use exact bracket strings after generic placeholder removal.
    # Endpoint markers are reported separately, without dropping them from links.
    marker_groups_with_repeats = 0
    marker_rows = 0
    marker_classification_counts = {}
    for marker, members in sorted(
        marker_groups.items(), key=lambda kv: (-len(kv[1]), kv[0])
    ):
        if generic_marker(marker) or syntactic_slot_marker(marker):
            continue
        classification = "MARKER_ENDPOINT" if is_endpoint_marker(marker) else "MARKER_SAME"
        marker_classification_counts[classification] = marker_classification_counts.get(classification, 0) + 1
        if len(members) < 2:
            continue
        marker_groups_with_repeats += 1
        marker_rows += len(members)
        bridge_group(out_edges, members, classification, marker)
    report["marker_spelling_groups"] = len(marker_groups)
    report["marker_groups_with_repeats"] = marker_groups_with_repeats
    report["marker_represented_rows"] = marker_rows
    report["marker_classification_counts"] = marker_classification_counts
    report["marker_rows_used"] = marker_rows

    report["parents_present"] = sum(
        1
        for parent in {v["parent_id"] for v in rows_by_id.values() if v["parent_id"]}
        if parent in rows_by_id
    )

edge_type_counts = {}
for line in edges_path.read_text().splitlines():
    obj = json.loads(line)
    edge_type_counts[obj["edge_type"]] = edge_type_counts.get(obj["edge_type"], 0) + 1

report["edge_type_counts"] = dict(sorted(edge_type_counts.items()))
report["total_edges"] = len(edges_path.read_text().splitlines())
report["parent_direct_edges"] = edge_type_counts.get("PARENT_DIRECT", 0)
report["parent_sibling_edges"] = edge_type_counts.get("SAME_PARENT_SIBLING", 0)
report["exact_text_bridge_edges"] = edge_type_counts.get("EXACT_BODY", 0)
report["normalized_bridge_edges"] = edge_type_counts.get("NORMALIZED_REPLAY", 0)
report["marker_bridge_edges"] = edge_type_counts.get(
    "MARKER_SAME", 0
) + edge_type_counts.get("MARKER_ENDPOINT", 0)

# Components from the core row graph.
union_parent = {rid: rid for rid in rows_by_id}


def find(x):
    union_parent.setdefault(x, x)
    while union_parent[x] != x:
        union_parent[x] = union_parent[union_parent[x]]
        x = union_parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        union_parent[ra] = rb


for line in edges_path.read_text().splitlines():
    edge_obj = json.loads(line)
    if edge_obj["source"] in union_parent and edge_obj["target"] in union_parent:
        find(edge_obj["source"])
        find(edge_obj["target"])
        union(edge_obj["source"], edge_obj["target"])
for rid in rows_by_id:
    find(rid)

component_sizes = {}
for rid in rows_by_id:
    comp = find(rid)
    component_sizes[comp] = component_sizes.get(comp, 0) + 1
sizes = sorted(component_sizes.values(), reverse=True)
report["components"] = len(component_sizes)
report["singletons"] = sum(1 for size in sizes if size <= 1)
report["largest_component"] = max(sizes) if sizes else 0
report["component_top_25"] = sizes[:25]

edges_written_final = sum(1 for _ in edges_path.open())

stats_path = OUT_DIR / "graph_core_stats.json"
with stats_path.open("w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

LOG.parent.mkdir(parents=True, exist_ok=True)
log_entry = {
    "step": "build_graph_core_v1",
    "source": str(SOURCE),
    "source_sha256": report["source_sha256"],
    "rows": report["rows_processed"],
    "edges": report["total_edges"],
    "components": report["components"],
    "largest_component": report["largest_component"],
    "status": "complete",
    "timestamp": report["generated_at"],
}
with LOG.open("a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

print(json.dumps(report, indent=2, ensure_ascii=False))
print("edges=", edges_written_final, "edges_path=", edges_path)
print("nodes=", nodes_path)
