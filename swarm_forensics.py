#!/usr/bin/env python3
"""Forensic reconstruction over the redacted Swarm Traces dataset.

Input: Data/redacted.jsonl
Outputs:
  forensics/baseline.json
  forensics/cluster_summary.csv
  forensics/chain_events.csv
  forensics/salient.json
  forensics/early_detection.json
  forensics/communication_graph.csv
"""
from __future__ import annotations

import csv, hashlib, json, re, statistics
from collections import Counter, defaultdict
from pathlib import Path
import polars as pl

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Data" / "redacted.jsonl"
OUT = ROOT / "forensics"
OUT.mkdir(exist_ok=True)

PLACEHOLDER_RX = re.compile(r"\[([A-Z][A-Z0-9 _:-]*?)\]")

def family(text: str) -> list[str]:
    tl = text.lower()
    return sorted({
        "link" if ("shortener" in tl or "document.write" in tl or "script src=" in tl or "location.hash" in tl) else None,
        "api" if ("fetch(" in tl or "xmlhttprequest" in tl) else None,
        "img" if ("new image" in tl or "i.src=" in tl) else None,
        "eval" if ("eval(" in tl or "atob(" in tl or "fromcharcode" in tl) else None,
        "cmd" if ("src/main.c" in tl or "uname -a" in tl or "/proc/1/status" in tl or ";id;" in tl) else None,
        "canvas" if ("canvas" in tl) else None,
    } - {None})

def normalize(t: str) -> str:
    substitutions = [
        (r"\[REDACTED:source_identifier:[^\]]*\]", "[source]"),
        (r"\[REDACTED:runtime_identifier(?::[^\]]*)?\]", "[runtime]"),
        (r"\[REDACTED:destination:[^\]]*\]", "[destination]"),
        (r"\[REDACTED:[^\]]*\]", "[redacted]"),
        (r"\[SERVICE \d+ URL \d+\]", "[service]"),
        (r"\[SHORTENER [^\]]*\]", "[shortener]"),
        (r"\[PROXY \d+ URL \d+\]", "[proxy]"),
        (r"\[ENCODED BLOB(?: \d+)?\]", "[blob]"),
        (r"\[CREDENTIAL [^\]]*\]", "[credential]"),
        (r"\[HF REPO [^\]]*\]", "[hf-repo]"),
    ]
    for rx, rep in substitutions:
        t = re.sub(rx, rep, t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip()

def digest(s: str, n: int = 16) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:n]

def first_texts(text, rx):
    return rx.findall(text)[:8]

def primary_endpoint(t: str) -> str:
    for rx in [r"\[REDACTED:destination:\d+\]", r"\[SERVICE \d+ URL \d+\]", r"\[PROXY \d+ URL \d+\]"]:
        m = re.search(rx, t)
        if m: return m.group(0)
    urls = re.findall(r"https?://[^\s'\"<>]+", t)
    return urls[0] if urls else "unknown"

print("Loading...")
df = pl.read_ndjson(DATA, schema_overrides={"parent_id": pl.Utf8, "time_utc": pl.Utf8})
rows = df.to_dicts()
ids = [r["id"] for r in rows]
kind_by_id = {r["id"]: r["kind"] for r in rows}
text_by_id = {r["id"]: r["text"] for r in rows}
child_by_parent = defaultdict(list)
for r in rows:
    if r["parent_id"]:
        child_by_parent[r["parent_id"]].append(r["id"])
templates_seen = Counter()
fam_seen = Counter()
children_count = {r["id"]: len(child_by_parent.get(r["id"], [])) for r in rows if r["kind"] == "payload"}
norm_forms = Counter()
salient_markers = ["FANPASS_12345", "TINYOK", "CHAINWORKS", "cybergym", "sqlite3_initialize", "small quickchain families not needed"]

# Save row annotations
records = []
for r in rows:
    fams = family(r["text"])
    tmpl = digest(normalize(r["text"]))
    norm_forms[tmpl] += 1
    records.append({
        "id": r["id"],
        "cite": r["cite"],
        "kind": r["kind"],
        "parent_id": r["parent_id"],
        "length": len(r["text"]),
        "families": fams,
        "template": tmpl if r["kind"] == "payload" else None,
        "endpoint": primary_endpoint(r["text"]) if r["kind"] == "payload" else None,
        "children": child_by_parent.get(r["id"], []),
        "child_kinds": sorted({kind_by_id[x] for x in child_by_parent.get(r["id"], [])}),
        "markers": sorted({m for m in salient_markers if m in r["text"]}),
    })

