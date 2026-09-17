# D-010 — Phase 0 Final 0.X Authority

<!-- FANTASY_D010_PHASE0_FINAL_AUTHORITY:BEGIN -->
## Decision

Treat v0.36 as the latest **source-validated 0.X candidate**, but do not treat the
existing v0.36 ZIP as a valid commissioned release.

### Basis

The only deterministic test regression in the packaged artifact was traced to
four omitted mock-draft calibration fixtures. Restoring only those fixtures in
a disposable exact-v0.36 extraction caused both failing tests and the complete
suite to pass. No football/model/application source or config change was needed.

### Consequences

1. Football/model reasoning may use v0.36 as the latest validated 0.X source
   candidate.
2. The existing v0.36 ZIP is rejected for commissioning/delivery.
3. No historical v0.36-fixed1 should be inferred.
4. A packaging-only repaired artifact may be created after explicit
   production/release authorization.
5. Durable import of v0.36 source should occur in the same authorized release
   checkpoint.
6. v1.0A implementation begins only after that source/release boundary is made
   durable and validated.
<!-- FANTASY_D010_PHASE0_FINAL_AUTHORITY:END -->
