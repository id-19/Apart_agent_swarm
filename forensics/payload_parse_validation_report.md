# Swarm Traces Payload Parse Validation (small sample)

Scope: rows 1-500 of `Data/redacted.jsonl` (all dataset kind `payload` in this
range), plus 4 representative rows discovered later in the file.  No full 189,579-row
parse was performed.  The dataset was treated as read-only.

## Script

- Exact script path: `forensics/payload_parser_validator.py`
- Invocation used: `python3 forensics/payload_parser_validator.py --sample-start 1 --sample-end 500 --include-representatives`
- Outputs: `/Users/id19/scratchpad/payload_parser_validation/`

## Detection rules used (explicit, not majority-JS)

| Family | Marker rules |
|---|---|
| JavaScript | contains `fetch(`, `document.`, `XMLHttpRequest`, or `new Image`; also explicit `eval(atob(location.hash...))` shape |
| Python | contains `import ` / word-boundary `import`, `pushblob`, or tokens `socket`/`ssl`/`base64` |
| Docker/JSON | contains `schemaVersion`, `"mediaType"`, `"rootfs"`, or `'config'` |
| HTML | contains `<iframe`, `<script`, or `<img` |
| Shell | contains `;` and at least one of `curl`, `echo`, `python3`, `src/main.c` |
| Unknown | none of the above |

Families are multi-label.  A row may be counted in more than one family; primary family
was derived by structural precedence (HTML starts-with-tag, Python starts-with-statement,
JSON starts-with object, JS markers, Shell, then Unknown).

## Counts: rows 1-500

| Dataset kind | Rows |
|---|---:|
| payload | 500 |
| recovered_text | 0 (first occurrence is row 62,486; see representatives) |
| response | 0 (first occurrence is row 53,433; see representatives) |

### Multi-label family marker counts

| Family | Rows detected |
|---|---:|
| JavaScript | 473 |
| Shell | 82 |
| HTML | 57 |
| Python | 22 |
| Unknown | 13 |
| Docker/JSON | 0 |

### Primary family counts

| Primary family | Rows |
|---|---:|
| JavaScript | 465 |
| HTML | 13 |
| BareURL (URL-only) | 12 |
| Python | 9 |
| Unknown | 1 |

### Semantic parse success by family

| Family | Rows detected | Parse success | Parse fail | Success rate |
|---|---:|---:|---:|---:|
| JavaScript (Node `--check`) | 473 | 284 | 189 | 60.0% |
| Python (`ast.parse`) | 22 | 9 | 13 | 40.9% |
| HTML (html.parser feed) | 57 | 57 | 0 | 100.0% |
| Shell (quote/brace balance) | 82 | 3 | 79 | 3.7% |
| Docker/JSON (`json.loads`) | 0 | 0 | 0 | n/a (none in 1-500) |

Pure Python snippets (9 rows starting with import/from) all parse successfully; the
other 13 Python-family rows are JavaScript/Shell wrappers containing Python-like
tokens, so `ast.parse` fails on them as expected.

## JavaScript failure classification (189 Node failures, all classified as redaction/template defects by heuristic)

| Failure class | Count | Example IDs |
|---|---:|---|
| redaction_defect:missing_backslash_escape | 136 | R0000001, R0000003, R0000006, R0000007, R0000009 |
| redaction_defect:encoded_blob_token | 29 | R0000008, R0000014, R0000020, R0000027, R0000031 |
| redaction_defect:missing_backslash+encoded_blob | 13 | R0000022, R0000034, R0000035, R0000038, R0000076 |
| redaction_defect:redaction_token_with_space | 7 | R0000075, R0000300, R0000319, R0000329, R0000446 |
| likely_redaction_defect:unquoted_expanded_token | 3 | R0000078, R0000121, R0000328 |
| likely_redaction_defect:truncated_template | 1 | R0000361 |

So 284/473 JS-family rows (60.0%) pass Node syntax as-is; 189/473 (40.0%) fail, and
all 189 failures are attributed by the heuristic to redaction/template defects
(missing escaped quote `\"`, `[ENCODED BLOB]`, or expanded multi-word redaction tokens)
rather than to genuine JavaScript syntax issues.  This is a heuristic classification;
see limitations.

