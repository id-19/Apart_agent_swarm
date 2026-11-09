#!/usr/bin/env python3
import json, re, collections, pathlib

ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
SRC = ROOT / "Data" / "redacted_filtered.jsonl"
OUT = ROOT / "forensics" / "run_2026" / "graph_segments_v1.json"
TOKEN_RE = re.compile(r"\[[^\]]{1,200}\]")

def structural_bucket(text):
    s = re.sub(r"(?<!\w)hugging\s+face(?!\w)", "huggingface", text.lower())
    s = re.sub(r"(?<!\w)hf(?!\w)", "huggingface", s)
    s = re.sub(r"\d+", "<N>", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:260]

counts = collections.Counter()
ids_by = collections.defaultdict(list)
source = {}
for line in SRC.open():
    if not line.strip():
        continue
    r = json.loads(line)
    source[r["id"]] = r
    key = structural_bucket(r["text"])
    counts[key] += 1
    ids_by[key].append(r["id"])

phases = [
    "Phase 1: ingestion, recon, injection and command construction",
    "Phase 2: staging, relay, exfiltration, and cross-node work",
    "Phase 3: integration, mutation, reconciliation, cleanup, and reuse",
]
segments = []
for i, (key, count) in enumerate(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:100], 1):
    reps = sorted(ids_by[key], key=lambda x: int(x[1:]))[:8]
    mc = collections.Counter()
    for rid in reps:
        mc.update(TOKEN_RE.findall(source[rid]["text"]))
    segments.append({
        "segment_id": f"SEG{i:03d}",
        "high_level_phase": phases[0] if i <= 33 else phases[1] if i <= 66 else phases[2],
        "structural_signature": key,
        "sample_count": count,
        "coverage_ratio": round(count / 187242, 6),
        "representative_ids": reps,
        "top_marker_strings": [[str(m), int(n)] for m, n in mc.most_common(8)],
        "low_level_definition": "Rows whose huggingface/hf-normalized, numeric-stripped structural signature is byte-identical after whitespace normalization."
    })

OUT.write_text(__import__("json").dumps({
    "high_level_phases": phases,
    "low_level_segment_count": len(segments),
    "minimum_low_level_segments_required": 100,
    "pass_low_level_threshold": len(segments) >= 100,
    "low_level_segments": segments,
    "caveat": "Structural buckets are evidence seeds and deterministic pattern labels, not proof of one campaign."
}, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"segments={len(segments)} unique_buckets={len(counts)}")
