# Row-stage label doctrine

The labels `payload`, `response`, and `recovered_text` in `Data/redacted.jsonl` are **mechanical capture-stage labels**.

They are not operational evidence classes and must not be interpreted as:
- attestable page behavior
- proven source / target intent
- execution success
- message provenance

Use them only together with stronger evidence:
- identical or near-identical body matches
- shared low-frequency marker pivots
- explicit lifecycle parent / child links
- externally corroborated report observations

In particular:
- short exact copies in `response` + `recovered_text` may simply be pipeline duplication
- generic shortener `script.src` markers are coupling features, not standalone packet content
- a row being marked `response` does not by itself mean a response observation exists

Use labels as metadata, not explanation.