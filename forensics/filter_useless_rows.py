import json
from pathlib import Path

SRC = Path("Data/redacted.jsonl")
DST = Path("Data/redacted_filtered.jsonl")
TRIVIAL = {
    "[ENCODED BLOB]",
    "[REDACTED OPAQUE BINARY CONTENT]",
    "[REDACTED:binary_padding; exact source text retained privately]",
}

removed = 0
kept = 0
with SRC.open() as inp, DST.open("w") as out:
    for line in inp:
        if not line.strip():
            continue
        r = json.loads(line)
        t = (r.get("text") or "").strip()
        if t in TRIVIAL or t == "":
            removed += 1
            continue
        if len(t) < 4:
            removed += 1
            continue
        out.write(json.dumps(r, ensure_ascii=False) + "\n")
        kept += 1

print("removed", removed)
print("kept", kept)
print("written", DST)
