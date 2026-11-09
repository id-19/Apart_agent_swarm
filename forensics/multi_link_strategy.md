# Multi-link strategy for Swarm Traces

## Scope

This framework reconstructs *candidate* linkages across 189,579 redacted Swarm Traces
samples using only observed IDs and textual pivots. IDs are ordered (R000...) but are
not known real chronology, so every edge is directional by ID order only.

## Edge policies

| Policy | Edge types | Use |
|---|---|---|
| Parent lineage | `parent_child`, `sibling_same_parent` | Highest-confidence structural chains and fanout. |
| Template reuse | `shared_template`, `shared_command_body`, `shared_normalized_text_global`, `payload_same_template`, `response_same_text` | Reuse of command-injection and payload templates; strong for batch attribution, weak for actor identity. |
| Salient markers | `salient_marker` plus `marker_*` and literal marker edges | Rare high-impact output/beacon markers such as TINYOK, FANPASS_12345, CHAINWORKS, cybergym, 23619, sqlite3_initialize. |
| URL/service/destination pivots | `destination_id`, `service_url`, `service_host`, `proxy_url`, `redirect_url`, plus compound variants | Infrastructure and transport linkage; may overmerge shared pools. |
| Shortener pivots | `shortener_code`, `shortener_url`, `shortener_host`, `blob_shortener_pair` | Shortener-chain propagation and destination pivots. |
| Encoded blob pivots | `encoded_blob_number`, `opaque_*`, `blob_*_pair` | Encoded/Opaque blob number linkage; strong when exact number repeats. |
| HF repo/config pivots | `hf_repo_number`, `hf_repo_redacted_id`, repo locator/partial repo edges, `hf_repo_destination_pair` | HuggingFace repository/config reuse. |
| Credential aliases | `credential_id`, `secret_key_id`, `bearer_token_id`, JWT claim/user edges, compound credential edges | Credential alias/linkage (anti-spoof caution; identifiers may be spoofed). |
| Rare substantive decoded literals | `rare_decoded_literal`, `rare_number_literal`, `recovered_text_value` | Low-frequency genuine content literals; highest signal-to-noise among decoded pivots. |

Confidence tiers: A = exact structural/parent or compound pivot; B = strong shared token;
C = moderate infrastructure pivot; D = weak/shared context only.

## Grouping strategy

`links(samples, edge_types)` groups by token key, never doing O(n^2) all-pairs scans:

1. For parent-family edges, group children by `parent_id`.
2. For token edges, extract a token set from each sample and group sample IDs by token.
3. For template edges, group by exact normalized full text (optionally constrained by kind).
4. For each group with occurrence count inside the type's configured `[min, max]` range,
   emit ID-ordered star edges from the lowest observed ID to each higher ID.
5. Deduplicate identical `(src, dst, edge_type)` tuples.

Star grouping keeps connected reconstruction possible without all-pairs edges and preserves
the ID-ordered direction.

## Spuriousness controls

- Rarity filters: common infra tokens (e.g. destination 2, credential 1, bare ENCODED BLOB)
  are excluded from star expansion unless their group size is within the configured max.
- Token-specific, exact compound pivots (such as shortener code + destination) are preferred
  over broad shared-context edges.
- Direction is ID order only, never real chronology.
- Confidence tiers are recorded and no edge should be treated as proof of a real actor.

## Usage

```python
from forensics.graph import load_samples, links

samples = load_samples()
edges = links(samples, ["parent_child", "shortener_code", "encoded_blob_number"])
# list of (src_id, dst_id, edge_type)
```

## Files

- `forensics/graph.py`
- `forensics/edge_type_catalog.csv`
- `forensics/chain_events.csv`, `content_flow_edges.csv`, `structural_edges.csv` (existing artifacts)
