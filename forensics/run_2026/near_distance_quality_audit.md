# Near-distance candidate quality audit

- Source data (read-only): `/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted_filtered.jsonl`
- Candidates (read-only): `/Users/id19/scratchpad/binned_levenshtein/candidates.ndjson`
- Source rows: 187,242; candidate pairs total: 18,359,221
- Verification uses Python Levenshtein with banded DP (K=3) plus approved `canonical_text` (hf/hugging face, whitespace, lowercasing).
- Output samples: `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics/run_2026/near_distance_quality_samples.json`

## Candidate counts by exact Levenshtein distance
| distance | candidate_pairs | missing_endpoints |
| --- | --- | --- |
| 0 | 66,592 | 0 |
| 1 | 301,267 | 0 |
| 2 | 2,815,018 | 0 |
| 3 | 15,176,344 | 0 |

- Missing-endpoint (source or target absent from `redacted_filtered.jsonl`) total across d0-d3: 0. All candidate endpoints resolve inside the filtered row set. Note: the separately known unresolved graph parent `R0113768` (present only in `redacted.jsonl`, not in the filtered set) is not represented among candidate endpoints, so it creates no near-distance candidate-pair gaps.

## Repeated pairs
- Candidate rows with both endpoints present: 18,359,221
- Unique unordered row pairs: 18,359,221
- Repeated unordered groups: 0; extra occurrences: 0; largest repeated run: 1
- No repeated unordered row pairs were observed. Candidate generation emits each unordered row pair at most once (max repeated run length 1).

## Kind transition matrix (source_kind -> target_kind)
### d=0
| kind transition | count |
| --- | --- |
| payload -> payload | 28,086 |
| payload -> recovered_text | 4,799 |
| payload -> response | 2,911 |
| recovered_text -> recovered_text | 11,807 |
| recovered_text -> response | 32 |
| response -> recovered_text | 18,460 |
| response -> response | 497 |

### d=1
| kind transition | count |
| --- | --- |
| payload -> payload | 38,737 |
| payload -> recovered_text | 3,988 |
| payload -> response | 3,264 |
| recovered_text -> payload | 5,096 |
| recovered_text -> recovered_text | 143,558 |
| recovered_text -> response | 33,598 |
| response -> payload | 3,861 |
| response -> recovered_text | 33,062 |
| response -> response | 36,103 |

### d=2
| kind transition | count |
| --- | --- |
| payload -> payload | 255,136 |
| payload -> recovered_text | 45,236 |
| payload -> response | 37,928 |
| recovered_text -> payload | 67,571 |
| recovered_text -> recovered_text | 1,577,002 |
| recovered_text -> response | 276,495 |
| response -> payload | 44,870 |
| response -> recovered_text | 255,620 |
| response -> response | 255,160 |

### d=3
| kind transition | count |
| --- | --- |
| payload -> payload | 1,131,549 |
| payload -> recovered_text | 245,441 |
| payload -> response | 174,949 |
| recovered_text -> payload | 507,694 |
| recovered_text -> recovered_text | 9,544,992 |
| recovered_text -> response | 1,342,283 |
| response -> payload | 290,225 |
| response -> recovered_text | 1,060,857 |
| response -> response | 878,354 |

## Length delta (target_length - source_length) by distance
### d=0
| length_delta | count |
| --- | --- |
| 0 | 66,592 |

### d=1
| length_delta | count |
| --- | --- |
| 0 | 275,389 |
| 1 | 25,878 |

### d=2
| length_delta | count |
| --- | --- |
| 0 | 2,589,697 |
| 1 | 203,190 |
| 2 | 22,131 |

### d=3
| length_delta | count |
| --- | --- |
| 0 | 12,836,307 |
| 1 | 2,281,204 |
| 2 | 37,299 |
| 3 | 21,534 |

## d0 raw identical verification
- All d0 candidates: 66,592; missing endpoints: 0.
- Raw-text identical on both endpoints: 66,313.
- Raw-text different despite candidate distance 0: 279 (these are non-matching-distance candidates; see samples).

## Sampling
| distance | rate | seed | population | sampled | sampled_missing |
| --- | --- | --- | --- | --- | --- |
| 1 | 10% (+top-up to ≥10%) | 20250301 | 301,267 | 30,127 | 0 |
| 2 | 5% (+top-up to ≥5%) | 20250302 | 2,815,018 | 140,751 | 0 |
| 3 | 5% (+top-up to ≥5%) | 20250303 | 15,176,344 | 758,818 | 0 |

Sampling is deterministic by hashed pair key, independent of file order. Aggregates below are computed over the sampled pairs, not over all candidate pairs. Candidate counts and structural summaries above are computed over the full candidate set.

