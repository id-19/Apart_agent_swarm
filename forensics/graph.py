"""Clean reference implementation of the Swarm Traces row graph schema.

This is intentionally a spec-first, evidence-first implementation. It is meant to
make the instrumentation rules explicit without depending on the generated
projection artifacts.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "Data" / "redacted_filtered.jsonl"

TOKEN_RE = re.compile(r"\[[^\]]{1,200}\]")
FUNCTION_RE = re.compile(r'"function_name"\s*:\s*"([^"]*)"\s*')

ALIASES = ("hugging face", "hf")
ALIAS_REPLACEMENT = "huggingface"


def canonical_text(text: str) -> str:
    """Approved semantic normalization. Additional rewrites are prohibited."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").lower()
    for alias in ALIASES:
        text = re.sub(rf"(?<!\w){re.escape(alias)}(?!\w)", ALIAS_REPLACEMENT, text)
    return re.sub(r"\s+", " ", text).strip()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


@dataclass(frozen=True)
class Row:
    id: str
    position: int
    kind: str | None
    parent_id: str | None
    text: str
    text_sha256: str
    canonical_sha256: str
    markers: tuple[str, ...]


def build_row_index() -> dict[str, Row]:
    rows: dict[str, Row] = {}
    for position, raw in enumerate(DATA.open(encoding="utf-8")):
        if not raw.strip():
            continue
        obj = json.loads(raw, strict=False)
        text = obj.get("text", "")
        rid = obj["id"]
        if rid in rows:
            raise ValueError(f"duplicate row id: {rid}")
        rows[rid] = Row(
            id=rid,
            position=position,
            kind=obj.get("kind"),
            parent_id=obj.get("parent_id"),
            text=text,
            text_sha256=sha256(text),
            canonical_sha256=sha256(canonical_text(text)),
            markers=tuple(sorted(set(TOKEN_RE.findall(text)))),
        )
    return rows


def is_generic_marker(marker: str) -> bool:
    low = marker.lower()
    return (
        marker in {"[ENCODED BLOB]", "[REDACTED SENSITIVE CONTENT]",
                   "[REDACTED REPOSITORY]", "[REDACTED PRIVATE HOST]"}
        or low.startswith("[redacted:runtime_identifier")
    )


def is_syntactic_slot(marker: str) -> bool:
    return bool(re.fullmatch(r"\[\d+\]", marker)) or marker in (
        "['token']", "[i]", "[k]", "[rstatus]", "[key]"
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