Representative defect example (R0000001): the JSON body embedded in the `fetch(...)`
option string ends with `...runtime_identifier:000001]` followed by an unescaped
`"`; the expected escaped form is `]\"`, then closing brace and closing JS string.

Representative `[ENCODED BLOB]` example (R0000014): an unquoted `[ENCODED BLOB]` leak
appears inside a `font:... [ENCODED BLOB]` CSS-ish expression.

## Additional representative roots (outside rows 1-500)

| Index | ID | Kind | Families | Result summary |
|---:|---|---|---|---|
| 525 | R0000525 | payload | JavaScript, Python, Shell | JS fails (`Invalid or unexpected token`); starts data URL fetch + gzip + `eval` |
| 593 | R0000593 | payload | JavaScript, Docker/JSON | JS passes; Docker embedded JSON strings parse successfully (multi-stage registry probe) |
| 53,433 | R0053433 | response | Unknown | no JS markers; no parser applied |
| 62,486 | R0062486 | recovered_text | JavaScript | JS passes Node `--check` |

Example: R0000593 contains two parseable embedded JSON objects (`config` manifest /
`schemaVersion:2` manifest).  This confirms the Docker/JSON family validation path works
on real rows even though none occurred in rows 1-500.

## Failure examples index

- JS/Shell/Python parse-failure examples only: `failure_examples_sample.json` (197 unique
  rows, includes ID, families, parser results, JS failure class, snippet).
- Full per-row results: `sample_validation_results.json` / `.jsonl`.
- Representative results: `representative_validation_results.json`.
- Aggregated counts: `summary_sample_1_500.json`, `summary_representatives.json`,
  `family_counts_sample.csv`.

## Limitations / overclaim guardrails

1. Multi-label families mean counts do not sum to 500.  Primary-family counts are a
   precedence-based partition, not a semantic truth.
2. Shell success is a crude 3/82 because `quote/brace balance` is run over the whole
   payload; many otherwise-deliverable payloads contain an embedded JSON body, HTML, or
   Python snippets, making whole-text brace counts fail.  This heuristic does not identify
   whether the *shell command fragment* itself is balanced.
3. The JS failure classifier attributes all 189 Node failures to redaction/template
   defects.  That is based on marker presence and error tokens, not a proof that no
   genuine syntax error exists.  Rows containing `[ENCODED BLOB]` may still fail for a
   different adjacent syntax reason.
4. The raw flag counters (`missing_backslash_escape` 333, `redaction_token_with_space` 469)
   are broad substring signals and include rows whose Node check passes; they should not
   be read as 333 failing rows.
5. Python-family count (22) is intentionally marker-broad; only 9 rows are standalone
   Python and all pass `ast.parse`.  The others are mixed-language wrappers.
6. Docker/JSON was absent from rows 1-500 by the chosen markers; only representative row
   R0000593 was exercised, so its 100% success rate (1/1) is not a sample estimate.
7. `html.parser` feeding a fragment almost never errors, so the 57/57 HTML result
   reflects parser leniency, not sanitization safety.
8. Node was invoked on 473 rows; environment availability was assumed (verified available).
   Full 189K automation was not attempted.

## Recommended next steps before larger-data safety

1. Build a balanced shell-command extractor (pull unquoted command strings out of JS
   wrappers) and validate those substrings separately.
2. Repair and re-parse experiments: implement and test the known repairs
   (`apply missing \"`, replace `[ENCODED BLOB]` with a quoted placeholder, expand redaction
   tokens as quoted strings) on a small labeled subset and measure exact recovery.
3. Add a JSON-aware extractor that tries every JS string literal whose contents start with
   `{`/`[` (done here) plus regex recovery for JS-template escapes, before declaring failure.
4. Scale in guarded increments: rows 1-500 -> 1-5000 -> 1-10000, checking runtime and
   temporary file cleanup; keep row cap and progress logging.
5. Create a labeled gold subset (approx. 100 rows across families) with expected parse
   outcomes to calibrate the defect classifier and avoid over-attribution.
6. Only after stable small-sample results, consider batch automation with checkpointing
   and deterministic summaries; retain read-only dataset access.