# Base counts
baseline = {
    "rows": len(rows),
    "unique_ids": len(set(ids)),
    "duplicate_ids": len(rows) - len(set(ids)),
    "kinds": {k: sum(1 for r in records if r["kind"] == k) for k in sorted({r["kind"] for r in records})},
    "null_time_utc": sum(1 for r in rows if r["time_utc"] is None),
    "null_or_empty_tags": sum(1 for r in rows if (r["tags"] in (None, "", "None"))),
    "parented": sum(1 for r in records if r["parent_id"]),
    "unparented": sum(1 for r in records if not r["parent_id"]),
    "dangling_parents": sum(1 for r in records if r["parent_id"] and r["parent_id"] not in kind_by_id),
    "parent_ids_always_less": sum(1 for r in records if r["parent_id"] and r["parent_id"] < r["id"]),
    "family_rows_payload": sum(1 for r in records if r["kind"] == "payload" and r["families"]),
    "unclassified_payloads": sum(1 for r in records if r["kind"] == "payload" and not r["families"]),
    "template_count_payload": norm_forms.__len__(),
    "top_templates": norm_forms.most_common(10),
    "top_family": family.__name__,
}
with open(OUT / "baseline.json", "w") as f:
    json.dump(baseline, f, indent=2)

# Salient records
salient_ids = ["R0000001", "R0000021", "R0000027", "R0024455", "R0036471", "R0036645", "R0049534", "R0057512", "R0069699"]
salient = []
for rid in salient_ids:
    salient.append({
        "id": rid,
        "kind": kind_by_id.get(rid),
        "families": [r["families"] for r in records if r["id"] == rid][0],
        "children": len(child_by_parent.get(rid, [])),
        "child_kinds": sorted({kind_by_id[x] for x in child_by_parent.get(rid, [])}),
        "endpoint": primary_endpoint(text_by_id[rid]) if rid in text_by_id else None,
        "text_excerpt": text_by_id.get(rid, "")[:1200],
    })
# Marker scans
marker_rows = []
for m in salient_markers:
    rows_for = [r["id"] for r in records if m in r.get("markers", [])]  # markers already scanned macro list
    # redo explicitly for typos above
    for r in rows:
        if m in r["text"]:
            marker_rows.append({"marker": m, "id": r["id"], "kind": r["kind"], "parent": r["parent_id"], "families": None})
uniq = {}
for mr in marker_rows:
    # family annotation
    mr["families"] = family(text_by_id[mr["id"]])
marker_examples = defaultdict(list)
for m in salient_markers:
    for r in rows:
        if m in r["text"] and len(marker_examples[m]) < 3:
            marker_examples[m].append({"id": r["id"], "kind": r["kind"], "families": family(r["text"]), "children": len(child_by_parent.get(r["id"], []))})
salient.append({"marker_examples": {k: v for k, v in marker_examples.items()}})
with open(OUT / "salient.json", "w") as f:
    json.dump(salient, f, indent=2)

