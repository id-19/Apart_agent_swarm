# Reads Data/redacted.jsonl and assigns broad functional family by textual markers.
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "Data" / "redacted.jsonl"
OUTCSV = ROOT.parent / "scratchpad" if False else Path("/Users/id19/scratchpad")
OUTCSV.mkdir(parents=True, exist_ok=True)

def classify(text: str) -> str:
    low = text.lower()
    if "manifests/latest" in low or "v2/" in low and "pushblob" in low:
        return "DOCKER-REGISTRY-PUSH"
    if "socket,ssl" in low or "pushblob" in low or "auth.docker.io" in low or "registry-1.docker.io" in low:
        return "PYTHON-REGISTRY-PUSH"
    if "sqlite3_initialize" in text and (";" in text or "file_path" in low) and ("curl" in low or "python3" in low or "echo " in low):
        return "CYBERGYM-SHELL-INJECTION"
    if "mkcol" in low or "github-remote-cache/zz" in low or "github-remote/zz" in low:
        return "ARTIFACTORY-DEAD-DROP-WRITE"
    if "decompressionstream(\"gzip\")" in low or "eval(atob" in low or "eval(" in low and "atob" in low:
        return "JS-DIRECTORY-REASSEMBLE-EVAL"
    if "shortener url" in low or "proxy 4 url" in low or "proxy 5 url" in low:
        return "JS-FETCH-AND-REPORT-SHORTENER"
    if "<iframe" in low or "<img" in low or "document.body.append(i)" in low:
        return "HTML-SCRIPT-IMAGE-INJECTION"
    if "tar member" in low or "encoded blob" in low:
        return "TAR-BLOB-DERIVED-ARCHIVE"
    if "zz" in low and ("fetch(" in low or "xmlhttprequest" in low):
        return "ARTIFACTORY-PATH-PROBE-OR-RELAY"
    return "OTHER/UNCLASSIFIED"

rows = []
with DATA.open() as f:
    for line in f:
        if not line.strip():
            continue
        o = json.loads(line)
        family = classify(o["text"])
        rows.append((o["id"], family, o.get("kind")))

# Sequence histograms.
bins = []
bin_size = 1000
for start in range(0, len(rows), bin_size):
    segment = rows[start:start+bin_size]
    counts = Counter(f for _, f, _ in segment)
    bins.append((start+1, start+len(segment), counts))
rows_of_children = Counter()

# Print compact.
for start, end, counts in bins[:15]:
    print(f"IDs {start:6}-{end:6}", dict(sorted(counts.items())))
print("...")
for start, end, counts in bins[-3:-1] + [bins[-1]]:
    print(f"IDs {start:6}-{end:6}", dict(sorted(counts.items())))

# write CSV, all rows.
p = Path("/Users/id19/scratchpad/functional_group_rows.csv")
with p.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "family", "kind", "bin"])
    for idx, (rid, fam, kind) in enumerate(rows):
        w.writerow([rid, fam, kind, idx // bin_size * bin_size + 1])
print("wrote", p)
print("TOTAL FAMILY COUNT:", dict(Counter(f for _, f, _ in rows)))
