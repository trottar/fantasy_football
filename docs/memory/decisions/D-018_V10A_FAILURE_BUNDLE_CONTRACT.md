# D-018 — v1.0A Failure-Bundle Contract

<!-- FANTASY_D018_V10A_FAILURE_BUNDLE:BEGIN -->
## Decision

Adopt a bounded privacy-safe local failure-bundle contract before production
observability integration.

Default exception evidence retains exception type while omitting raw message
text. Stack evidence uses file basenames/function/line only. Caller-supplied
structured state, reproduction metadata, event tails, invariant tails,
project-file modification state, and runtime side effects are redacted before
persistence. Exact-byte manifests make tampering detectable.

Failure bundles are evidence only. They do not define exception recovery, alter
application control flow, emit automatically, or enable private/authenticated
persistence.
<!-- FANTASY_D018_V10A_FAILURE_BUNDLE:END -->
