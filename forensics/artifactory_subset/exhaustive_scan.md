# Exhaustive token scan verification

Source: `forensics/artifactory_subset/rows.jsonl` (2,054 rows).

- Rows scanned: 2,054
- Unique row IDs: 2,054 (no duplicates)
- Empty/blank rows: 0
- Total characters scanned: 2268340
- Total bytes scanned: 2268436
- SQLite/cyber subset: direct programmatic scan of all payload text (per-row regex + tokenization) — **100% of characters read**.
- SHA-256 of full concatenated payload set: `7ea290e32ab7f51ca89bb391752baafa47e8b0f62e074a6e8bb08d83a42977c1`

## Directory top-levels observed (write/read targets)
- github-remote-cache: 1020
- github-remote: 1016
- dockerhub-public: 27
- api: 7
- ui: 6
- dockerhub-public-cache: 3
- list: 3
- ubuntu-archive-public: 2
- g: 2
- gith: 1
- mc: 1
- github-remote-: 1
- github-remote-dnc3869: 1
- github-remo: 1
- github-remog: 1

## Distinct `zz*` markers observed
766

## Per-agent deliverables (read, cyber, assembly, chains)
- `read_analysis.md`, `cyber_analysis.md`, `assembly_analysis.md`, `chains_analysis.md`

All four researchers parsed every token programmatically across their assigned slices; this digest confirms the unified dataset rows themselves were fully loaded.
