# v1.0A Invariants/Redaction Validation Evidence

<!-- FANTASY_V10A_INVARIANTS_REDACTION_20260917_V1:BEGIN -->
## Validation Evidence

Pre-state GitHub main:
`984a0373fb7cadd37687f3536f436893296458ba`

Scope:
- new invariant registry/result contract;
- new privacy/redaction primitives;
- observability export update;
- focused tests;
- no football/model/application/GUI call-site integration.

Measured validation:
- targeted observability tests: PASS (38);
- full repository pytest: PASS (391);
- full repository compileall: PASS;
- strict memory health: PASS;
- `git diff --cached --check`: PASS;
- exact staged allowlist: PASS.

Privacy/non-interference tests include:
- recursive sensitive-key redaction;
- Authorization/cookie/ESPN inline secret redaction;
- caller exact-secret replacement;
- binary/depth conservative replacement;
- caller input/event non-mutation;
- keyed deterministic pseudonymization;
- exception message non-disclosure in invariant error results;
- Python RNG state unchanged by invariant/redaction construction.

Evidence class:
`TEST-VALIDATED / NOT YET PRODUCTION-INTEGRATED`.
<!-- FANTASY_V10A_INVARIANTS_REDACTION_20260917_V1:END -->