## Verification of candidate distance on samples
| distance | computed==candidate | mismatch | computed_distance_distribution |
| --- | --- | --- | --- |
| 1 | 30,092 | 35 | 1=30092, 2=1, 3=1, >=4=33 |
| 2 | 140,686 | 65 | 2=140686, 3=3, >=4=62 |
| 3 | 758,593 | 225 | 3=758593, >=4=225 |

- A computed value of `>=4` means the true Levenshtein distance is at least 4 (banded verification capped at 3 edits), so the candidate's `<=3` claim is wrong for that pair. Exact mismatched pairs are listed in `near_distance_quality_samples.json` (`verification_mismatch`).

## Classification of sampled pairs
| distance | raw_identical | formatting_noop | single_token_serial_digit | broad_template_swap | sampled_with_endpoints |
| --- | --- | --- | --- | --- | --- |
| 1 | 0 | 775 | 27,856 | 1,496 | 30,127 |
| 2 | 0 | 65 | 131,615 | 9,071 | 140,751 |
| 3 | 0 | 8 | 653,495 | 105,315 | 758,818 |

- `raw_identical` means source and target text are byte-for-byte equal; these arise from d0-only logic leaking into d>0 or canonical aliases making edits vanish.
- `formatting_noop` means raw text differs but `canonical_text` (lowercase + hf/hugging face alias + whitespace collapse) is identical.
- `single_token_serial_digit` means only digit runs differ after replacing each digit run with a placeholder; no alphabetic/template change (serial/identifier mutation).
- `broad_template_swap` means at least one non-digit character/template token differs; includes small spelling changes, marker substitutions, and structural changes.

## Signal vs noise assessment

### When d1/d2/d3 are useful signal
- d1 is the best near-distance signal: the edit is small and local, so a candidate distance of 1 often isolates a single meaningful mutation (a serial digit, host marker, or tiny template token) while keeping the surrounding payload structure identical.
- d1 formatting-noop and digit-only mutations are especially useful: they preserve the template and change one identifier, which is the pattern the graph relies on for provenance linkage.
- d2/d3 are still useful when the edits are concentrated in one or two contiguous tokens (serial digits, markers). The candidate distance itself is an actionable similarity score.
- Length-preserving (delta 0) and same-direction (same kind) pairs are the cleanest signals; they keep the candidate from mixing format changes with structural rewrites.

### When d1/d2/d3 become noise
- Any d>0 candidate that is actually byte-identical or canonical-identical is noise as a 'near miss': it proves normalization equivalence, not a mutation.
- Broad template swaps at distance 2-3 are often noise: a 3-character edit can change a semantic marker or host token, but it can also be incidental redaction/whitespace/quote-style differences with no provenance value.
- Cross-kind pairs (payload -> recovered_text, etc.) and length-changing pairs mix formatting/extraction differences (wrapper changes) with content similarity; they should not be treated as same-artifact mutations without checking normalization.
- Sample verification shows a tail of candidates whose true distance is >=4; these are false positives of the `<=3` near-distance gate and should be discarded rather than clustered.

## Recommended normalization / canonicalization policy

Allowed (already approved in `canonical_text` and appropriate for near-distance replay detection):
- CRLF/LF line-ending normalization.
- Lowercasing.
- Collapse runs of whitespace to a single space and trim (formatting-only).
- Alias `hugging face` / `hf` -> `huggingface` (approved lexical alias, no numeric identifier handling).

Conditionally allowed / experimental (should be separate flags, never silently folded into distance):
- Digit-run placeholder equality (`\d+` -> `<N>`) for *classification* of serial/identifier mutations, but not as a substitute for Levenshtein distance. This detects serial mutations without erasing numeric provenance.
- Quote-style normalization (`"` vs `'`) only if applied explicitly and recorded as a distinct canonical variant, because it changes the raw payload bytes.

Not allowed / unsafe:
- Stripping or collapsing numeric identifiers, serials, UUIDs, redaction counters, or destination indices; these are the actual signal in this corpus.
- Removing markers, URLs, service identifiers, or bracketed redactions; that would fabricate false equivalence across unrelated payloads.
- Treating whitespace/alias canonical equality as raw equality; near-distance candidates must retain raw edit evidence.
- Allowing unbounded normalization to convert a d3 candidate into 'same text' without recording which transformation was applied.

## Sample example counts in JSON
- Formatting-noop examples: 30
- Single-token/serial-digit examples: 30
- Verification-mismatch examples: 30
- Kind-change examples: 30
- Broad template-swap examples: 30
- d0 raw-mismatch examples: 30
- Shortest-pair examples: 36
- Lowest-similarity examples: 36
