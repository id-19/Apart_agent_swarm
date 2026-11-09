# Step 2 draft plan: iterative structural cluster construction

## Purpose

Build meaningful nested clusters only when they are justified by concrete, reproducible linkage patterns. A cluster is not a prose narrative. A cluster means a tested, trigger-defined set of rows whose connection can be checked against sampling, disproof, and exact row evidence.

## Success condition

Step 2 is complete only when:

1. At least 95% of cleaned rows are members of at least one cluster.
2. Every row can map to nested cluster levels.
3. Each significant cluster has an explicit trigger formula, 3 or more sample IDs, 10+ sampled members, and adversarial disproof attempts.
4. Broad marker or infrastructure clusters are explicitly labeled as non-explanatory.
5. Disputed clusters remain listed rather than hidden.

## Cluster levels

- L1: exact or near-body identity
  - D0 exact normalized body equality
  - approved normalized replay
  - D1, D2, D3 near-body candidate distance
- L2: shared operation skeleton
  - request form, command structure, decode sequence, upload stage, payload wrapper, proxy relay
- L3: shared structural marker or route pivot
  - exact destination, credential ID chain, service URL, proxy route, source identifier
- L4: motion, stage, or broad working-set family
  - stage family not behavioral conclusion

Cluster notation example:

```json
{
  "sample_cluster_id": "SC-2026-0001",
  "level": "L3",
  "trigger_formula": "contains [CREDENTIAL 1] AND contains [SERVICE 3 URL 209] AND payload skeleton starts with fetch(...)",
  "member_ids": ["R0078985", "R0078988"],
  "disproof_ids": ["R0060001", "R0060002"],
  "taxonomy_labels": ["cybergym_recon", "registry_push"],
  "status": "accepted|split|quarantined"
}
```

## Iteration protocol

### A. Inspect components

Use existing bridge components and compare distinct G_CORE runs:
- exact body communities
- parent bursts
- marker and endpoint communities
- intent relation chains
- same-parent groups.

Record:
- component size,
- edge mix,
- fan-in/fan-out,
- representative triggers,
- whether the component is held together by an exact marker or broad infrastructure identity.

### B. Repeat small samples and adjudicate

- Sample 10-20 members from each candidate cluster.
- Sample another 10-20 rows with similar superficial shape but not the trigger as disproof.
- Record:
  - accepted
  - failed as connector
  - trigger too broad
  - must split
  - quarantined as broad hub
  - needs a new condition.

This is a manual, human-readable correction loop, not only percentage metrics.

### C. Use external events as candidates only

For each significant external event:
- find rows whose literal text, markers, operation skeletons, or mutation structure correspond,
- build a trigger formula,
- find disproof examples,
- classify as supported / partially supported / candidate-only / contradictory.

No report event may be treated as proven temporal assignment to any row.

### D. Operation families and graph combination

Meaningful linkage candidates include:
- fetch -> assemble -> decode -> write
- SQL/command injection wrappers
- base64/gzip droppers
- user/account discovery
- registry push and credential use
- docker/compose pushes
- proc and environment probing
- AV-evasion style probe queries
- gzip archive endpoints
- shortener / proxy / destination chains.

Each row should obtain at least one linkage class, but no arbitrary cap is allowed in the underlying generator. Broad families are permitted only when their composition is explicitly labeled, e.g. `C0001_skeleton_family`, plus attempted trigger evidence and caveat.

### E. Repeat until settled

Continue:
1. inspect current components,
2. inspect salient rows,
3. check the existing 10,000-row exploratory findings and cross-references,
4. propose and tighten triggers,
5. generate updated membership,
6. validate coverage,
7. record disputes,
8. stop only when ≥95% coverage and unresolved disputes are explicit.

Do not treat percentages as proof of semantic coherence.

## Cluster output requirements

- `cluster_signature_profiles.json`
- `cluster_rankings.json`
- `cluster_iteration_log.jsonl`
- `cluster_disputes.jsonl`
- `node_taxonomy_labels.jsonl`
- `cluster_coverage.json`
- human-readable explanation table.
