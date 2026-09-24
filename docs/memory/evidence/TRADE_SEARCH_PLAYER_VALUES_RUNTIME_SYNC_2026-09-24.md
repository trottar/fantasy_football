# Trade Search Player-Values Runtime Synchronization — 2026-09-24

## Purpose

Resolve the commissioned runtime's missing automatic trade-search
`data/processed/player_values_2026.csv` dependency with explicit provenance and
without changing football/model logic.

## Read-Only Dependency Inventory

Diagnostic package:
`trade_search_player_values_inventory_20260924_v1`.

Measured commissioned runtime source identities:

- `src/market_manager.py`:
  `b384776b7bf1338af778a1ef146700755d87b340`;
- `src/gui/season_service.py`:
  `733d32d7a8a62cf3dc9e88163971d0bd285edf87`.

Measured path contract:

- `SeasonGuiService` default:
  `data/processed/player_values_2026.csv`;
- `SeasonGuiService.reload()` requires the file to exist;
- `trade_search()` forwards `self.values_path`;
- `market_manager.search_trades()` accepts `values_path` explicitly.

Pre-synchronization runtime target:

`fantasy_season_v0_36_repack1/data/processed/player_values_2026.csv`:
**ABSENT**.

The bounded inventory found three exact candidates:

| Root | Version | Bytes | Rows | SHA-256 |
| --- | --- | ---: | ---: | --- |
| control root | n/a | 361778 | 939 | `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d` |
| `fantasy_season_v0_35_fixed1` | `0.35-fixed1` | 361778 | 939 | `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d` |
| `fantasy_season_v0_36` | `0.36` | 361778 | 939 | `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d` |

All three candidates had:

- no CSV parse error;
- required columns `espn_id`, `latent_mean_ppg`;
- optional model columns `latent_mean_sd_ppg`,
  `predictive_weekly_sd_ppg`.

Classification:
`DEFAULT_MISSING / PRIOR_SHA_MATCH_AVAILABLE`.

## Synchronization Mechanism

The accepted mechanism is an explicit runtime synchronization from the
control-root artifact to the same relative path in the commissioned runtime.

Required preconditions:

1. control-root source SHA-256 is exactly `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`;
2. source byte count is exactly `361778`;
3. the v0.35-fixed1 and v0.36 sibling artifacts, when present at the expected
   path, have the same exact SHA-256;
4. commissioned runtime is `VERSION = 0.36`;
5. commissioned `market_manager.py` and `season_service.py` retain the exact
   measured source identities;
6. runtime target is either absent or already has the exact target SHA.

The operation does not alter:

- trade-screen logic;
- predictive MC;
- player/DST/K channel boundaries;
- trade perception or response formulas;
- observability boundaries;
- calibration state.

## Post-Synchronization Validation

The synchronization package validates:

- runtime target SHA-256 and byte count;
- CSV row count and required/optional schema;
- runtime model-value loading through
  `transaction_manager._load_model_value_index`;
- runtime weekly fallback loading through
  `weekly_manager._load_model_values`;
- exact commissioned source identities remain unchanged;
- strict durable-memory health;
- Git index identity unchanged;
- no staging, commit, push, or trade-search execution.

Expected runtime artifact:

`fantasy_season_v0_36_repack1/data/processed/player_values_2026.csv`

SHA-256:
`4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.

## State Boundary

After all package gates pass:

**RUNTIME-DATA-SYNCED / TRADE-SEARCH-DEPENDENCY-READY**

The next action is not an immediate reuse of an old decision state. Obtain a
fresh prospective decision-time season state/capture, then run the first
league-wide trade search against that frozen state.
