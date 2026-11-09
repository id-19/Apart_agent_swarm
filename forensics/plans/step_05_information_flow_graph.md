# Step 5 draft plan: information-flow graph

## Purpose

Model how information moves or reappears across already tested and ordered structural elements. This is separate from semantic similarity or co-occurrence.

## Required info-flow edge classes

- `SHARED_INFO_READ`
- `WRITE_THEN_USE`
- `SAME_WRITE_TARGET`
- `META_INJECTION_PATTERN`
- `BODY_REVISION_OR_REPLAY`
- `OPERATION_SIGNATURE_FLOW`

No single marker should be reinterpreted as causation without a read, write, target, or replay trigger. Co-occurrence is merely supporting evidence.

The parent-child, mutation, and temporal-order triggers make directed flow possible when supported.

## Procedure

1. Use structural bases from the previous step:
   - L1 identity or replay
   - L2 structural operation family
   - L3 marker/pivot
   - L4 broad grouping
   - direct temporal edge evidence.
3. Define information roles:
   - source information
   - transformed information
   - intermediary information
   - reused information
   - destination information
   - injection surface
4. For each candidate flow edge, require:
   - a textual or structural object reference
   - a time order or temporal confidence
   - body or marker evidence
   - at least one disproof case
5. Ignore arbitrary field scoring; only evidence-backed states should be able.
6. Group workflow routes separately by payload, destination, marker, and assembly chains.

## Outputs
- `info_flow_edges_v1.jsonl`
- `info_flow_evidence.json`
- `node_reconstruction_paths.json`
- `info_flow_visualization_export.json`.

## Success condition
Every info-flow edge explains what information is shared, direction of possible transmission, confidence and an explicit trigger. And itself being reconstructable.
