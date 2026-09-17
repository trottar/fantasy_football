# v0.36 release notes

## Scope

Bounded higher-order player-channel league response around released-player counterfactuals. No 2026 game outcome is used for tuning.

## Physics/response contract

- Preserve commissioned order 1 exactly.
- Propagate only causally seeded recipient releases to orders 2+.
- Released players become available no earlier than the following modeled week.
- Player channel only: QB/RB/WR/TE.
- Branch probabilities multiply along the response path.
- Orders 2+ use paired predictive football MC under CRN after screen-only claimant pruning.
- Stop by depth, branch probability, incremental field response, branch limits, cycle guard, or season boundary.
- Surface order decomposition, higher-order MC size, pruned probability mass, and stop reasons.

## Prospective measurement

The v0.34 a-priori capture contract remains unchanged. v0.36 records its cascade architecture and stopping parameters before any outcome-informed calibration.

## Commissioning target

The source-only runtime has two inherited mock-draft tests that require the user's migrated `data/mock_drafts` files. With commissioned data migrated from v0.35-fixed1, the expected complete suite is 353 tests.
