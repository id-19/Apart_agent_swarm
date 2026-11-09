# Core findings

- Retained Rows: 187242.
- Non-candidate graph edges: 1505515.
- Active projected edge classes: EXACT_BODY, INTENT_SIGNATURE, MARKER_ENDPOINT, MARKER_SAME, NORMALIZED_REPLAY, PARENT_DIRECT, PARENT_MUTATION, SAME_PARENT_SIBLING, TIMESTAMP_ANCHOR.
- Largest G_CORE component: 141,970 rows; this is chiefly a co-occurrence effect from shared marker/endpoint links, not proof of single operational intent.
- Exact validation found 0 failed resolved structural edges and 2 unresolved parent-link endpoints from ghost parent R0113768.
- The top structural risk indicators are exact-body repetition, normalized replay, repeated credential/service/pivot markers, parent-star bursts, and command-injection mutation templates.
- Time cues cannot establish actor ordering; they are evidence metadata only.
- External chronologies (38 dated events) cannot be assigned to individual Swarm rows because all source time_utc values are null.
