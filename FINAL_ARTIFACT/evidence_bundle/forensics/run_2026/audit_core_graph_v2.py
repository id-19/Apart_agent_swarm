#!/usr/bin/env python3
import json, random, collections, hashlib, re
from pathlib import Path
ROOT = Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
ROWS = ROOT / "forensics/run_2026/core/core_rows.ndjson"
EDGES = ROOT / "forensics/run_2026/core/core_edges.ndjson"
SRC = ROOT / "Data/redacted_filtered.jsonl"
OUT = ROOT / "forensics/run_2026/core/core_edge_validation.json"
rows = {json.loads(l)["id"]: json.loads(l) for l in ROWS.open() if l.strip()}
src = {json.loads(l)["id"]: json.loads(l) for l in SRC.open() if l.strip()}
edges = [json.loads(l) for l in EDGES.open() if l.strip()]
rng = random.Random(20260325)
by = collections.defaultdict(list)
for e in edges:
    by[e["edge_type"]].append(e)

def marker_trigger(e):
    proof = e["proof"]
    return proof[: proof.rfind(" rows=")] if proof.endswith("] rows=...") or " rows=" in proof else proof

def trust(e):
    et = e["edge_type"]
    a, b = e["source"], e["target"]
    proof = e["proof"]
    if et == "EXACT_BODY":
        trig = proof.split("=", 1)[1].rsplit(" rows=", 1)[0]
        return (a in src and b in src and
                hashlib.sha256(src[a]["text"].encode()).hexdigest() == trig and
                hashlib.sha256(src[b]["text"].encode()).hexdigest() == trig)
    if et == "NORMALIZED_REPLAY":
        trig = proof.rsplit(" rows=", 1)[0].rsplit(";", 1)[0].split("=", 1)[1]
        return (a in rows and b in rows and
                rows[a].get("canonical_sha256") == trig and
                rows[b].get("canonical_sha256") == trig and
                rows[a].get("text_sha256") != rows[b].get("text_sha256"))
    if et == "PARENT_DIRECT":
        return a not in src or (b in src and src[b].get("parent_id") == a)
    if et == "SAME_PARENT_SIBLING":
        return (a in src and b in src and
                src[a].get("parent_id") is not None and
                src[a].get("parent_id") == src[b].get("parent_id"))
    trig = proof.rsplit(" rows=", 1)[0]
    return a in src and b in src and trig in src[a]["text"] and trig in src[b]["text"]

summary = {}
loops = []
for et, cls in sorted(by.items()):
    accepted = rng.sample(cls, max(1, len(cls) // 10))
    disproof = rng.sample(cls, min(len(cls), max(1, len(cls) // 20)))
    bad = [e for e in accepted if not trust(e)]
    adversarial = [e for e in disproof if not trust(e)]
    summary[et] = {
        "edges": len(cls),
        "accepted_10pct": len(accepted),
        "loopholes_10pct": len(bad),
        "adversarial_5pct": len(disproof),
        "adversarial_loopholes_5pct": len(adversarial),
        "sample_loopholes": bad[:20],
        "adversarial_loopholes": adversarial[:20],
    }
    loops.extend({"edge_type": et, "sample_direction": "accepted_10pct", "edge": e, "reason": "deterministic fails"} for e in bad)
    loops.extend({"edge_type": et, "sample_direction": "adversarial_5pct", "edge": e, "reason": "deterministic fails"} for e in adversarial)
OUT.write_text(json.dumps({
    "rows": len(rows),
    "source_rows": len(src),
    "edges": len(edges),
    "loophole_count": len(loops),
    "validation": summary,
    "loopholes": loops[:200],
}, indent=2, ensure_ascii=False), encoding="utf-8")
for et, v in summary.items():
    print(et, v["edges"], v["loopholes_10pct"], v["adversarial_loopholes_5pct"])
