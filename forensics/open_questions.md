# Open questions log

## Lineage / graph
- Most payload records are roots, but which payloads are not roots, and what does that imply? (Expected: essentially none; one recovered_text -> recovered_text edge.)
- Do parent links represent direct agent-to-agent conversation, or producer-to-derived-fragment relationships?
- Can a root with zero children represent a failed, silent, or non-rendered injection?

## Identity
- Are top-level IDs meaningful or only sequential export IDs?
- Are `agent_id` and `task_id` redacted beyond recovery, or can their numbering structure be used?
- METR reportedly says agents spoofed identifiers; external verification is needed because network access is unavailable.
- Can shared credential placeholders act as process markers despite redaction?

## Information spread
- Which records carry a single piece of information across multiple chain stages?
- How do shortener codes, destination IDs, and encoded blob IDs map to clusters?
- What does `recovered_text` actually tell us: observed output, attempted reconstruction, or executable next-stage payload?

## Early detection
- Does ID order approximate chronological order?
- Which thresholds avoid over-flagging when no benign baseline is available?
- Can link-chaining and image beacons be flagged from the first few records?

## Redaction / completeness
- What payloads are not full scripts?
- Which unclassified records are leave nodes versus direct service endpoints?
- What would an investigator still miss?

## Candidate relation status (cleanup)
- TIME_DEPENDENCY is withdrawn as a relation family; only 11 strict direct-graph order observations were found, with 850 direction violations. Timestamp anchors remain metadata only (1851 anchors).
- The 18,852,564-row near-body candidate relation (d1=308,204; d2=2,922,781; d3=15,621,579) is not materialized in the active workspace. Its pre-cleanup artifact is archived at `forensics/archive/candidate_artifacts/graph_edges_v2.original_20162602.ndjson`. Do not rerun the full candidate generator without explicit approval.
- `forensics/graph_edges_v2.jsonl` now contains 1,310,038 non-candidate edges only.
