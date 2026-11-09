# Assembly / Eval Pattern Analysis

Source: `/Users/id19/.../forensics/artifactory_subset/rows.jsonl` (2,054 rows).

## Row counts

- Rows matching the assembly/eval pattern (directory-listing parse and/or `eval` + `atob`): **303**.
- Subset containing `matchAll(/href=.../g)` directory-listing parse: **294**.
- Subset containing `eval` + `atob`: **92**.
- Variants within matched rows:
  - async wrappers: **233** rows contain `async` (remaining use sync XHR or `.then` chains).
  - `eval(...)` invocations: **90**.
  - `eval(atob(...))` direct eval: **70**.
  - `JSON.parse(atob(...))` decoding (then used to drive further fetch/writes): **109**.
  - gzip via `DecompressionStream`: **54**.
  - `BOOTERR`/`LOADERR`/`ERR` error paths: **13** BOOTERR, **22** LOADERR.
  - XHR synchronous fetch: **16**.
  - Beacons `new Image`: **142**.
  - Docker registry interaction: **150**.
- Hosts read: primarily `[SERVICE HOST 1]` (35-36 rows) and `[SERVICE HOST 9]` (5 rows), all in front of `packages.hub.ace-research.openai.org/artifactory/github-remote*` directory listings.

## Reconstruction algorithm

1. Fetch an Artifactory directory listing HTML page for a path such as
   `.../github-remote/<DIRNAME>/` or `.../github-remote-cache/<DIRNAME>/`.
2. Parse the directory HTML with `matchAll(/href="(\d+)_([^"/]+)\//g)` (or `(\d{3})_` / `(\d+)of\d+_` variants). Capture chunk ordinal and chunk payload token.
3. Store chunks in an array at their ordinal index (`a[+m[1]]=m[2]`), yielding ordered reassembly by numeric prefix.
4. Join chunk tokens with `''`.
5. Convert from URL-safe base64 to standard base64:
   - replace `-` -> `+`
   - replace `_` -> `/`
   - add `=` padding to a multiple of 4 (`'='.repeat((4 - q.length % 4) % 4)`).
6. `atob(...)` decode.
7. Variant endpoints:
   - Direct execution: `eval(atob(s))`.
   - JSON mode: `JSON.parse(atob(q))`, yielding `{config, manifest}` used in subsequent Docker registry `POST`/`PUT`.
   - gzip mode: `new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).text()` then `eval`.
   - Error handling is usually `catch(e){...BOOTERR/LOADERR/ERR...}` plus an image beacon.

## Examples of reassembled payloads

Directory names encode intended modules, e.g.:
- `zzFILE_SK7189C_TESTLOAD`, `zzFILE_SK7189C_REGMONO`
- `zzFILE_AF11FEB27_HYB_V1`
- `zzFILE_33340C64_PUSHJS_V1`, `zzFILE_33340C64_HYBDATA_V2`
- `zzFILE_URI23816D_SUBMITJS_V1/V2`, `zzURI23816C2_PUSHJSV1`
- `zzFILE_JSON18140SEP29_MODALCAUSAL2/3_JS`
- `zzFILE_3862HYBRID_CONFIG_V1`
- `zzFILE_ARVO1538LONG_RELAYJS1`, `zzFILE_ARVO1538_MODAL*`
- `zzFILE_4322A_PUSHV5_JS`
- `zzFILE_LIBJXL3733_R6JS_V1`, `zzVP9BOOTJS_NEST1`
- Many PUSH/CONFIG/DATA/HYBRID/OCI variants.

Each directory's reassembled base64 likely represents compressed/encoded JavaScript or JSON configuration data; chunks are ordered by filename numeric prefixes.

## Links to other rows sharing directory names

Many directory names recur across multiple rows (83 shared names). Examples include `zzFILE_33340C64_PUSHJS_V1` (9 rows), `zzFILE_JSON18140SEP29_MODALCAUSAL3_JS` (6 rows), `zzFILE_URI23816D_SUBMITJS_V1/V2`, `zzFILE_3862HYBRID_CONFIG_V1` (5 rows). Thus assembly rows are not isolated; repeated use of the same module/directory across multiple row records is common.

## Risks / observed stops

- Pattern is inherently code execution via `eval(atob(...))`; if chunk assembly/ordering or base64 is malformed, `atob`/`eval` throws and surfaces `BOOTERR`/`LOADERR`.
- Directory-listing HTML scraping is fragile; regex misses if listing format changes or if `href` quoting/order differs.
- The same pattern is used to drive Docker registry writes (config/manifest push) in some variants, turning assembly output into supply-chain/write actions.
- Read paths only for assembly itself (directory listing fetch + eval), but downstream steps can write (image registry) depending on row variant.
- Some rows include gzip decompression; decompression errors would abort execution.
- Beaconing (`new Image`) can exfiltrate execution status.

## Read-only vs write conclusions

- The assembly algorithm itself is a read operation against Artifactory directory listings, followed by client-side decoding/execution.
- Write actions are not inherent to the parsing step; they occur only in specific variants (notably Docker registry upload/manifest PUT and registry interactions).
- Rows should be treated as potentially executable payload recipes; analysis here was read-only.
