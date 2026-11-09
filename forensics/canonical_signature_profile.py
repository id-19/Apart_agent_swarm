import json
import re
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "Data" / "redacted.jsonl"
ALIASES = {
    "hf": "HUGGINGFACE",
    "hf repo": "HUGGINGFACE REPO",
    "hf_repo": "HUGGINGFACE REPO",
    "huggingface": "HUGGINGFACE",
    "hugging face": "HUGGINGFACE",
    "destination": "DESTINATION",
    "service": "SERVICE",
    "proxy": "PROXY",
    "shortener": "SHORTENER",
    "artifactory": "ARTIFACTORY",
    # executable/archive trivial blobs are semantically meaningless
}
TRIVIAL = {"[ENCODED BLOB]", "[REDACTED SENSITIVE CONTENT]", "[ENCODED ARCHIVE]", "[ENCODED BLOB?]"}

def normalize(text):
    s = text.lower()
    # normalize explicit redaction placeholders
    s = re.sub(r"\[redacted:\s*[^]]+\]", "[REDACTED]", s)
    s = re.sub(r"\[(encoded blob|redacted [a-z ]+)\]", "[TRIVIAL]", s)
    # collapse numeric IDs in placeholder handles
    s = re.sub(r"(\[[A-Z_]+)(\d+)", r"\1_N", s)
    # normalize one-off operator tokens
    s = s.replace("huggingface", "HUGGINGFACE").replace("hugging face", "HUGGINGFACE")
    s = s.replace("hf repo", "HUGGINGFACE REPO").replace("hf_repo", "HUGGINGFACE REPO")
    # squeeze whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

def signature(row):
    t = normalize(row.get("text", ""))
    # keep marketplace marker families, excluding trivial construct-only semantics
    markers = sorted(set(m for m in re.findall(r"\[[A-Z_]+(?:_N)?\]|\bzz[A-Za-z0-9_]{4,}\b", t) if m not in TRIVIAL))
    return (len(t), tuple(markers), hashlib.sha256(t.encode()).hexdigest())

groups = defaultdict(list)
with DATA.open() as f:
    for line in f:
        if not line.strip():
            continue
        r = json.loads(line)
        sig = signature(r)
        groups[sig].append(r["id"])

counts = {k: len(v) for k, v in groups.items() if len(v) >= 2}
rows = sum(counts.values())
print("rows:", sum(1 for _ in DATA.open()))
print("unique canonical sigs:", len(groups))
print("repeat groups:", len(counts))
print("rows in repeat groups:", rows)
print("repeat rate:", round(rows / 189579 * 100, 2), "%")
# top groups by size
top = sorted(counts.items(), key=lambda x: -x[1])[:12]
for key, n in top:
    print(f"  {n:5} sig_len={key[0]:4}")
# write summary
p = Path("/Users/id19/scratchpad/canonical_normalized_clusters.json")
import json as j
payload = {
    "rows": rows,
    "unique_groups": len(groups),
    "repeat_groups": len(counts),
    "repeat_rows": rows,
    "example": {f"{k[0]}|{k[1][:3]}|{k[2]}" : n for k, n in list(counts.items())[:50]},
}
p.write_text(j.dumps(payload, indent=2), encoding="utf-8")
print("wrote", p)