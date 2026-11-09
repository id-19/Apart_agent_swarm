#!/usr/bin/env python3
"""Recreate files listed in large_file_parts_manifest.json from their parts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "large_file_parts_manifest.json").read_text())
for record in manifest["files"]:
    target = ROOT / record["original"]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as out:
        for part in record["parts"]:
            with (ROOT / part["path"]).open("rb") as src:
                while block := src.read(1024 * 1024):
                    out.write(block)
    h = hashlib.sha256()
    with target.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    if target.stat().st_size != record["bytes"] or h.hexdigest() != record["sha256"]:
        raise RuntimeError(f"verification failed for {record['original']}")
    print(f"reassembled {record['original']}")
