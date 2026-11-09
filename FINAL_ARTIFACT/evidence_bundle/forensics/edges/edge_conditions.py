"""Pure, explicit edge class conditions, triggers, and edge formulation.

This module is the authoritative spec for how an edge is formed. It deliberately
does not execute over the dataset. Generators and projections must keep their
emitted fields consistent with the schema defined here.
"""

from __future__ import annotations

import dataclasses
import re
from typing import Callable

# Concrete, retained row-graph families. TIME_DEPENDENCY is deliberately absent:
# timestamp co-occurrence is retained only as timestamp-anchor inventory metadata,
# not as a relation family.
EDGE_CLASSES = (
    "EXACT_BODY",
    "NORMALIZED_REPLAY",
    "PARENT_DIRECT",
    "SAME_PARENT_SIBLING",
    "MARKER_SAME",
    "MARKER_ENDPOINT",
    "INTENT_SIGNATURE",
    "PARENT_MUTATION",
    "TIMESTAMP_ANCHOR",
    "NEAR_BODY_D1",
    "NEAR_BODY_D2",
    "NEAR_BODY_D3",
)

# Genuinely directed classes: stored parent/child or concrete temporal order.
DIRECTED_CLASSES = {"PARENT_DIRECT", "PARENT_MUTATION", "TIMESTAMP_ANCHOR"}
# Structurally symmetric classes. They are emitted once in row-position order but
# carry an explicit direction marker instead of inventing a reverse assertion.
SYMMETRIC_CLASSES = set(EDGE_CLASSES) - DIRECTED_CLASSES

EDGE_DIRECTIONS = {cls: ("directed" if cls in DIRECTED_CLASSES else "symmetric") for cls in EDGE_CLASSES}

TOKEN_RE = re.compile(r"\[[^\]]{1,200}\]")
NUMERIC_SLOT_RE = re.compile(r"\[\d+\]")


def is_generic_marker(marker: str) -> bool:
    low = marker.lower()
    return (
        marker in {
            "[ENCODED BLOB]",
            "[REDACTED SENSITIVE CONTENT]",
            "[REDACTED REPOSITORY]",
            "[REDACTED PRIVATE HOST]",
        }
        or low.startswith("[redacted:runtime_identifier")
    )


def is_syntactic_slot_marker(marker: str) -> bool:
    # Excluded syntactic markers are bare numeric brackets and these exact tokens.
    return bool(NUMERIC_SLOT_RE.fullmatch(marker)) or marker in (
        "['token']", "[i]", "[k]", "[rstatus]", "[key]",
    )


def is_endpoint_marker(marker: str) -> bool:
    low = marker.lower()
    return (
        marker.startswith((
            "[PROXY ", "[SHORTENER URL ", "[SERVICE HOST ", "[IP ADDRESS ",
            "[REDACTED:destination:", "[REDACTED:network_address:",
            "[REDACTED PRIVATE HOST]",
        ))
        or low.startswith("[redacted:destination:")
        or marker.startswith("http://")
    )


@dataclasses.dataclass(frozen=True)
class Edge:
    source: str
    target: str
    edge_class: str
    trigger: str
    evidence: str
    direction: str = "directed"
    source_id: str | None = None
    destination_id: str | None = None
    distance: int | None = None

    def __post_init__(self):
        if self.source_id is None:
            object.__setattr__(self, "source_id", self.source)
        if self.destination_id is None:
            object.__setattr__(self, "destination_id", self.target)
        if self.edge_class not in EDGE_CLASSES:
            raise ValueError(f"unknown edge class: {self.edge_class}")
        expected = "directed" if self.edge_class in DIRECTED_CLASSES else "symmetric"
        if self.direction not in {"directed", "symmetric", "bidirectional"}:
            raise ValueError(f"invalid direction: {self.direction}")
        # Prevent silently mislabeling a symmetric class as directed.
        if self.edge_class in SYMMETRIC_CLASSES and self.direction == "directed":
            raise ValueError(f"{self.edge_class} may not be marked directed")


def edge_row(edge: Edge) -> dict:
    """Canonical four-field JSONL row. All detail belongs in the nested object."""
    return {
        "source": edge.source,
        "dest": edge.target,
        "edge_class": edge.edge_class,
        "edge_sub_class": {
            "source_id": edge.source_id,
            "destination_id": edge.destination_id,
            "source": edge.source,
            "target": edge.target,
            "trigger": edge.trigger,
            "distance": edge.distance,
            "direction": edge.direction,
            "residual_detail": edge.evidence,
        },
    }

def parent_direct(source: str, target: str, trigger: str) -> Edge:
    return Edge(source, target, "PARENT_DIRECT", trigger, "explicit stored parent_id", "directed")


def parent_mutation(source: str, target: str, trigger: str) -> Edge:
    return Edge(source, target, "PARENT_MUTATION", trigger, "parent/child text differs", "directed")


def timestamp_anchor(source: str, target: str, trigger: str, distance: int | None = None) -> Edge:
    return Edge(source, target, "TIMESTAMP_ANCHOR", trigger, "explicit timestamp anchor", "directed", distance=distance)


def same_sibling(source: str, target: str, parent: str) -> Edge:
    return Edge(source, target, "SAME_PARENT_SIBLING", f"shared_parent={parent}",
                f"both rows are distinct children of {parent}", "symmetric")


def marker_same(source: str, target: str, marker: str, occurrences: int) -> Edge:
    return Edge(source, target, "MARKER_SAME", marker,
                f"shared exact marker {marker}; occurrences={occurrences}", "symmetric")


def marker_endpoint(source: str, target: str, marker: str, occurrences: int) -> Edge:
    return Edge(source, target, "MARKER_ENDPOINT", marker,
                f"shared route/destination marker {marker}; occurrences={occurrences}",
                "symmetric")


def exact_body(source: str, target: str, digest: str, body_length: int) -> Edge:
    return Edge(source, target, "EXACT_BODY", f"text_sha256={digest}",
                f"byte-identical body length={body_length}", "symmetric", distance=0)


def normalized_replay(source: str, target: str, canonical_digest: str, raw_class_count: int) -> Edge:
    return Edge(source, target, "NORMALIZED_REPLAY",
                f"canonical_sha256={canonical_digest}; raw_class_count={raw_class_count}",
                "approved synonym/whitespace rewrite only; raw_sha256 differs", "symmetric")


def intent_signature(source: str, target: str, signature: str) -> Edge:
    return Edge(source, target, "INTENT_SIGNATURE", signature,
                f"shared operation signature: {signature[:160]}", "symmetric")


def near_body(source: str, target: str, distance: int) -> Edge:
    if distance not in (1, 2, 3):
        raise ValueError("NEAR_BODY distance must be 1, 2, or 3")
    return Edge(source, target, f"NEAR_BODY_D{distance}", f"levenshtein_distance={distance}",
                f"normalized body distance={distance}", "symmetric", distance=distance)
