#!/usr/bin/env python3
"""Replace files over 50 MB with lossless 45 MB parts for GitHub upload.

Parts concatenate byte-for-byte to recreate each original.  The manifest is
written at the repository root and is consumed by reassemble_large_files.py.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIMIT = 50_000_000
PART_SIZE = 45_000_000
MANIFEST = ROOT / "large_file_parts_manifest.json"

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

records = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or ".git" in path.relative_to(ROOT).parts:
        continue
    if path.name in {MANIFEST.name, "reassemble_large_files.py", "split_large_files.py"}:
        continue
    size = path.stat().st_size
    if size <= LIMIT:
        continue
    rel = path.relative_to(ROOT).as_posix()
    source_hash = digest(path)
    parts = []
    with path.open("rb") as src:
        index = 0
        while True:
            block = src.read(PART_SIZE)
            if not block:
                break
            part = path.with_name(f"{path.name}.part-{index:03d}")
            part.write_bytes(block)
            parts.append({"path": part.relative_to(ROOT).as_posix(), "bytes": len(block)})
            index += 1
    if sum(p["bytes"] for p in parts) != size:
        raise RuntimeError(f"part size mismatch for {rel}")
    path.unlink()
    records.append({"original": rel, "bytes": size, "sha256": source_hash, "parts": parts})

MANIFEST.write_text(json.dumps({"part_bytes": PART_SIZE, "files": records}, indent=2) + "\n")
print(json.dumps({"files_split": len(records), "parts": sum(len(r["parts"]) for r in records), "manifest": str(MANIFEST)}))