# Chain events and graph edges
with open(OUT / "chain_events.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["parent", "child", "parent_kind", "child_kind", "parent_children_for_parent", "child_has_parent"])
    for p, children in child_by_parent.items():
        for c in children:
            w.writerow([p, c, kind_by_id[p], kind_by_id[c], len(children), 1])

# Cluster summary: template + endpoint
groups = defaultdict(lambda: {"members": [], "children": 0, "child_kinds": Counter()})
for r in records:
    if r["kind"] != "payload":
        continue
    t = r["template"]; ep = r["endpoint"]
    key = f"{','.join(r['families'])}|{ep}|{t}"
    rec = groups[key]
    rec["members"].append(r["id"])
    rec["children"] += len(r["children"])
cluster_rows = []
for key, v in groups.items():
    cluster_rows.append({
        "cluster_key": key[:180],
        "size": len(v["members"]),
        "first_id": min(v["members"]),
        "last_id": max(v["members"]),
        "total_children": v["children"],
        "members_with_children": sum(1 for mid in v["members"] if child_by_parent.get(mid)),
        "families": ",".join(v["members"] and family(text_by_id[v["members"][0]]) or ""),
        "example_members": ";".join(v["members"][:5]),
    })
cluster_rows.sort(key=lambda x: (-x["size"], -x["total_children"]))
with open(OUT / "cluster_summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(cluster_rows[0].keys()))
    w.writeheader(); w.writerows(cluster_rows[:1000])

# communication graph: connected components via shared destinations and templates
parent = {i: i for i in ids}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
# parent-child edges
for r in rows:
    if r["parent_id"] in kind_by_id:
        try: union(r["id"], r["parent_id"])
        except KeyError: pass
# shared endpoint/template peers, capped to avoid O(n^2)
by_endpoint = defaultdict(list)
by_template = defaultdict(list)
for r in records:
    if r["kind"] == "payload" and r["endpoint"]:
        by_endpoint[r["endpoint"]].append(r["id"])
    if r["template"]:
        by_template[r["template"]].append(r["id"])
for ep, lst in by_endpoint.items():
    for a, b in zip(lst, lst[1:]):
        union(a, b)
for tmpl, lst in by_template.items():
    for a, b in zip(lst, lst[1:]):
        union(a, b)
comp = defaultdict(list)
for i in ids:
    comp[find(i)].append(i)
comp_summary = [
    (root, len(members), min(members), max(members))
    for root, members in comp.items()
]
comp_summary.sort(key=lambda x: (-x[1], x[2]))
with open(OUT / "communication_components.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["component_root", "size", "first_id", "last_id"])
    w.writerows(comp_summary[:100])

# Early detection simulation using row order as approximate timeline
ordered = [r for r in records if r["kind"] == "payload"]
cum = Counter()
thresholds = [10, 25, 50, 100, 250, 500, 1000, 2500]
family_makeup_at = {}
alerts = []
for i, r in enumerate(ordered, 1):
    for fam_ in r["families"]:
        cum[fam_] += 1
    # total count after i
    cum_all = i
    has_family = {f: cum[f] for f in ("link", "api", "img", "eval", "cmd", "canvas")}
    to_check = {}
    newly = False
    for thr in thresholds:
        if i == thr:
            family_makeup_at[thr] = dict(cum_all=cum_all, families=dict(has_family), unclassified=i - sum(has_family.values()))
    # thresholds of suspicious-family presence
    if cum_all >= 1 and (cum["cmd"] == 1 or cum["img"] == 1 or cum["link"] == 1):
        # first hint already; only record if not already recorded
        if not any(a["name"] == "first_suspicious_family" for a in alerts):
            alerts.append({"name": "first_suspicious_family", "row_id": r["id"], "row_index": i, "counts": {"total_payloads_seen": cum_all, "families": dict(has_family)}})
    if cum["cmd"] >= 10 and not any(a["name"] == "cmd_10" for a in alerts):
        alerts.append({"name": "cmd_at_least_10", "row_id": r["id"], "row_index": i, "cmd_count": cum["cmd"]})
    if cum["link"] >= 10 and not any(a["name"] == "link_10" for a in alerts):
        alerts.append({"name": "link_at_least_10", "row_id": r["id"], "row_index": i, "link_count": cum["link"]})
    if cum["img"] >= 10 and not any(a["name"] == "img_10" for a in alerts):
        alerts.append({"name": "img_at_least_10", "row_id": r["id"], "row_index": i, "img_count": cum["img"]})
    if cum["canvas"] >= 5 and not any(a["name"] == "canvas_5" for a in alerts):
        alerts.append({"name": "canvas_at_least_5", "row_id": r["id"], "row_index": i, "canvas_count": cum["canvas"]})
    if cum["eval"] >= 10 and not any(a["name"] == "eval_10" for a in alerts):
        alerts.append({"name": "eval_at_least_10", "row_id": r["id"], "row_index": i, "eval_count": cum["eval"]})
E = {
    "payload_total": len(ordered),
    "alerts": alerts,
    "family_counts_at_prefixes": family_makeup_at,
    "full_counts": dict(cum),
}
with open(OUT / "early_detection.json", "w") as f:
    json.dump(E, f, indent=2)

# Spread traces for salient markers.
spread = {}
for m in ["TINYOK", "FANPASS_12345", "CHAINWORKS", "sqlite3_initialize"]:
    root_candidates = [r["id"] for r in rows if m in r["text"]][:8]
    paths = []
    # ancestors (parents recursively) for each
    def ancestors(x):
        out = []
        cur = kind_by_id.get(x) and None
        # records may have parent
        pr = [rr["parent_id"] for rr in rows if rr["id"] == x][0]
        while pr:
            out.append(pr); pr = [rr["parent_id"] for rr in rows if rr["id"] == pr][0] if pr in kind_by_id else None
        return out
    for rid in root_candidates:
        paths.append({"id": rid, "ancestors": ancestors(rid), "child_count": len(child_by_parent.get(rid, [])), "children": child_by_parent.get(rid, [])[:8]})
    spread[m] = paths
with open(OUT / "spread_markers.json", "w") as f:
    json.dump(spread, f, indent=2)

print("DONE")
print(json.dumps(E, indent=2)[:3000])
