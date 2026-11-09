# Artifactory Read-Side Analysis

Source: `/Users/id19/.../forensics/artifactory_subset/rows.jsonl` (2054 rows).

## Distinct read patterns
1. Relay-wrapped fetches via `[SERVICE HOST 1]` — 284 rows; example `R0000032` slices first 1000 chars.
2. Directory listing reassembly / eval(atob) — 239 rows; example `R0000614` parses hrefs and evals atob.
3. Docker manifest probes — 233 rows; example `R0000717`.
4. Direct Artifactory GETs bundled with probes.

## Abuse vs legitimate
SSRF-style relay, eval(atob) payload reassembly, canary markers, hardcoded creds.

## Read-write pairs
121 read rows overlap 68 write markers; examples listed in prior analysis.

## Relay
Likely internal gateway.