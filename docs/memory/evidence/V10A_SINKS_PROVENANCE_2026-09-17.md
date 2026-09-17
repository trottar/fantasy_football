# v1.0A Sinks/Provenance Validation Evidence

<!-- FANTASY_EVIDENCE_V10A_SINKS_PROVENANCE_20260917:BEGIN -->
## Validation evidence

Timestamp: `2026-09-17T12:43:17.557313-04:00`

Pre-state GitHub main:
`fd829ac829e9ffddd38c14e9bca9cd3eaa6a96e3`

Checkpoint:
`v1.0A sinks + provenance slice 2`

Implemented slice:
- `src/observability/sinks.py`
  - explicit `EventSink` protocol;
  - thread-safe in-memory sink;
  - append-only JSONL machine sink;
  - concise human-text sink with payload omitted by default;
  - explicit fanout and batch emission helpers.
- `src/observability/provenance.py`
  - exact-byte SHA-256;
  - canonical semantic JSON SHA-256;
  - file and JSON-file hashing;
  - release-version reader;
  - Git HEAD + tracked-dirty provenance with untracked files ignored;
  - frozen `SourceProvenance` compatible with `RunContext`;
  - `collect_provenance()` returns hashes/identity only, never file contents.

No production call site emits events yet. No global logger/sink is installed. Persistent sinks are not wired to private/authenticated runtime data before the redaction contract exists.

Validation:
- targeted observability tests: PASS (22);
- full pytest: PASS (375);
- full compileall: PASS;
- `git diff --check`: PASS;
- exact staged allowlist: PASS;
- sink/provenance RNG non-interference: PASS;
- human sink default payload omission: PASS;
- canonical JSON order-independence and exact-byte sensitivity: PASS;
- Git provenance dirty/untracked behavior: PASS;
- provenance-content non-disclosure test: PASS.

State:
`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`.

Pre-delivery tooling QA note:
- the first artifact-builder attempt failed at Python parse time because a nested triple-quote delimiter prematurely terminated the generated installer string;
- that attempt produced no delivered checkpoint and made no project/Git modification;
- the builder delimiter was corrected and the successor exact ZIP passed compile, static-global, targeted runtime self-test, whitespace, parser-risk, and CRC checks.

The commissioned v0.36-repack1 football/model/GUI behavior remains unchanged.
<!-- FANTASY_EVIDENCE_V10A_SINKS_PROVENANCE_20260917:END -->
