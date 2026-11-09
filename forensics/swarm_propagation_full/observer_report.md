# Swarm Reconstruction Observer Report

- source rows: 189579
- graph nodes (including synthetic atoms): 203999
- graph edges: 284152
- references_marker: 126956
- parent_of: 61125
- template_echo: 44989
- references_information_piece: 31830
- exact_echo: 18007
- passed_identical_content: 1245

## strongest propagation signal
- passed_identical_content edges: 1245

## What was reconstructed
- Parent lineage: producer -> derived record (execution/output lineage).
- Exact echo edges: first -> later occurrence of byte-identical content.
- Passed content edges: parent and child are byte-identical (information passed unchanged).
- Rare marker edges: structural coupling among records sharing an uncommon pivot.
- Template echo edges: campaign-shape reuse among payloads.

## What an investigator still cannot prove with this dataset
1. Precise chronological order: every time_utc is null; ID order is observed order only.
2. True identity behind redaction handles; handles are masks, not people.
3. Whether parent-child lineage is execution vs storage/recovery.
4. Out-of-band channel content (image beacons, proxy calls, console output, server state).
5. Exact causal intent or collusion; structural correlation is not causation.
6. Effects of injected command fragments; only their presence is recorded, not execution outcomes beyond returned text.
7. Deduplication of agents: one operator or many accounts is not resolvable from redacted IDs.
