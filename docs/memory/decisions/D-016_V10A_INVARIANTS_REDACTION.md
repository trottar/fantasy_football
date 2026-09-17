# D-016 — v1.0A Invariants and Privacy/Redaction

<!-- FANTASY_D016_V10A_INVARIANTS_REDACTION:BEGIN -->
## Decision

Adopt immutable invariant-result contracts and conservative privacy/redaction
primitives before any production event emission.

### Invariants

Invariant definitions are named evidence contracts. This slice does not turn
invariants into hidden production enforcement or decision logic.

Results preserve epistemic state explicitly as `PASS`, `FAIL`, `SKIP`, or
`ERROR`. Error results may record exception type but do not automatically retain
raw exception messages because those may contain secrets/private payloads.

### Redaction

Redaction is explicit and copy-only. It does not mutate source events or data.
Default policy conservatively redacts authentication/secrets and private runtime
identifier keys, known inline Authorization/cookie/ESPN credential patterns,
and binary blobs. Callers may additionally supply exact secret values.

Pseudonymization is caller-keyed HMAC; no global key or persistent secret is
introduced.

### Integration boundary

Existing sinks remain explicit/caller-owned and are not silently changed. No
persistent private/authenticated runtime emission is enabled by this decision.
A later integration checkpoint must explicitly apply the redaction contract and
prove non-interference/privacy before production emission is authorized.
<!-- FANTASY_D016_V10A_INVARIANTS_REDACTION:END -->
