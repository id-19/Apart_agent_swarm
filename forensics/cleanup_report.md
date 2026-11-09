# Forensics cleanup report

## Scope
Organized `/Users/id19/Programming/AI_research/Apart_agent_swarm/forensics` in place.
Core dataset `Data/` was not modified.

## Actions performed

1. Verified reproducible scripts:
   - `forensics/artifactory_payload_audit/run_audit.py` - ran successfully; selected 1,227
     payload rows and regenerated `artifactory_payload_audit.md` and `payload_index.tsv`
     (34.3s).
   - `forensics/artifactory_subset/cluster_markers.py` - ran successfully; wrote 1,234
     marker clusters into `marker_clusters.md` (0.08s).
   - `forensics/graph.py` - smoke-tested with `--list-edge-types` (102 edge types, compiles).
   - `eda.py`, `swarm_forensics.py` - compile-checked.
2. Removed accidental working/temp files:
   - `.DS_Store` at project root and any nested instances.
   - `__pycache__` directories and `.pyc` files at project root, `forensics/`,
     `forensics/artifactory_payload_audit/`, and `forensics/artifactory_subset/`.
   - `forensics/artifactory_payload_audit/run_audit2.py` - incomplete, non-runnable
     (unterminated string literal); not referenced by any deliverable or script.
3. Grouped documentation:
   - Created top-level `forensics/README.md` with directory layout, script run notes, and a
     41-file manifest with counts.
   - Kept all prior deliverables; no core dataset or analysis outputs were deleted.
4. Did not modify `Data/`.

## Verification

- Scripts above compiled/run without errors after cleanup.
- Forensics file count after cleanup (excluding this README and cleanup report): 41 files.
- Dataset checksums unchanged:
  - `Data/redacted.jsonl` - 92,801,525 bytes,
    sha256 `91e9158487a63acb12e54faa8490c4a23f664e1650c947a87d270d2022b0451e`
  - `Data/redacted.jsonl.gz` - 15,214,685 bytes,
    sha256 `7b66ab21674de52fcd3f557652f68b1801170c998e2f266862124e6edf283488`

## Remaining notes

- Top-level helpers `../eda.py` and `../swarm_forensics.py` remain outside `forensics/`;
  they were not moved because they are project-root entry points.
- Top-level `artifactory_subset/` remains outside `forensics/` as an existing companion
  directory; its files were not deleted.
