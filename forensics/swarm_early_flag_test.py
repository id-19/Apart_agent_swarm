from __future__ import annotations
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

TOKEN_RE = re.compile(r"\[[A-Z][A-Z0-9 _:-]*?\]|zz[A-Za-z0-9_]{4,}")
DATA = Path("Data/redacted.jsonl")
OUT = Path("/Users/id19/scratchpad/swarm_early_flag_test.json")
row_order = []
token_events = defaultdict(lambda: None)
field = lambda r: sorted(set(TOKEN_RE.findall(r.get("text", "") or "")))
first_multi = []
prefixes = [500, 1000, 2000, 5000, 10000, 189579]
prefix_results = {}

with DATA.open("r", encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
        if not line.strip():
            continue
        r = json.loads(line)
        row_order.append(r["id"])
        toks = field(r)
        for t in toks:
            if token_events[t] is None:
                token_events[t] = [i]
            else:
                token_events[t].append(i)
prefix_counts = {p: 0 for p in prefixes}
tokens_that_repeated = [t for t, locs in token_events.items() if len(locs) >= 2]
first_repeat_rows = []
for t in tokens_that_repeated:
    loc = token_events[t]
    if len(loc) >= 2:
        first_repeat_rows.append((loc[1], loc[0], t, loc))
first_repeat_rows.sort()
prefix_cumulative = {}
cum = 0
for p in prefixes:
    # number of tokens with at least two appearances in first p rows
    cum = sum(1 for _, __, ___, locs in first_repeat_rows if locs[1] <= p)
    prefix_cumulative[p] = cum

first_20_repeats = first_repeat_rows[:20]
outdoc = {
    "rows_total": len(row_order),
    "tracked_token_types": len(token_events),
    "token_types_repeated": len(tokens_that_repeated),
    "shared_markers_by_prefix": prefix_cumulative,
    "firsttwenty_repeating_markers": [
        {"first_second_occurrence_at_row_index": a, "first_occurrence_row_index": b, "marker": c, "all_occurrence_indices": d[:8]}
        for a, b, c, d in first_20_repeats
    ],
}
OUT.write_text(json.dumps(outdoc, indent=2), encoding="utf-8")

print("tracked tokens:", len(token_events))
print("tokens repeated:", len(tokens_that_repeated))
print("shared marker count by prefix:", prefix_cumulative)
print("top first repeats:", [(c, a) for a, b, c, d in first_20_repeats][:10])
