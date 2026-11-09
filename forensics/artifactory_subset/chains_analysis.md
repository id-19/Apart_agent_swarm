# Parentage / chain analysis of redacted.jsonl

## Dataset stats
- Total rows: 189579
- Kinds: payload 91037, recovered_text 75534, response 23008
- Roots (parent_id null): 128454
- Rows with valid parent: 61125 (all depth 1; max parent-depth = 1 edge)
- Distinct parents: 26248
- Hubs with >10 children: 912 (covering 13630 child rows); max 858 (R0024455)

## Chain topology
No deep chains exist under parent_id: structure is star-like (payload parent -> many recovered_text/response children), not multi-hop. "chains" are effectively 2-level: a payload request and its derived recovered texts/responses. Topology classes:
- Root: payload (init)
- Branch/continuation: recovered_text (often derived artifacts/transcripts)
- Terminal: response (final outputs)

## Position classification
- Init: payload rows issuing outbound requests (HTTP fetch/XHR) and command text.
- Continuation: recovered_text reconstructing directory scans / prior artifacts.
- Terminal: response rows returning prior operation results.

## Artifactory / HF
- Artifactory mentions in 2211 rows; HF in many API/dataset/model calls.
- Artifactory directory reads (`artifactory/github-remote/...`, `/api/search/artifact`, `/api/search/aql`) feed subsequent write targets in some rows (`github-remote-cache/...` uses same repo/dir prefixes).
- Observed read->write dependency: directory names under `github-remote/` recur as cache write targets under `github-remote-cache/`, indicating derived cache writes based on prior directory listings.

## Cross-chain connections
- Parent-child links via payload id; heavy hubs aggregate many artifacts into one request context.
- Cross-domain overlap: Artifactory cached remote GitHub layers and HF dataset/model identifiers appear in same recovered transcripts, suggesting shared artifact namespaces rather than isolated chains.
