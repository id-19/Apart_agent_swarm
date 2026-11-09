#!/usr/bin/env python3
"""Deterministic near-body exemplar sampler."""
import json
import pathlib
import random
import re

ROOT = pathlib.Path("/Users/id19/Programming/AI_research/Apart_agent_swarm")
DATA = ROOT / "Data" / "redacted_filtered.jsonl"
STATS = ROOT / "forensics" / "run_2026" / "near_distance_stats.json"
OUT = ROOT / "forensics" / "run_2026" / "near_body_exemplars.ndjson"
LOG = ROOT / "forensics" / "run_2026" / "near_body_exemplars.log"

ANCHOR_SEED = 731
ANCHOR_COUNT = 200
MAX_PER_DISTANCE = 2
BAND_K = 2


def canonical_text(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").lower()
    for alias in ("hugging face", "hf"):
        text = re.sub(rf"(?<!\w){re.escape(alias)}(?!\w)", "huggingface", text)
    return re.sub(r"\s+", " ", text).strip()


def lev_upto_k(a: str, b: str, k: int = BAND_K) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > k:
        return abs(la - lb)
    prev = {j: j for j in range(0, min(lb, k) + 1)}
    for i, ch in enumerate(a, 1):
        cur = {}
        lo = max(0, i - k)
        hi = min(lb, i + k)
        for j in range(lo, hi + 1):
            if j == 0:
                cur[0] = i
                continue
            best = 10 ** 9
            if j in prev:
                best = min(best, prev[j] + 1)
            if j - 1 in cur:
                best = min(best, cur[j - 1] + 1)
            if j - 1 in prev:
                cost = 0 if ch == b[j - 1] else 1
                best = min(best, prev[j - 1] + cost)
            cur[j] = best
        if not cur or min(cur.values()) > k:
            return k + 1
        prev = cur
    d = prev.get(lb, k + 1)
    return d if d <= k else k + 1


def main() -> None:
    rows_raw = [json.loads(line) for line in DATA.open(encoding="utf-8") if line.strip()]
    ids = [r["id"] for r in rows_raw]
    canons = [canonical_text(r.get("text", "")) for r in rows_raw]
    lens = [len(c) for c in canons]
    token_sets = [set(c.split()) for c in canons]
    n = len(rows_raw)

    rng = random.Random(ANCHOR_SEED)
    anchors = sorted(rng.sample(range(n), ANCHOR_COUNT))

    seen_pairs = set()
    emitted = []
    stats = {
        "anchors": len(anchors),
        "pairs_emitted": 0,
        "pairs_d1": 0,
        "pairs_d2": 0,
        "anchors_with_d1": 0,
        "anchors_with_d2": 0,
        "duplicate_pairs_skipped": 0,
    }

    for ai, a in enumerate(anchors):
        ca = canons[a]
        la = lens[a]
        ta = token_sets[a]
        d1 = []
        d2 = []
        for j in range(n):
            if j == a:
                continue
            if len(d1) >= MAX_PER_DISTANCE and len(d2) >= MAX_PER_DISTANCE:
                break
            lb = lens[j]
            if abs(lb - la) > BAND_K:
                continue
            tb = token_sets[j]
            if ta and tb and not (ta & tb):
                continue
            cb = canons[j]
            if ca == cb:
                continue
            d = lev_upto_k(ca, cb, BAND_K)
            if d == 1 and len(d1) < MAX_PER_DISTANCE:
                d1.append(j)
            elif d == 2 and len(d2) < MAX_PER_DISTANCE:
                d2.append(j)
        a_has_d1 = bool(d1)
        a_has_d2 = bool(d2)

        def disproof_ids(src_pos: int, tgt_pos: int) -> list:
            seed = src_pos * 1000003 + tgt_pos * 97 + ANCHOR_SEED
            rr = random.Random(seed)
            out = []
            used = {src_pos, tgt_pos}
            for idx in rr.sample(range(n), 7):
                if len(out) >= 3:
                    break
                if idx in used:
                    continue
                out.append(ids[idx])
                used.add(idx)
            cursor = (src_pos + tgt_pos + ANCHOR_SEED) % n
            while len(out) < 3:
                if cursor not in used:
                    out.append(ids[cursor])
                    used.add(cursor)
                cursor = (cursor + 1) % n
            return out[:3]

        for bucket, measured in ((d1, 1), (d2, 2)):
            for j in bucket:
                pair_key = frozenset((ids[a], ids[j]))
                if pair_key in seen_pairs:
                    stats["duplicate_pairs_skipped"] += 1
                    continue
                seen_pairs.add(pair_key)
                rec = {
                    "source": ids[a],
                    "target": ids[j],
                    "measured_distance": measured,
                    "canonical_equal": False,
                    "canonical_equal_note": "should differ (bodies non-identical after normalization)",
                    "trigger_formula": (
                        "levenshtein(canonical_text(source), canonical_text(target))"
                        f" == {measured}; normalization = lowercase + whitespace collapse + "
                        "hugging face/hf -> huggingface"
                    ),
                    "candidate_filter": "heuristic_shared_normalized_word_or_length_window",
                    "anchor_row_index": a,
                    "target_row_index": j,
                    "disproof_row_ids": disproof_ids(a, j),
                }
                emitted.append(rec)
                stats["pairs_emitted"] += 1
                if measured == 1:
                    stats["pairs_d1"] += 1
                else:
                    stats["pairs_d2"] += 1
        if a_has_d1:
            stats["anchors_with_d1"] += 1
        if a_has_d2:
            stats["anchors_with_d2"] += 1
        if (ai + 1) % 25 == 0:
            print(f"anchors processed: {ai + 1}/{len(anchors)}; emitted={len(emitted)}", flush=True)

    with OUT.open("w", encoding="utf-8") as f:
        for rec in emitted:
            f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")

    verify_errors = []
    idset = set(ids)
    pair_keys2 = set()
    by_id = {rid: c for rid, c in zip(ids, canons)}
    for rec in emitted:
        if rec["source"] == rec["target"]:
            verify_errors.append(f"identical source/target: {rec['source']}")
        if rec["canonical_equal"] is not False:
            verify_errors.append(f"canonical_equal not false: {rec['source']}->{rec['target']}")
        pk = frozenset((rec["source"], rec["target"]))
        if pk in pair_keys2:
            verify_errors.append(f"duplicate pair: {rec['source']}->{rec['target']}")
        pair_keys2.add(pk)
        if rec["measured_distance"] not in (1, 2):
            verify_errors.append(f"bad distance: {rec['measured_distance']}")
        for did in rec["disproof_row_ids"]:
            if did not in idset:
                verify_errors.append(f"unknown disproof id: {did}")
            if did in (rec["source"], rec["target"]):
                verify_errors.append(f"disproof equals endpoint: {did}")
        if by_id[rec["source"]] == by_id[rec["target"]]:
            verify_errors.append(f"canonical actually equal: {rec['source']}->{rec['target']}")

    d3_aggregates = {}
    try:
        stats_json = json.loads(STATS.read_text(encoding="utf-8"))
        d3 = stats_json.get("distance_3", {})
        d3_aggregates = {
            "edge_count_cumulative_le3": d3.get("edge_count"),
            "distance_counts": d3.get("distance_counts"),
            "endpoints": d3.get("endpoints"),
            "components": d3.get("components"),
        }
    except Exception as e:
        d3_aggregates = {"error": str(e)}

    log_lines = [
        "near_body_exemplars run log",
        f"input_rows: {n}",
        f"anchor_seed: {ANCHOR_SEED}",
        f"anchors_sampled: {len(anchors)} (uniform by row index)",
        f"pairs_emitted: {stats['pairs_emitted']} (d1={stats['pairs_d1']}, d2={stats['pairs_d2']})",
        f"anchors_with_d1: {stats['anchors_with_d1']}",
        f"anchors_with_d2: {stats['anchors_with_d2']}",
        f"duplicate_pairs_skipped: {stats['duplicate_pairs_skipped']}",
        f"verification_errors: {len(verify_errors)}",
    ]
    for e in verify_errors[:20]:
        log_lines.append(f"  ERROR: {e}")
    log_lines.append("distance_3 (aggregate only, not materialized):")
    for k, v in d3_aggregates.items():
        log_lines.append(f"  {k}: {v}")
    LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT} ({stats['pairs_emitted']} pairs)")
    print(f"wrote {LOG}")
    print(f"verification errors: {len(verify_errors)}")
    print("distance_3 aggregates:", d3_aggregates)
    if verify_errors:
        raise SystemExit("VERIFICATION FAILED: " + "; ".join(verify_errors[:5]))


if __name__ == "__main__":
    main()
