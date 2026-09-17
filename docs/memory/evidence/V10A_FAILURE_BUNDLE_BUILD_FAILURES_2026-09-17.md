# v1.0A Failure-Bundle Package / Delivery Failures

<!-- FANTASY_EVIDENCE_V10A_FAILURE_BUNDLE_BUILD_FAILURES_20260917:BEGIN -->
## Failure record

Four assistant-side defects occurred during construction/QA/delivery of the
failure-bundle checkpoint:

1. **Builder quote-boundary defect — pre-delivery.** The first package-builder
   attempt embedded an inner triple-quoted memory template inside an outer
   triple-quoted installer string. Python raised `SyntaxError` before a package
   was produced.
2. **Synthetic tamper-fixture defect — pre-delivery QA.** The first tamper test
   rewrote an already-empty `{}` state-summary file with identical bytes and
   incorrectly expected integrity verification to fail. This exposed a defective
   QA fixture, not a bundle-integrity defect.
3. **Delivered v1 predecessor-hash representation defect.** At 2026-09-17
   14:19 local time, `fantasy_v10a_failure_bundle_checkpoint_20260917_v1.zip`
   captured GitHub main `304f84c4deb8557e759afc6ebb10daf501bfe01e` and then
   failed its predecessor guard with:
   `FAILED BEFORE MODIFICATION: observability __init__ changed from expected predecessor`.
   GitHub verification showed the repository file was unchanged and had Git blob
   object ID `2af28d7f3cd2743827df5451ca8991f062472da8`. The v1
   installer incorrectly computed a 64-character SHA-256 over file bytes and
   compared it against that 40-character Git blob object ID. Those values use
   different algorithms/representations and cannot be compared.
4. **v2 patch-builder syntax defect — pre-delivery.** The first attempt to build
   the v2 correction used a malformed quoting expression in the package-builder
   script itself. Python rejected that builder before it could produce v2 or
   touch any project repository.

Classification of delivered v1:
`INVALID / SUPERSEDED / FAILED BEFORE MODIFICATION`.

Modification state for delivered-v1 failure:
- payload copied into staging clone: NO;
- project source modified: NO;
- durable memory modified: NO;
- commit created: NO;
- push attempted: NO;
- GitHub main moved by the failed run: NO.

Corrective rule:
when validating a predecessor, hash algorithm, byte representation, and
authority layer must match. Git blob object IDs must be compared to Git blob
object IDs; SHA-256 byte checksums must be compared to SHA-256 checksums over the
same byte representation. The successor v2 uses `git rev-parse HEAD:<path>` and
explicitly validates a 40-character Git blob object ID.
<!-- FANTASY_EVIDENCE_V10A_FAILURE_BUNDLE_BUILD_FAILURES_20260917:END -->
