# Step 4 draft plan: external and internally discovered temporal context graph

## Purpose

Map structural and temporal clusters to external events and internally discovered events. Never imply external dates are row-local timestamps.

## External context stage

Use `external_event_timeline.md`, crosswalk notes, and parsed source reports only as candidate associations.

Each event relationship must include:
- local trigger or marker family,
- external event date,
- source bounds (high confidence strict source (HCP) only where explicit),
- match confidence, and
- `candidate_only` or `unverified` where applicable.

Do not link every individual row to an external event. Link a representative cluster or sample only where exact structural, string, or operation evidence supports a transition.

## Internally discovered events

Some graph structures will likely not match any report event. These can become internally reconstructed events where justified, for example:
- repeated dead-drop writes
- probe sequences against routes
- hollow response/registration sequence
- repeated exfiltration preparation
- gateway traversal patterns
- cross-region service/endpoint dissemination
- unique many-to-many or unusual staged payloads extending order.

Each candidate internal event must include:
- defining trigger
- source row IDs
- structural or manual cited evidence
- why no external event is needed
- why this should not be reported as proven incident action if arsity only.

## Required outputs
- `external_event_to_cluster_candidates.tsv`
- `external_unmatched_events.md`
- `external_created_events.tsv`
- `event_support_scores.json`
- `cluster_to_event_candidates.jsonl`
- `external_false_parallel_patterns.md`

## Rules
- report facts can constrain only structurally matched rows
- unverified external events stay explicit
- report-candidate link cannot prove timestamped execution or actor
- internal events are labeled reconstructed, not report-confirmed

## Success condition
Every event relation either has local structural support or is explicitly unverifiable. No cluster receives an external timestamp.
