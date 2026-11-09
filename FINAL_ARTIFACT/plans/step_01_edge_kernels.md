# Step 1 plan: construct and verify the basic edge kernels

## Eventual goal bearing on this step
Build a graph in which every edge is justified by one literal, reproducible trigger. No relation may be introduced merely because it "looked meaningful" until its defining condition, samples, and validation record are documented.

## Required output
- One clean graph construction layer.
- One `edges/` directory containing the exact condition for every edge class.
- One canonical, clean tap-dataset layer.
- Archived legacy files rather than deleted work.
- Four-field edge schema:
  - `source`
  - `target`
  - `edge_class`
  - `edge_sub_class`

## Graph kernel classes

### 1. Lineage and parent-child linkage
- `PARENT_DIRECT`: child `row.parent_id == parent`.
- `SAME_PARENT_SIBLING`: distinct children with the same non-null parent.
- `PARENT_MUTATION`: parent→child where the parent and child bodies are not byte-identical.
- Direction rule: parent to child only. No reverse parent edge is invented.
- `PARENT_MUTATION` sub classes:
  - `addition`: child begins with the parent body (extension).
  - `truncation`: parent begins with the child body (prefix relation).
  - `substitution`: otherwise changed.
  - record measured parent and child lengths; do not overstate line-level diffs unless a diff algorithm is implemented and cited.

### 2. Identical-body / replay similarity
Replace separate `EXACT_BODY`, `NORMALIZED_REPLAY`, and `NEAR_BODY` events with one relation class:

- `IDENTICAL_BODY`
- Sub-classes:
  - `D0`: canonical body equality after approved normalization
  - `D1`: Levenshtein distance 1
  - `D2`: Levenshtein distance 2
  - `D3`: Levenshtein distance 3

Rules:
- apply only approved semantic normalization: approved alias replacement and Unicode/whitespace-wrapper normalization.
- keep the exact measured distance as sub-class/trigger.
- no arbitrary cap; emit the full mathematical result unless resource constraints force a clearly documented policy decision.
- near-body links remain candidate adjacency, not proof of coordination or shared intent.

### 3. Intent / operation-signature linkage
- `INTENT_SIGNATURE_L1`: shared explicit operation name/function template, for example `sqlite3_initialize`, registry handler, or a recognizable endpoint.
- `INTENT_SIGNATURE_L2`: shared endpoint or destination signature.
- `INTENT_SIGNATURE_L3`: shared operation skeleton (method, route, payload framing, command syntax).
- `INTENT_SIGNATURE_L4`: shared coarse campaign-like technique family only when a literal repeated structural trigger supports it.

Allowed primitives:
- exact quoted string or identifier
- exact URL/host/route token
- exact bracketed marker
- exact command phrase
- counted order only for descriptive ordering, never as runtime identity/order

Not allowed:
- free-form “looks similar” labels
- semantic-campaign guesses presented as triggers
- host/user/secret-inferred identity
- broad markers such as syntactic slots (`[\d+]`, `[i]`, `[k]`, `[token]`, `[key]`) as linkage pivots

### 4. Information linkages
- `MARKER_SAME`: exact repeated non-generic, non-syntactic bracketed marker.
- `MARKER_ENDPOINT`: exact repeated transit marker (`PROXY`, `SHORTENER URL`, `SERVICE HOST`, `IP ADDRESS`, destination, HTTP route).
- Proposed refined semantic information classes:
  - `SHARED_INFO_READ`: both samples read or consume the same named information marker
  - `WRITE_THEN_USE`: one sample writes an information marker that another later consumes
  - `SAME_WRITE_TARGET`: same destination/service/repository/shortener path
  - `META_INJECTION_PATTERN`: same injection wrapper or code-delivery structure

Concretely, a marker only joins samples when it identifies an endpoint, service, destination, credential occurrence, repository, proxy route, or other non-trivial shared structural pivot. Generic syntax markers do not join.

### Provenance rules
Every edge must resolve both IDs to retained sample rows, preserve an explicit `source`, `target`, `edge_class`, and `edge_sub_class`, and document:
- exact trigger,
- normalization policy involved (if any),
- computation method,
- sampling limits,
- contradiction or dispute status.

### Validation
1. Inspect 10–20 hand-selected rows per proposed edge class.
2. Record accepted, rejected, split, or newly needed classes.
3. Only then run deterministic 10% random and 5% adversarial sampling.
4. Do not overstate rejection-free results because broad edges such as marker overlap can legitimately produce weak or mixed findings.
5. Maintain a `edge_class_acceptance.json`, `disputed_edges.jsonl`, and `edge_validation_report.md`.

