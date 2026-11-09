# Early detection verdict

Structural families can be flagged earlier than full payload accumulation, but only as candidates:

- parent-star bursts,
- exact and normalized replay loops,
- credential, service-host, destination, proxy, shortener, and packed payload markers,
- stage/exfiltration command mutation templates,
- overlapping read-into-write patterns in sibling sets,
- bounded near-body similarity among known endpoints.

A proportional detector should require parent provenance, marker rareness, repetition, and operational context; broad markers such as generic slots and container shards can otherwise create false positives.
