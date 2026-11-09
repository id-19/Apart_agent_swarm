import json
import re
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path("Data/redacted.jsonl")
OUT = Path("/Users/id19/scratchpad/canonical_normalize_v2_groups.json")

ALIASES = [
    (r"\bhf[-_]repo\b", "HUGGINGFACE_REPO"),
    (r"\bhf[-_ ]repo\b", "HUGGINGFACE_REPO"),
    (r"\bhugging\s+face\b", "HUGGINGFACE"),
    (r"\bhf\b", "HUGGINGFACE"),
    (r"\bdestination\b", "DEST"),
    (r"\bshortener[-_ ]?url\b", "SHORTENER"),
    (r"\bproxy[-_ ]?url\b", "PROXY"),
    (r"\bservice[-_ ]?url\b", "SERVICE"),
    (r"\bartifactory\b", "ARTIFACTORY"),
]

PLACEHOLDER = re.compile(r"\[[^\]]+\]")
COUNTER = re.compile(r"(\d{3,})")

def normalize(text):
    s = text or ""
    low = s.lower()
    low = PLACEHOLDER.sub("PLACEHOLDER_TOKEN", low)
    low = COUNTER.sub("N", low)
    for a, b in ALIASES:
        low = re.sub(a, b, low)
    low = re.sub(r"\s+", " ", low).strip()
    low = low.replace(" ", "")
    return low, hashlib.sha256(low.encode()).hexdigest()

groups = defaultdict(list)
with DATA.open() as f:
    for line in f:
        if not line.strip():
            continue
        r = json.loads(line)
        _, h = normalize(r.get("text", ""))
        groups[h].append(r["id"])

rows = sum(len(v) for v in groups.values())
repeat = {h: v for h, v in groups.items() if len(v) >= 2}
print("rows", rows)
print("unique sigs", len(groups))
print("repeat groups", len(repeat))
print("rows in repeat groups", sum(len(v) for v in repeat.values()))
print("repeat rate", round(sum(len(v) for v in repeat.values()) / rows * 100, 2))
print("repeat group size dist", Counter(len(v) for v in repeat.values()).most_common(12))
payload = {
    "rows": rows,
    "unique_sigs": len(groups),
    "repeat_groups": len(repeat),
    "repeat_rows": sum(len(v) for v in repeat.values()),
    "repeat_rate": round(sum(len(v) for v in repeat.values()) / rows * 100, 2),
}
OUT.write_text(__import__("json").dumps(payload, indent=2), encoding="utf-8")
print("wrote", OUT)
