# Scope and Plan: Swarm Traces Information Propagation

## Scope
Dataset: Data/redacted.jsonl, 189,579 redacted records (payload, recovered_text, response), no timestamps. ID order is observed only, never chronology. Redaction masks, not identities.

Goal: reconstruct who produced or carried a given piece of information, how it moved through the swarm, whether coordination would have been flagged early, and what remains unprovable.

## Executed plan
1. Dataset baseline and existing work inventory.
2. Define information pieces: byte-identical exact text (SHA256), normalized payload templates, rare pivots/markers (2-25 occurrences), direct parent-child identical content.
3. Build a forward-directed graph (source ID < target ID) with provenance tiers:
   - A: passed_identical_content, parent_of
   - B: exact_echo, template_echo
   - C/D: references_marker, references_information_piece
4. Replay records in ID order and emit earliest coordination flags.
5. Export SQLite, NDJSON, components, DOT, and HTML DAG.
6. Validate acyclicity and propagation counts.
7. Write observer report of unavoidable gaps.

## Deliverables
- Tool: forensics/swarm_propagation_tool.py
- Database: forensics/swarm_propagation_full/swarm_reconstruction.sqlite3
- DAG: forensics/swarm_propagation_full/info_passage_dag.html (+ .dot)
- Early flags: forensics/swarm_propagation_full/early_flags.json
- Report: forensics/swarm_propagation_full/observer_report.md
