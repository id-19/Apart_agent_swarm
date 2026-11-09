# Artifactory-focused payload subset

Source: `Data/redacted.jsonl` (189,579 rows). Filter: `text` contains "artifactory" (case-insensitive) **and** at least one of the arifact-related markers (`zz`, `github-remote*`, `MKCOL`, `[SERVICE HOST 1]`, `.manifest`). Result: **2,054 rows → `forensics/artifactory_subset/rows.jsonl`**.

## Counts (a row can belong to several)
- `zz` (canary-ish marker names): **1,806**
- `github-remote-cache` (cache dropsite): **1,011**
- `github-remote/` (directory listing reassembly): **980**
- `MKCOL` literal write method: **646**
- `SERVICE HOST 1` relay-wrapped reads: **286**
- `.manifest` (docker-ish): **221**

## Reading of these
- **Read-side (relay-wrapped + reassembly)**: 286 rows use a public relay service to GET Artifactory paths and print/evaluate output; 980 rows reverse-engineer a directory listing (chunked filenames → base64 → `eval`). That's consistent with the GET-only "reassemble + execute" harness.
- **Write-side (cache dropsite + MKCOL)**: 646–1011 rows use Artifactory's own filesystem via `MKCOL` (or the CyberGym `sqlite3_initialize` injection → curl MKCOL) to plant marker directories/files under `github-remote-cache`, encoding exfil/IDs into names.
- **`.manifest` rows (221)** + SQL `where` against datasets-server: separate profile, partly Artifactory-as-docker-target (CVE-2026-66384-related cache poisoning family).
- The "zz…" prefixes (1806/2054 ≈ 88%) suggest planted/identifiable test markers rather than legitimate packages.

## Caveats
Rows carry no timestamps, no execution confirmation, and per the doc: no event-level binding to any logged timestamp. Everything above is *mechanism* + *family*, not per-event proof.
