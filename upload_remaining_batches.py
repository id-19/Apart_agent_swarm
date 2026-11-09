#!/usr/bin/env python3
"""Commit and push remaining untracked files in <=60 MB batches."""
from __future__ import annotations

import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
paths = subprocess.check_output(
    ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=root
).decode().split("\0")
files = []
for raw in paths:
    if not raw or Path(raw).name == ".DS_Store":
        continue
    path = root / raw
    if path.is_file():
        files.append((raw, path.stat().st_size))

groups: list[list[str]] = []
current: list[str] = []
current_size = 0
for raw, size in files:
    if current and current_size + size > 60_000_000:
        groups.append(current)
        current, current_size = [], 0
    current.append(raw)
    current_size += size
if current:
    groups.append(current)

for index, group in enumerate(groups, 1):
    subprocess.run(["git", "add", "--", *group], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", f"Add recovered research files batch {index:02d}"], cwd=root, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=root, check=True)
    print(f"pushed batch {index}/{len(groups)} ({len(group)} files)", flush=True)
