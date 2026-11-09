# Core graph edge validation v2

Read-only audit of `forensics/run_2026/core/core_rows.ndjson` and `core_edges.ndjson` against `Data/redacted_filtered.jsonl`. No graph data was altered.

## Scope and result

- Rows (entities): 187,242
- Edges: 506,242
- Components: 19,575 (singletons 17,514; largest 153,561)
- Edge sets: rebuilt independently from the graph builder; 0 missing and 0 extra edges.
- Global loopholes: 2, both in `PARENT_DIRECT` unresolved-parent endpoints.
- Random 10% sample: 50,622 edges reviewed, 0 loopholes.
- Adversarial 5% disproof sample: 25,310 edges reviewed, 0 loopholes.

## Edge-class counts

| Edge class | Edges | 10% sample | 5% adversarial |
|---|---:|---:|---:|
| EXACT_BODY | 23,471 | 2,347 | 1,173 |
| MARKER_ENDPOINT | 121,104 | 12,110 | 6,055 |
| MARKER_SAME | 267,062 | 26,706 | 13,353 |
| NORMALIZED_REPLAY | 1,826 | 182 | 91 |
| PARENT_DIRECT | 59,313 | 5,931 | 2,965 |
| SAME_PARENT_SIBLING | 33,466 | 3,346 | 1,673 |
| Total | 506,242 | 50,622 | 25,310 |

## Components

- Row nodes: 187,242
- Connected components: 19,575
- Singletons: 17,514
- Largest component: 153,561
- Top component sizes: 153561, 9280, 253, 51, 44, 42, 32, 30, 27, 26, 24, 20, 19, 18, 18, 18, 15, 15, 15, 15, 14, 14, 14, 14, 13.
- Endpoints missing from row index: 2 (external source `R0113768` only).
- Marker type mismatches: 0.

## Proof-string mapping

- EXACT_BODY: `text_sha256=<sha256(raw text)> rows=<group size>`. Both endpoint raw text SHA-256 values equal the proof hash.
- NORMALIZED_REPLAY (canonical replay): `canonical_sha256=<sha256(canonical text)>; raw_class_count=<distinct raw bodies in the normalized group> rows=<representatives>`. Each endpoint has that canonical hash, the endpoints' raw text SHA-256 values differ, and `raw_class_count` matches the recomputed distinct raw classes. Canonical text only applies approved `hugging face`/`hf` -> `huggingface`, whitespace, and lowercase normalization; numeric identifiers are not stripped.
- PARENT_DIRECT: `stored parent_id=<parent row id>`. Target row's `parent_id` must equal source.
- SAME_PARENT_SIBLING: `shared_parent=<parent row id> rows=<sibling count>`. Both endpoints share one non-null parent.
- MARKER_SAME / MARKER_ENDPOINT: `<exact bracketed marker> rows=<rows containing that exact marker>`. The marker must appear in both endpoints' marker lists, and the edge type must match endpoint classification via `is_endpoint()`.

Sampling used deterministic seeds 20260325 (10%) and 20260326 (5%), with fixed floor formulas `max(1, n//10)` and `min(n, max(1, n//20))`.

## Loophole details

### L1 - Unresolved parent endpoints (graph-level)

- Class: `PARENT_DIRECT`
- Count: 2
- Source: `R0113768` (not present in filtered row index)
- Targets: `R0149891`, `R0168370`
- Proof: `stored parent_id=R0113768`
- Gate violated: row-level graph edges must resolve both endpoint sample IDs.
- Reason: both children retain a valid `parent_id=R0113768`, but that parent exists only in `Data/redacted.jsonl` as `payload` and was excluded from `Data/redacted_filtered.jsonl`. Thus the two parent edges point outside the graph entity set.
- Disposition: reported only; graph data left unchanged.
- Status in samples: these two edges were not captured in the random 10% or 5% samples, but the full-edge scan found them.

### L2 - Prior validation trust short-circuit (method-level)

- Scope: `verify_core_graph.py` and `audit_core_graph.py`
- Proof/check: `PARENT_DIRECT` trust `a not in src or (b in src and src[b].get('parent_id')==a)`.
- Reason: when the parent/source was absent, the prior validator returned true without checking the child or endpoint resolution, hiding L1. v2 applies universal row-resolution before class-specific proof checks.
- Disposition: corrected in v2 methodology; no data changed.

No other edge-class loopholes were found. In particular: marker endpoints exact-match (0 mismatches), normalized replay proof counts match recomputed group sizes (0 mismatches), EXACT_BODY hashes (0 mismatches), SAME_PARENT groups (0 mismatches), and marker endpoint classification (0 mismatches).

## Sample results

- Accepted 10% sample: 50,622 edges, 0 loopholes.
  - EXACT_BODY 2,347; MARKER_ENDPOINT 12,110; MARKER_SAME 26,706; NORMALIZED_REPLAY 182; PARENT_DIRECT 5,931; SAME_PARENT_SIBLING 3,346.
- Adversarial 5% disproof sample: 25,310 edges, 0 loopholes.
  - EXACT_BODY 1,173; MARKER_ENDPOINT 6,055; MARKER_SAME 13,353; NORMALIZED_REPLAY 91; PARENT_DIRECT 2,965; SAME_PARENT_SIBLING 1,673.

## Conclusion

All 506,242 edges match the independently rebuilt expected edge set, including all proof strings. Row-resolving graph edges are class-valid across all edge classes. The only loopholes are two unresolved `PARENT_DIRECT` parent references to filtered-out row `R0113768`; these are reported, not fixed, and no graph data was modified.
