# Swarm Traces report handoff

## Report-ready conclusion

The retained Swarm Traces corpus contains 187,242 filtered rows. Its strongest
evidence is structural: repeated bodies, parent-child revisions, shared marker
and endpoint pivots, recurring clusters, and candidate information-flow paths.
The evidence supports repeatable exploit-template and propagation-pattern
families, but it does not establish sender identity, authorization, execution
success, or row-level chronology.

The core graph contains 459,448 validated non-candidate edges across 26,043
components. The largest component contains 144,075 rows and is quarantined as a
broad marker/endpoint hub rather than treated as one operation. Validation found
zero failed resolved structural edges and two documented unresolved references
to storage parent `R0113768`.

Temporal evidence is deliberately limited. Every retained row has null
`time_utc`; 1,851 rows contain parseable timestamp-like cues and 945 grounded
temporal links are retained as advisory ordering evidence. External reports are
used only for candidate context. No local row is assigned an external event
date as fact.

## Numbers safe to quote

| Measure | Result | Interpretation |
|---|---:|---|
| Retained rows | 187,242 | Filtered corpus; source IDs are storage IDs |
| Core structural edges | 459,448 | Trigger-defined structural relations, not causation |
| Components | 26,043 | Largest component is quarantined as a broad hub |
| L1 exact-body clusters | 161,945 | 100% row membership at this structural tier |
| L3 marker clusters | 79,451 | Marker recurrence; not identity evidence |
| L4 components | 26,043 | Union of validated structural edges |
| Valid timestamp anchors | 1,851 | Cue metadata only |
| Grounded temporal links | 945 | Advisory ordering candidates |
| Information-flow edges | 60,256 | Parent direction or grounded stored direction |
| Near-body candidate pairs | 18,852,564 | Aggregate candidate adjacency; not coordination proof |
| Deterministic low-level segments | 100 | 87,438 rows / 46.7%; evidence families only |

## Evidence boundaries

Use “supports,” “is consistent with,” and “candidate” for graph conclusions.
Do not write that the corpus proves an actor, campaign, timestamp, execution
outcome, credential use, or external incident assignment. Parent links encode
stored lineage, not execution order. `payload`, `recovered_text`, and `response`
are capture stages, not actor roles. Redaction removes the values needed for
identity or endpoint attribution.

## Canonical sources

- Final narrative: `FINAL_ARTIFACT/report.md`
- Full reconstruction: `FINAL_RECONSTRUCTION_REPORT.md`
- Executive summary: `FINAL_ARTIFACT/evidence_bundle/EXECUTIVE_REPORT.md`
- Evidence archive and hash: `FINAL_ARTIFACT/evidence_bundle.tar.gz` and
  `FINAL_ARTIFACT/evidence_manifest.json`
- Recovered plans: `FINAL_ARTIFACT/plans/`
- Recovered analysis workspace: `Data/`, `forensics/`, and
  `artifactory_subset/`

The final bundle is authoritative for shipped artifact contents. The recovered
root reports, scripts, checkpoints, and older forensic outputs are retained for
provenance and reproduction history; they are not automatically interchangeable
with the final bundle.

## Reproducibility

The filtered source hash is:

`5a048060a8fc2a90246b42c10c5bdd2e35d1b59f98b48b2849155853e4dc28ee`

The final evidence archive hash is recorded in
`FINAL_ARTIFACT/evidence_manifest.json`. Use `RUN.md` for the historical build
pipeline and the final bundle’s manifests for artifact-level verification.
