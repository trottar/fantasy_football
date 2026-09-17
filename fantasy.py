#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.draft_state import DraftState
from src.league import load_league, user_overall_picks
from src.scoring import score_offense, score_kicker, score_dst


DEFAULT_LEAGUE = Path("config/league.json")
DEFAULT_MODEL = Path("config/model.json")
DEFAULT_STATE = Path("data/draft_state.json")
RAW_ESPN = Path("data/raw/espn")
RAW_NFLVERSE = Path("data/raw/nflverse")
PROCESSED = Path("data/processed")
DEFAULT_SECRETS = None
SEASON_SNAPSHOTS = Path("data/season_snapshots")
INTERACTION_GRID_DIR = Path("data/fitted_models/interaction_grids/v001")
INTERACTION_CACHE = Path("data/raw/nflverse_matchups")
CLOSURE_PREDICTIONS = Path("data/season_predictions/closure")
CLOSURE_ROOT = Path("data/season_closure")
CLOSURE_RAW = Path("data/raw/nflverse/closure")


def cmd_league(args):
    print(json.dumps(load_league(args.league), indent=2))


def cmd_picks(args):
    league = load_league(args.league)
    d = league["draft"]
    picks = user_overall_picks(league["teams"], d["rounds"], d["user_draft_slot"])
    print("User overall picks:")
    print(", ".join(str(x) for x in picks))


def cmd_init(args):
    league = load_league(args.league)
    d = league["draft"]
    state = DraftState(league["teams"], d["rounds"], d["user_draft_slot"])
    state.save(args.state)
    print(f"Initialized draft state: {args.state}")


def cmd_record(args):
    state = DraftState.load(args.state)

    if args.board:
        from src.live_draft import load_board, resolve_player
        board = load_board(args.board)
        row = resolve_player(board, args.name)
        espn_id = int(row["espn_id"])
        pick = state.record_pick(
            str(espn_id),
            str(row["name"]),
            str(row["position"]),
            str(row.get("nfl_team") or ""),
            espn_id=espn_id,
        )
    else:
        player_id = args.player_id or args.name.lower().replace(" ", "_")
        pick = state.record_pick(
            player_id, args.name, args.position, args.nfl_team
        )

    state.save(args.state)
    print(json.dumps(pick, indent=2))


def cmd_status(args):
    state = DraftState.load(args.state)
    print(f"Recorded picks: {len(state.picks)}/{state.total_picks}")
    print(f"Next overall pick: {state.next_overall}")
    rnd, pick_in_round, slot = state.expected_slot_for_pick(state.next_overall)
    print(f"Next: round {rnd}, pick {pick_in_round}, draft slot {slot}")
    roster = state.roster_for_slot(state.user_draft_slot)
    if roster:
        print("\nUser roster:")
        for p in roster:
            print(f'  {p["overall"]:>3}: {p["player_name"]} ({p.get("position") or "?"})')
    else:
        print("\nUser roster: empty")


def cmd_score(args):
    stats = json.loads(args.stats)
    if args.kind == "offense":
        points = score_offense(stats)
    elif args.kind == "kicker":
        points = score_kicker(stats)
    else:
        points = score_dst(stats)
    print(f"{points:.3f}")


def cmd_sync_espn(args):
    from src.data_sources.espn import sync_espn
    cfg = json.loads(Path(args.model).read_text())["espn"]
    result = sync_espn(
        args.out,
        season=int(cfg["season"]),
        scoring_default_id=int(cfg["scoring_default_id"]),
        rank_type=str(cfg["rank_type"]),
        limit=int(cfg["limit"]),
    )
    for key, value in result.items():
        print(f"{key}: {value}")


def cmd_sync_nflverse(args):
    from src.data_sources.nflverse import sync_nflverse
    seasons = None
    if getattr(args, "seasons", None):
        seasons = [int(x) for x in str(args.seasons).split(",") if str(x).strip()]
    elif getattr(args, "model", None):
        model = json.loads(Path(args.model).read_text(encoding="utf-8"))
        seasons = [int(x) for x in (((model.get("interaction_grid") or {}).get("fit") or {}).get("seasons") or [])]
        if not seasons:
            seasons = None
    result = sync_nflverse(args.out, force=args.force, seasons=seasons)
    for key, value in result.items():
        print(f"{key}: {value}")
    if seasons:
        print(f"player_stats_seasons: {','.join(str(s) for s in seasons)}")


def cmd_build_priors(args):
    from src.historical import build_historical_priors
    out = build_historical_priors(args.stats, args.model, args.out)
    print(f"Wrote {len(out)} historical priors: {args.out}")




def cmd_interaction_fit(args):
    from src.interaction_fit import fit_interaction_grids
    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    seasons = [int(x) for x in args.seasons.split(",")] if args.seasons else None
    try:
        result = fit_interaction_grids(
            stats_path=args.stats,
            model=model,
            cache_dir=args.cache,
            out_dir=args.out,
            seasons=seasons,
        )
    except ValueError as exc:
        failure_path = Path(args.out) / "fit_failure.json"
        if not failure_path.exists():
            from datetime import datetime, timezone
            failure_path.parent.mkdir(parents=True, exist_ok=True)
            failure_path.write_text(json.dumps({
                "failed_utc": datetime.now(timezone.utc).isoformat(),
                "model_version": "0.28",
                "reason": str(exc),
                "coverage_path": str(Path(args.out) / "coverage.json") if (Path(args.out) / "coverage.json").exists() else None,
            }, indent=2), encoding="utf-8")
        print(f"ERROR: {exc}")
        print(f"Latest fit status: {failure_path}")
        raise SystemExit(2) from None
    validation = json.loads(result.validation_path.read_text(encoding="utf-8"))
    commissioned = 0
    total = 0
    for group in (validation.get("components") or {}).values():
        for row in group.values():
            total += 1
            commissioned += int(bool(row.get("commissioned")))
    print(f"Interaction artifact: {result.artifact_dir}")
    print(f"Training rows: {result.rows}")
    print(f"Grids: {result.grids}")
    print(f"Chronologically commissioned components: {commissioned}/{total}")
    print(f"Manifest: {result.manifest_path}")
    print(f"Validation: {result.validation_path}")


def cmd_interaction_status(args):
    root = Path(args.artifact)
    manifest = root / "manifest.json"
    validation_path = root / "validation.json"
    failure_path = root / "fit_failure.json"
    if failure_path.exists():
        try:
            failure = json.loads(failure_path.read_text(encoding="utf-8"))
        except Exception:
            failure = {"reason": "unreadable fit_failure.json"}
        manifest_is_older = (not manifest.exists()) or failure_path.stat().st_mtime >= manifest.stat().st_mtime
        if manifest_is_older:
            print("LATEST INTERACTION FIT: FAILED")
            print(f"  reason: {failure.get('reason')}")
            if failure.get("coverage_path"):
                print(f"  coverage: {failure.get('coverage_path')}")
            if not manifest.exists():
                return
            print("  existing artifact below is from an earlier fit and is STALE")
    if not manifest.exists():
        print(f"MISSING interaction artifact: {root}")
        return
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    print(f"Artifact: {payload.get('artifact_id')}  model={payload.get('model_version')}")
    print(f"Training seasons: {payload.get('training_seasons')}")
    print(f"Training rows: {payload.get('training_rows_total')}  grids={payload.get('grids')}")
    print(f"Fantasy points used in fit: {payload.get('fantasy_points_used_in_fit')}")
    if validation_path.exists():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        print(f"Validation season: {validation.get('validation_season')}")
        coverage = validation.get("coverage") or {}
        if coverage:
            print(
                "Validation coverage: "
                f"rows={int(coverage.get('rows') or 0)} "
                f"opponent={int(coverage.get('opponent_present') or 0)} "
                f"defense_matched={int(coverage.get('defense_matched') or 0)} "
                f"fraction={float(coverage.get('defense_match_fraction') or 0.0):.3f}"
            )
        for pos, group in (validation.get("components") or {}).items():
            for component, row in group.items():
                flag = "COMMISSIONED" if row.get("commissioned") else "SHADOW"
                before = row.get("mae_ratio_before")
                after = row.get("mae_ratio_after")
                print(f"  {pos:2} {component:30} {flag:12} n={int(row.get('n') or 0):4} MAE {before:.4f}->{after:.4f}" if isinstance(before, (int,float)) and isinstance(after, (int,float)) else f"  {pos:2} {component:30} {flag}")

def cmd_build_master(args):
    from src.player_master import build_player_master
    out = build_player_master(args.espn, args.players, args.priors, args.out)
    n_ids = int(out["has_nflverse_id"].sum()) if len(out) else 0
    n_prior = int(out["has_historical_prior"].sum()) if len(out) else 0
    print(f"Wrote {len(out)} ESPN players: {args.out}")
    print(f"Matched nflverse IDs: {n_ids}/{len(out)}")
    print(f"Historical priors: {n_prior}/{len(out)}")


def cmd_data_status(args):
    paths = {
        "ESPN normalized": RAW_ESPN / "player_pool_2026.csv",
        "nflverse players": RAW_NFLVERSE / "players.csv",
        "nflverse stats": RAW_NFLVERSE / "player_stats.csv.gz",
        "historical priors": PROCESSED / "historical_priors.csv",
        "player master": PROCESSED / "player_master.csv",
        "player values": PROCESSED / "player_values_2026.csv",
        "projection calib": PROCESSED / "projection_calibration.json",
        "transition calib": PROCESSED / "transition_calibration.json",
        "draft values": PROCESSED / "draft_values_2026.csv",
        "draft diagnostics": PROCESSED / "draft_value_diagnostics.json",
        "draft market": PROCESSED / "draft_market_2026.csv",
        "market diagnostics": PROCESSED / "draft_market_diagnostics.json",
        "live board": PROCESSED / "live_board_2026.csv",
        "interaction grids": INTERACTION_GRID_DIR / "manifest.json",
    }
    for label, path in paths.items():
        status = "OK" if path.exists() else "MISSING"
        size = f"{path.stat().st_size / 1e6:.1f} MB" if path.exists() else ""
        print(f"{status:7} {label:20} {str(path):50} {size}")



def cmd_inspect_data(args):
    from src.diagnostics import build_data_diagnostics, print_data_diagnostics
    result = build_data_diagnostics(
        args.master,
        args.priors,
        args.out,
        top_n=args.top_n,
    )
    print_data_diagnostics(
        result,
        unmatched_limit=args.unmatched_limit,
        board_limit=args.board_limit,
    )


def cmd_projection_status(args):
    from src.diagnostics import projection_coverage
    table = projection_coverage(args.master)
    print("=== ESPN PROJECTION COVERAGE ===")
    print(table.to_string(index=False))


def cmd_build_values(args):
    from src.player_value import build_player_values, player_value_summary
    out, calibration = build_player_values(
        args.master,
        args.model,
        args.out,
        calibration_path=args.calibration,
        stats_path=args.stats,
        transition_path=args.transition,
    )
    print("=== TRANSITION + PROJECTION UNCERTAINTY CALIBRATION ===")
    for pos, info in calibration.items():
        print(
            f'{pos:>2}: n={info["n"]:>3} '
            f'resid={info["residual_sigma_ppg"]:.3f} '
            f'transition={info["historical_transition_sigma_ppg"]:.3f} '
            f'projection={info["projection_sigma_ppg"]:.3f} PPG'
        )
    print("\n=== PLAYER VALUE COVERAGE ===")
    print(player_value_summary(out).to_string(index=False))
    print(f"\nWrote {len(out)} core-position player values: {args.out}")


def cmd_value_board(args):
    import pandas as pd
    df = pd.read_csv(args.values, low_memory=False)
    for col in ["espn_adp", "espn_rank", "latent_mean_ppg"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if args.by == "market":
        df = df.sort_values(["espn_adp", "espn_rank"], na_position="last")
    else:
        df = df.sort_values(["latent_mean_ppg", "espn_adp"], ascending=[False, True], na_position="last")

    cols = [
        c for c in [
            "name", "position", "nfl_team", "espn_adp", "espn_rank",
            "projection_ppg", "historical_prior_mean_ppg",
            "latent_mean_ppg", "latent_mean_sd_ppg",
            "predictive_weekly_sd_ppg", "history_weight",
            "projection_weight", "model_status", "injury_status"
        ] if c in df.columns
    ]
    print(df[cols].head(args.limit).to_string(index=False))


def cmd_build_draft_values(args):
    from src.draft_value import build_draft_values, print_draft_value_summary
    out, diagnostics = build_draft_values(
        args.values,
        args.league,
        args.model,
        args.out,
        diagnostics_path=args.diagnostics,
    )
    print_draft_value_summary(diagnostics)
    print(f"\nWrote {len(out)} draft-value rows: {args.out}")


def cmd_draft_board(args):
    import pandas as pd
    df = pd.read_csv(args.values, low_memory=False)

    if args.position:
        df = df[df["position"].eq(args.position)]

    if args.by == "market":
        df = df.sort_values(["espn_adp", "espn_rank"], na_position="last")
    elif args.by == "vorp":
        df = df.sort_values(
            ["vorp_ppg", "espn_adp"],
            ascending=[False, True],
            na_position="last",
        )
    else:
        df = df.sort_values(
            ["draft_value_score", "espn_adp"],
            ascending=[False, True],
            na_position="last",
        )

    cols = [
        c for c in [
            "name", "position", "nfl_team",
            "espn_adp", "espn_rank",
            "latent_mean_ppg", "latent_mean_sd_ppg",
            "position_rank_model", "tier",
            "starter_advantage_ppg", "vorp_ppg",
            "vorp_conservative_ppg",
            "scarcity_gap_next_n_ppg",
            "draft_value_score",
            "model_status", "injury_status",
        ] if c in df.columns
    ]
    print(df[cols].head(args.limit).to_string(index=False))


def cmd_build_market(args):
    from src.draft_market import build_market_values, print_market_diagnostics
    out, diag = build_market_values(
        args.values,
        args.league,
        args.model,
        args.out,
        diagnostics_path=args.diagnostics,
    )
    print_market_diagnostics(diag)
    print(f"\nWrote {len(out)} market rows: {args.out}")


def cmd_survival_board(args):
    import pandas as pd
    from src.draft_market import add_survival_to_target, next_user_pick

    df = pd.read_csv(args.values, low_memory=False)

    target = args.target_pick
    if target is None:
        league = json.loads(Path(args.league).read_text())
        d = league["draft"]
        target = next_user_pick(
            args.current_pick,
            int(league["teams"]),
            int(d["rounds"]),
            int(d["user_draft_slot"]),
        )
        if target is None:
            raise ValueError("No later user draft pick exists.")

    df = add_survival_to_target(df, args.current_pick, target)
    pcol = f"p_available_pick_{target}"

    # Only current-market eligible players with a market center.
    mask = df["draft_eligible"].astype(str).str.lower().isin(["true", "1", "yes"])
    df = df[mask & df["market_pick_mean"].notna()].copy()

    if args.position:
        df = df[df["position"].eq(args.position)]

    # Focus on players plausibly relevant from the current pick onward.
    df["espn_adp"] = pd.to_numeric(df["espn_adp"], errors="coerce")
    df["draft_value_score"] = pd.to_numeric(df["draft_value_score"], errors="coerce")
    df[pcol] = pd.to_numeric(df[pcol], errors="coerce")

    if args.by == "urgency":
        df["urgency_score"] = df["draft_value_score"] * (1.0 - df[pcol])
        df = df.sort_values(
            ["urgency_score", "draft_value_score"],
            ascending=[False, False],
        )
    elif args.by == "market":
        df = df.sort_values(["espn_adp", "espn_rank"], na_position="last")
    else:
        df = df.sort_values(
            ["draft_value_score", "espn_adp"],
            ascending=[False, True],
            na_position="last",
        )

    cols = [
        c for c in [
            "name", "position", "nfl_team",
            "espn_adp", "espn_rank",
            "draft_value_score", "tier",
            "market_pick_mean", "market_pick_sigma",
            pcol, "urgency_score",
            "injury_status",
        ] if c in df.columns
    ]

    print(f"Current pick: {args.current_pick}")
    print(f"Target pick:  {target}")
    print(df[cols].head(args.limit).to_string(index=False))


def cmd_build_live_board(args):
    from src.pipeline import build_live_board
    out, diag = build_live_board(
        args.values,
        args.league,
        args.model,
        args.market_pre,
        args.draft_values,
        args.out,
        args.market_diagnostics,
        args.draft_diagnostics,
    )
    print("=== ELIGIBILITY-AWARE REPLACEMENT LEVELS ===")
    from src.draft_value import print_draft_value_summary
    print_draft_value_summary(diag)
    eligible = out["draft_eligible"].astype(str).str.lower().isin(["true", "1", "yes"])
    print(f"\nEligible rows in live board: {int(eligible.sum())}/{len(out)}")
    print(f"Live board: {args.out}")


def cmd_live_board(args):
    from src.live_draft import (
        load_board, available_board, add_dynamic_values
    )
    state = DraftState.load(args.state)
    board = load_board(args.board)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    cfg = model["draft_value"]

    avail = available_board(board, state)
    dyn, repl = add_dynamic_values(
        avail, state,
        cfg["expected_rostered_counts"],
        scarcity_lookahead=int(cfg["scarcity_lookahead_players"]),
        scarcity_weight=float(model["live_draft"]["scarcity_weight"]),
    )

    print(f"Next overall pick: {state.next_overall}")
    print(f"Available draft-eligible players: {len(dyn)}")
    print("\\n=== DYNAMIC REPLACEMENT ===")
    for pos, info in repl.items():
        print(
            f'{pos:>2}: drafted={info["drafted"]:>2} '
            f'remaining_expected={info["remaining_expected_rostered"]:>2} '
            f'replacement={info["replacement_ppg"]:6.3f} '
            f'({info["replacement_player"]})'
        )

    if args.position:
        dyn = dyn[dyn["position"].eq(args.position)]

    dyn = dyn.sort_values(
        ["dynamic_draft_value", "espn_adp"],
        ascending=[False, True],
        na_position="last",
    )
    cols = [
        c for c in [
            "espn_id", "name", "position", "nfl_team", "espn_adp",
            "latent_mean_ppg", "latent_mean_sd_ppg", "tier",
            "dynamic_replacement_ppg", "dynamic_vorp_ppg",
            "dynamic_scarcity_gap_ppg", "dynamic_draft_value",
            "injury_status"
        ] if c in dyn.columns
    ]
    print("\\n" + dyn[cols].head(args.limit).to_string(index=False))


def cmd_recommend(args):
    from src.fast_recommend import evaluate_candidates_fast
    from src.full_rollout import evaluate_candidates_full_rollout
    from src.forecast import (
        forecast_next_user_pick_deep,
        forecast_next_user_pick_fast,
    )
    from src.live_draft import is_user_pick, load_board
    from src.particle_bank import (
        build_offturn_bank,
        conditioned_orders_for_fast,
        default_bank_path,
        orders_for_deep_refresh,
        refresh_bank_from_deep,
    )

    state = DraftState.load(args.state)
    board = load_board(args.board)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    engine = getattr(args, "engine", "fast")
    seed = int(model.get("live_draft", {}).get("random_seed", 20260830) if args.seed is None else args.seed)
    bank_path = default_bank_path(args.state)

    if is_user_pick(state):
        rcfg = model.get("full_rollout", {})
        simulations = int(args.simulations or (
            rcfg.get("fast_simulations", 40) if engine == "fast"
            else rcfg.get("deep_simulations", 30)
        ))
        candidates = int(args.candidates or rcfg.get("candidate_limit", 10))
        if engine == "fast":
            orders, status, fresh_fraction = conditioned_orders_for_fast(
                bank_path, board, state, league, model, simulations, seed
            )
            info = status.to_dict()
            info["fresh_fraction"] = fresh_fraction
            result = evaluate_candidates_fast(
                board, state, league, model,
                simulations=simulations,
                seed=seed,
                candidate_limit=candidates,
                market_order_ids=orders,
                bank_info=info if orders is not None else None,
            )
        else:
            orders, prior_status, reused_fraction = orders_for_deep_refresh(
                bank_path, board, state, league, model, simulations, seed
            )
            result, used = evaluate_candidates_full_rollout(
                board, state, league, model,
                simulations=simulations,
                seed=seed,
                candidate_limit=candidates,
                deep=True,
                market_order_ids=orders,
                return_scenarios=True,
            )
            status = refresh_bank_from_deep(
                bank_path, board, state, league, model,
                used, result.to_dict("records"), seed, reused_fraction,
            )
            print(
                f"DEEP bank refreshed: {status.particles} particles, "
                f"ESS {status.ess:.1f}; reused scenario fraction {reused_fraction:.0%}"
            )
        print(f"Mode: current-pick full-roster recommendation at {state.next_overall}")
    else:
        if engine == "fast":
            result = forecast_next_user_pick_fast(
                board, state, league, model,
                simulations=args.simulations or 6000,
                seed=seed,
                candidate_limit=args.candidates or 16,
            )
        else:
            result = forecast_next_user_pick_deep(
                board, state, league, model,
                simulations=args.simulations or 300,
                seed=seed,
                candidate_limit=args.candidates or 16,
            )
            status = build_offturn_bank(
                bank_path, board, state, league, model, seed,
                source="DEEP-FORECAST",
            )
            print(
                f"DEEP bank re-anchored: {status.particles} particles, "
                f"ESS {status.ess:.1f}"
            )
        target = int(result.iloc[0]["target_pick"]) if len(result) else None
        print(f"Mode: next-user-pick forecast from {state.next_overall} to {target}")

    if len(result) == 0:
        print("No recommendation/forecast rows.")
        return

    if result.iloc[0].get("analysis_mode") == "forecast":
        cols = [
            "name", "position", "nfl_team", "espn_adp", "tier",
            "target_value_estimate", "p_available_target",
            "p_best_target", "forecast_score", "engine",
        ]
    else:
        cols = [
            "name", "position", "nfl_team", "espn_adp", "tier",
            "immediate_draft_value", "final_roster_utility_mean",
            "final_roster_utility_sd", "final_starter_value_mean",
            "final_bench_value_mean", "expected_final_QB",
            "expected_final_RB", "expected_final_WR", "expected_final_TE",
            "mc_objective", "engine",
        ]
    cols = [c for c in cols if c in result.columns]
    print(result[cols].head(args.limit).to_string(index=False))


def cmd_import_mock(args):
    from src.mock_calibration import save_mock_draft
    csv_path, summary_path = save_mock_draft(
        args.file, args.out, num_teams=int(args.teams)
    )
    print(f"Mock draft CSV: {csv_path}")
    print(f"Mock summary:   {summary_path}")


def cmd_mock_status(args):
    from src.mock_calibration import calibration_inventory
    info = calibration_inventory(args.dir)
    print(f'Complete mock drafts: {info["draft_count"]}')
    for d in info["drafts"]:
        print(f'  {d["file"]}: {d["picks"]} picks, {d["rounds"]} rounds')

def cmd_bank_status(args):
    from src.live_draft import load_board
    from src.particle_bank import bank_status, default_bank_path
    state = DraftState.load(args.state)
    board = load_board(args.board)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    path = default_bank_path(args.state)
    status = bank_status(path, board, state, league, model)
    print(f"Bank path: {path}")
    if not status.exists:
        print("No DEEP bank exists yet. Run DEEP first.")
        return
    print(f"Valid: {status.valid}")
    print(f"Source: {status.source}")
    print(f"Anchor pick: {status.anchor_pick}")
    print(f"Conditioned through: {status.conditioned_through}")
    print(f"Particles: {status.particles}")
    print(f"ESS: {status.ess:.1f} ({100*status.ess_fraction:.1f}%)")
    print(f"Observed opponent picks: {status.observed_opponent_picks}")
    print(f"Degraded: {status.degraded}")
    if status.selected_branch_name:
        print(f"Chosen anchor branch: {status.selected_branch_name}")
    print(status.message)



def _configured_user_team(league_path: str | Path) -> str | None:
    try:
        league = load_league(league_path)
    except Exception:
        return None
    value = league.get("user_team_name")
    return str(value) if value else None


def cmd_season_sync(args):
    from src.season_snapshot import sync_season_snapshot

    snapshot, path = sync_season_snapshot(
        secrets_path=args.secrets,
        out_root=args.out,
        week=args.week,
        include_sleeper=not args.skip_sleeper,
        include_nfl=not args.skip_nfl,
    )
    espn = snapshot["espn"]
    print("ESPN authentication: OK")
    print(f'League: {espn.get("league_name") or espn.get("league_id")}')
    print(f'Season/week: {espn.get("season")}/{espn.get("week")}')
    print(f'Teams: {len(espn.get("teams") or [])}')
    print(f'Available players: {len(espn.get("available_players") or [])}')
    sleeper = snapshot.get("source_status", {}).get("sleeper")
    if sleeper:
        print(f'Sleeper: {"OK" if sleeper.get("ok") else "FAILED"}')
        if sleeper.get("error"):
            print(f'  {sleeper["error"]}')
    nflverse_rosters = snapshot.get("source_status", {}).get("nflverse_rosters")
    if nflverse_rosters:
        print(f'nflverse rosters: {"OK" if nflverse_rosters.get("ok") else "FAILED"}')
        if nflverse_rosters.get("ok"):
            print(
                f'  rows={nflverse_rosters.get("rows", 0)} espn_ids={nflverse_rosters.get("matched_espn_ids", 0)} '
                f'fantasy_matches={nflverse_rosters.get("fantasy_player_matches", 0)}'
            )
        elif nflverse_rosters.get("error"):
            print(f'  {nflverse_rosters["error"]}')
    matchups = snapshot.get("source_status", {}).get("nflverse_matchups")
    if matchups:
        print(f'nflverse matchups: {"OK" if matchups.get("ok") else "FAILED"}')
        if matchups.get("ok"):
            current_note = f' current_pbp_rows={matchups.get("current_pbp_rows", 0)}'
            print(
                f'  prior={matchups.get("prior_season")} defenses={matchups.get("defense_profiles", 0)} '
                f'offenses={matchups.get("offense_profiles", 0)} scheduled_teams={matchups.get("scheduled_teams", 0)}'
                + current_note
            )
            if matchups.get("current_pbp_error"):
                print(f'  current PBP fallback: {matchups.get("current_pbp_error")}')
        elif matchups.get("error"):
            print(f'  {matchups["error"]}')
    nfl_rosters = snapshot.get("source_status", {}).get("nfl_official_rosters")
    if nfl_rosters:
        print(f'NFL.com team rosters: {"OK" if nfl_rosters.get("complete") else ("PARTIAL" if nfl_rosters.get("ok") else "FAILED")}')
        if nfl_rosters.get("ok"):
            print(
                f'  pages={nfl_rosters.get("fetches_ok", 0)}/{nfl_rosters.get("fetches_total", 0)} '
                f'parsed={nfl_rosters.get("parsed_teams", 0)} rows={nfl_rosters.get("rows", 0)} '
                f'matched={nfl_rosters.get("fantasy_player_matches", 0)}'
            )
        elif nfl_rosters.get("error"):
            print(f'  {nfl_rosters["error"]}')
    nfl = snapshot.get("source_status", {}).get("nfl_official")
    if nfl:
        tx_ok = int(nfl.get("transaction_category_fetches_ok") or 0)
        tx_total = int(nfl.get("transaction_category_fetches_total") or 0)
        injury_ok = bool(nfl.get("injury_page_ok"))
        if nfl.get("ok") and tx_ok == tx_total and injury_ok:
            nfl_label = "OK"
        elif nfl.get("ok"):
            nfl_label = "PARTIAL"
        else:
            nfl_label = "FAILED"
        print(f'NFL.com: {nfl_label}')
        print(
            f'  transaction pages={tx_ok}/{tx_total} rows={nfl.get("transactions", 0)}; '
            f'injury_page={"OK" if injury_ok else "FAILED"} rows={nfl.get("injury_rows", 0)} '
            f'matched={nfl.get("injury_player_matches", 0)}'
        )
    print(f'Snapshot: {path}')
    print(f'Latest: {Path(args.out) / "latest.json"}')


def cmd_season_status(args):
    from src.weekly_manager import availability_status, find_week_opponent, load_snapshot, resolve_team

    snapshot = load_snapshot(args.snapshot)
    espn = snapshot.get("espn", snapshot)
    team_name = args.team or _configured_user_team(args.league)
    team = resolve_team(snapshot, team_name=team_name, team_id=args.team_id)
    opponent_id = find_week_opponent(snapshot, int(team["team_id"]))
    opponent = next((t for t in espn.get("teams", []) if t.get("team_id") == opponent_id), None)

    print(f'League: {espn.get("league_name")}')
    print(f'Week: {espn.get("week")}')
    print(f'Team: {team.get("name")} (id={team.get("team_id")})')
    if opponent:
        print(f'Opponent: {opponent.get("name")} (id={opponent_id})')
    print(f'Waiver rank: {team.get("waiver_rank")}')
    print(f'Acquisitions/drops/trades: {team.get("acquisitions")}/{team.get("drops")}/{team.get("trades")}')
    print("\nRoster:")
    for p in team.get("roster") or []:
        q = p.get("weekly_projection")
        qtxt = f"{float(q):.2f}" if q is not None else "-"
        injury, injury_source = availability_status(p)
        official_practice = p.get("official_practice") or {}
        if isinstance(official_practice, dict) and official_practice:
            practice = "/".join(str(v) for v in official_practice.values() if v) or "-"
        else:
            practice_raw = p.get("sleeper_practice_participation")
            practice = "-" if practice_raw is None or str(practice_raw).casefold() == "nan" else str(practice_raw)
        roster_state = str(p.get("nflverse_roster_status") or "-")
        print(
            f'{str(p.get("lineup_slot") or "?"):>6}  '
            f'{str(p.get("position") or "?"):>3}  '
            f'{str(p.get("name") or "?"):<28} '
            f'proj={qtxt:>6}  status={injury:<12} source={injury_source:<17} '
            f'nfl={roster_state:<4} practice={practice}'
        )


def _print_lineup(title, lineup):
    print(f"\n=== {title} ===")
    for row in lineup.rows:
        print(
            f'{row.get("display_slot") or row.get("assigned_slot", "?"):>4}  '
            f'{str(row.get("name") or "?"):<28} '
            f'{str(row.get("position") or "?"):>3}  '
            f'proj={float(row.get("projection_points") or 0):5.2f}  '
            f'P(active)={float(row.get("active_probability") or 0):5.1%}  '
            f'exp={float(row.get("expected_points") or 0):5.2f}  '
            f'{row.get("availability_status") or row.get("injury_status") or "ACTIVE"}'
            f'[{row.get("availability_status_source") or "?"}]'
        )
    print(f'Projection total: {lineup.total_projection:.2f}')
    print(f'Availability-weighted total: {lineup.total_expected:.2f}')
    if lineup.missing_slots:
        print('Missing slots: ' + ', '.join(lineup.missing_slots))


def cmd_week_lineup(args):
    from src.transaction_manager import enrich_season_values
    from src.weekly_manager import (
        active_probability,
        build_lineup_scenarios,
        lineup_data_quality,
        load_snapshot,
        resolve_team,
    )
    from src.weekly_yield import build_weekly_yield_state

    snapshot = load_snapshot(args.snapshot)
    team_name = args.team or _configured_user_team(args.league)
    team = resolve_team(snapshot, team_name=team_name, team_id=args.team_id)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    week = int(snapshot.get("espn", snapshot).get("week") or 1)
    roster = enrich_season_values(team.get("roster") or [], args.values, league, week)
    warnings = lineup_data_quality(roster)
    matchup_context = snapshot.get("matchup_context") or {}
    for player in roster:
        state = build_weekly_yield_state(
            player,
            week=week,
            current_week=week,
            model=model,
            availability_probability=active_probability(player, model),
            matchup_context=matchup_context,
            league=league,
        )
        player["pre_v023_projection_points"] = player.get("projection_points")
        player["projection_points"] = state.operational_mean_ppg
        player["projection_source"] = f"V028_OPERATIONAL:{state.kinematic_factor_source}:{state.interaction_factor_source}"
        player["kinematic_factor_mean"] = state.kinematic_factor_mean
        player["matchup_opponent"] = state.matchup_opponent
    scenarios = build_lineup_scenarios(roster, league, model)

    print(f'Week {week} lineup: {team.get("name")}')
    print('Lineup projections use the v0.28 operational yield (base MC/K + ESPN anchor + precomputed Data/MC interaction-grid correction).')
    if scenarios["contingencies"]:
        _print_lineup("NOMINAL LINEUP IF QUESTIONABLE/DOUBTFUL PLAY", scenarios["all_uncertain_active"])
        _print_lineup("PLANNING EXPECTED-VALUE LINEUP (PROVISIONAL AVAILABILITY WEIGHTS)", scenarios["expected"])
        print("\n=== ONE-PLAYER INACTIVE CONTINGENCIES ===")
        for item in scenarios["contingencies"]:
            lineup = item["if_inactive"]
            names = ', '.join(f'{r.get("display_slot") or r.get("assigned_slot")}={r.get("name")}' for r in lineup.rows)
            print(f'{item["player"]} OUT -> total {lineup.total_projection:.2f}: {names}')
    else:
        _print_lineup("CURRENT LINEUP", scenarios["expected"])
        print("\nNo QUESTIONABLE/DOUBTFUL roster players in the current status snapshot.")

    if warnings:
        print("\n=== DATA-QUALITY FLAGS ===")
        for warning in warnings:
            print(f"- {warning}")
    print("\nAvailability probabilities remain provisional until live official practice/game-status observations are present and calibrated.")

def cmd_week_yields(args):
    from src.transaction_manager import enrich_season_values
    from src.weekly_manager import active_probability, load_snapshot, resolve_team
    from src.weekly_yield import build_weekly_yield_state

    snapshot = load_snapshot(args.snapshot)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    team_name = args.team or _configured_user_team(args.league)
    team = resolve_team(snapshot, team_name=team_name, team_id=args.team_id)
    week = int(snapshot.get("espn", snapshot).get("week") or 1)
    roster = enrich_season_values(team.get("roster") or [], args.values, league, week)
    matchup_context = snapshot.get("matchup_context") or {}

    print(f'Week {week} predictive yields: {team.get("name")}')
    print('ESPN is an external anchor; K is the v0.23 base matchup term and I is the separately fitted v0.28 Data/MC interaction-grid correction.')
    for player in roster:
        state = build_weekly_yield_state(
            player,
            week=week,
            current_week=week,
            model=model,
            availability_probability=active_probability(player, model),
            matchup_context=matchup_context,
            league=league,
        )
        anchor = '-'
        if state.espn_anchor_ppg is not None:
            ztxt = f' z={state.espn_anchor_z:+.2f}' if state.espn_anchor_z is not None else ''
            anchor = f'{state.espn_anchor_ppg:.2f} {state.espn_anchor_kind}{ztxt}'
        model_txt = f'{state.model_mean_ppg:.2f}' if state.model_mean_ppg is not None else '-'
        kin_model = f'{state.matchup_model_mean_ppg:.2f}' if state.matchup_model_mean_ppg is not None else '-'
        opp = state.matchup_opponent or '-'
        site = 'H' if state.matchup_home is True else ('A' if state.matchup_home is False else '-')
        print(
            f'{state.position:>3} {state.name:<28} '
            f'base={state.pre_matchup_operational_mean_ppg:5.2f} K={state.kinematic_factor_mean:5.3f} I={state.interaction_factor_mean:5.3f} dI={state.interaction_delta_ppg:+5.2f} '
            f'kin-model={kin_model:>5} op={state.operational_mean_ppg:5.2f} '
            f'ESPN={anchor:<28} opp={opp:<3} {site} '
            f'sd(game/model/K/I/total)={state.game_sd_ppg:4.2f}/{state.model_sd_ppg:4.2f}/{state.kinematic_sd_ppg:4.2f}/{state.interaction_sd_ppg:4.2f}/{state.predictive_sd_ppg:4.2f} '
            f'P(active)={state.availability_probability:5.1%}'
        )
        if state.position == "DST" and state.dst_component_expectation:
            d = state.dst_component_expectation
            print(
                f'    DST components vs {opp}: sacks={d.get("sacks_mean",0):.2f} TO={d.get("turnovers_mean",0):.2f} '
                f'PA={d.get("points_allowed_mean",0):.1f} YA={d.get("yards_allowed_mean",0):.0f} '
                f'raw_component_E={d.get("component_expected_fantasy",0):.2f}'
            )




def _print_action_rows(title, rows, limit, show_negative=False):
    print(f"\n=== {title} ===")
    shown = 0
    for row in rows:
        if not show_negative and float(row.get("delta_utility") or 0.0) <= 0.0:
            continue
        shown += 1
        if shown > limit:
            break
        status = str(row.get("fantasy_status") or "")
        ptxt = f' P(acquire)={float(row.get("p_acquire") or 0):5.1%}' if status == "WAIVERS" else ""
        trend = row.get("sleeper_adds_24h")
        trend_txt = f' adds24h={trend}' if trend is not None else ""
        lines = [
            f'{shown:>2}. ADD {row.get("add_name")} ({row.get("add_position")}, {row.get("add_team") or "FA"}) '
            f'/ DROP {row.get("drop_name")} ({row.get("drop_position")})',
            (
                f'    direct paired H2H Δ={100*float(row.get("delta_expected_h2h_win_probability") or 0):+6.3f} pp  '
                f'68% mean-CI=[{100*float(row.get("delta_h2h_p16") or 0):+6.3f}, '
                f'{100*float(row.get("delta_h2h_p84") or 0):+6.3f}]  '
                f'Pdirect(+/0/-)={float(row.get("p_raw_h2h_better_if_acquired") or 0):5.1%}/'
                f'{float(row.get("p_raw_h2h_tie_if_acquired") or 0):5.1%}/'
                f'{float(row.get("p_raw_h2h_worse_if_acquired") or 0):5.1%}  '
                f'direct={row.get("raw_action_classification") or "UNASSESSED"}'
            ),
            (
                f'    league-state paired utility Δ={100*float(row.get("delta_utility") or 0):+6.3f} pp  '
                f'68% mean-CI=[{100*float(row.get("delta_total_utility_p16") or 0):+6.3f}, '
                f'{100*float(row.get("delta_total_utility_p84") or 0):+6.3f}]  '
                f'Pleague(+/0/-)={float(row.get("p_utility_better_if_acquired") or 0):5.1%}/'
                f'{float(row.get("p_utility_tie_if_acquired") or 0):5.1%}/'
                f'{float(row.get("p_utility_worse_if_acquired") or 0):5.1%}  '
                f'{row.get("action_classification") or "UNASSESSED"}'
            ),
            (
                f'    action EVΔ={100*float(row.get("expected_delta_utility") or 0):+6.3f} pp  '
                f'WeekΔ={float(row.get("delta_current_week_points") or 0):+5.2f}  '
                f'SeasonPPGΔ={float(row.get("delta_season_lineup_ppg") or 0):+5.2f}  '
                f'InsuranceΔ={float(row.get("delta_bench_insurance_ppg") or 0):+5.2f}  '
                f'ByeFloorΔ={float(row.get("delta_bye_floor_points") or 0):+5.2f}{ptxt}{trend_txt}'
            ),
            (
                f'    release response: P(claimed)={float(row.get("release_p_claimed") or 0):5.1%}  '
                f'E[recipient gain]={float(row.get("release_expected_recipient_gain_ppg") or 0):+5.2f} ppg  '
                f'field shift={float(row.get("release_field_shift_ppg") or 0):+5.2f} ppg  '
                f'[order1={float(row.get("release_first_order_field_shift_ppg") or 0):+5.2f}, '
                f'order2+={float(row.get("release_higher_order_field_shift_ppg") or 0):+5.2f}]  '
                f'current-opp shift={float(row.get("release_current_opponent_shift_ppg") or 0):+5.2f} ppg  '
                f'N1={int(row.get("release_response_scenarios") or 0)} N2+={int(row.get("release_higher_order_scenarios") or 0)}'
            ),
            (
                f'    contingent diagnostic only: OptionDepthΔ={float(row.get("delta_future_option_ppg") or 0):+5.2f} ppg  '
                f'StressDepthΔ={float(row.get("delta_replacement_scarcity_ppg") or 0):+5.2f} ppg  '
                f'candidate_support={float(row.get("candidate_option_support") or 0):.2f}'
            ),
        ]
        model_mean = row.get("candidate_model_mean_ppg")
        espn_anchor = row.get("candidate_espn_anchor_ppg")
        op_mean = row.get("candidate_operational_mean_ppg")
        anchor_txt = ""
        if espn_anchor is not None:
            z = row.get("candidate_espn_anchor_z")
            ztxt = f' z={float(z):+.2f}' if z is not None else ""
            anchor_txt = (
                f'  ESPN={float(espn_anchor):.2f} [{row.get("candidate_espn_anchor_kind")}]'
                f' Δ(model-ESPN)={float(row.get("candidate_delta_model_minus_espn") or 0):+.2f}{ztxt}'
            )
        lines.append(
            f'    yield: operational={float(op_mean or 0):.2f}  '
            f'model={float(model_mean or 0):.2f}{anchor_txt}'
        )
        lines.append(
            f'    matchup: K={float(row.get("candidate_kinematic_factor") or 1.0):.3f} '
            f'opp={row.get("candidate_matchup_opponent") or "-"} '
            f'[{row.get("candidate_kinematic_source") or "UNKNOWN"}] '
            f'sdK={float(row.get("candidate_kinematic_sd_ppg") or 0):.2f}'
        )
        proj_source = str(row.get("candidate_projection_source") or "UNKNOWN")
        season_source = str(row.get("candidate_season_ppg_source") or "UNKNOWN")
        stop_txt = " FUTILITY_STOP" if row.get("mc_futility_stop") else ""
        lines.append(
            f'    source: week={float(row.get("candidate_projection_points") or 0):.2f} '
            f'[{proj_source}]  season={float(row.get("candidate_season_ppg") or 0):.2f}/wk '
            f'[{season_source}]  MC={int(row.get("mc_scenarios") or 0)} '
            f'stage={row.get("mc_stage") or "FINAL"}{stop_txt}'
        )
        destinations = row.get("release_top_destinations") or []
        if destinations:
            summary = "; ".join(
                f"#{d.get('waiver_rank') or '-'} {d.get('team_name')} Pwin={float(d.get('winner_probability') or 0):.0%} Δ={float(d.get('delta_season_ppg') or 0):+.2f} drop={d.get('best_drop_name') or '-'}"
                for d in destinations[:3]
            )
            lines.append(f'    release destinations: {summary}')
        blockers = row.get("waiver_blockers") or []
        if blockers:
            summary = "; ".join(
                f"#{b.get('waiver_rank')} {b.get('team_name')} P={float(b.get('claim_probability') or 0):.0%} Δ={float(b.get('delta_season_ppg') or 0):+.2f} drop={b.get('best_drop_name') or '-'}"
                for b in blockers[:5]
            )
            lines.append(f'    blockers: {summary}')
        # Print each action as one atomic block.  This prevents progress/output capture
        # layers from separating a numbered action header from the diagnostics beneath it.
        print("\n".join(lines), flush=True)
    if shown == 0:
        print(f"No positive modeled actions in this {title.lower()} section of the final frontier.")


def cmd_roster_actions(args):
    from src.transaction_manager import evaluate_actions, save_action_report, save_prediction_report
    from src.weekly_manager import load_snapshot

    snapshot = load_snapshot(args.snapshot)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    team_name = args.team or _configured_user_team(args.league)

    started = time.monotonic()
    last_print = [0.0]
    last_phase = [None]

    def progress(done: int, total: int, phase: str) -> None:
        now = time.monotonic()
        total_i = max(1, int(total))
        done_i = max(0, min(int(done), total_i))
        frac = done_i / total_i
        important = (
            phase.startswith("context ready")
            or phase.startswith("broad action screen")
            or phase.startswith("waiver manager model")
            or phase.startswith("paired action MC queued")
            or phase.startswith("hierarchical MC")
            or phase.startswith("final waiver manager model")
            or phase == "roster-actions complete"
        )
        finished = done_i >= total_i
        # Keep PowerShell readable: print at most about once/second during deep MC,
        # plus phase completions and the cheap screening/waiver stages.
        if not (important or finished or now - last_print[0] >= 1.0):
            return
        elapsed = int(now - started)
        hh, rem = divmod(elapsed, 3600)
        mm, ss = divmod(rem, 60)
        elapsed_text = f"{hh:02d}:{mm:02d}:{ss:02d}" if hh else f"{mm:02d}:{ss:02d}"
        print(
            f"[roster-actions {elapsed_text}] {100.0*frac:6.2f}%  {phase}",
            flush=True,
        )
        last_print[0] = now
        last_phase[0] = phase

    report = evaluate_actions(
        snapshot, league, model,
        values_path=args.values,
        team_name=team_name,
        team_id=args.team_id,
        position=args.position,
        predictive_mc_scenarios=args.mc,
        progress_callback=progress,
    )
    baseline = report["baseline"]
    print(f'Week {report.get("week")} PLAYER channel actions: {report.get("team_name")}')
    print(f'Waiver rank: {report.get("waiver_rank")}')
    print(f'Evaluated: {report.get("candidate_pool_evaluated")} QB/RB/WR/TE candidates x {report.get("legal_drop_players")} player-channel legal drops')
    stages = report.get("predictive_mc_stages") or [report.get("predictive_mc_scenarios")]
    requested_stages = report.get("predictive_mc_requested_stages") or stages
    stage_txt = " -> ".join(f"{int(x):,}" for x in stages)
    requested_txt = " -> ".join(f"{int(x):,}" for x in requested_stages)
    final_stage_actions = int(report.get("predictive_actions_final_stage") or 0)
    parked_actions = int(report.get("predictive_actions_futility_parked") or 0)
    if report.get("predictive_mc_stopped_for_futility"):
        print(
            f'Predictive MC: requested hierarchical {requested_txt}; stopped after {stage_txt} by league-state classification futility; '
            f'{report.get("predictive_actions_initial_frontier")} initial -> {report.get("predictive_actions_evaluated")} reported actions '
            f'({parked_actions} futility-stopped)'
        )
    else:
        print(
            f'Predictive MC: hierarchical {stage_txt}; {report.get("predictive_actions_initial_frontier")} initial -> '
            f'{report.get("predictive_actions_evaluated")} reported actions '
            f'({final_stage_actions} final-stage, {parked_actions} futility-stopped)'
        )
    excluded = int(report.get("available_players_excluded") or 0)
    if excluded:
        total = int(report.get("available_players_total") or 0)
        eligible = int(report.get("available_players_nfl_eligible") or 0)
        print(f'NFL-roster filter: {eligible}/{total} available players eligible; {excluded} non-active/stale/unknown excluded')
        examples = report.get("excluded_available_examples") or []
        if examples:
            text = ", ".join(
                f'{x.get("name")} [{x.get("reason")}]'
                for x in examples[:8] if x.get("name")
            )
            if text:
                print(f'Excluded examples: {text}')
        unknown_statuses = report.get("official_unknown_status_counts") or {}
        if unknown_statuses:
            summary = ", ".join(f"{code}={count}" for code, count in unknown_statuses.items())
            print(f'Unknown NFL.com roster codes (fail-safe excluded): {summary}')
    print("\n=== HOLD BASELINE ===")
    print(f'HOLD predictive MC:       N={int(report.get("predictive_mc_scenarios") or 0):,}')
    print(f'Expected H2H utility:      {100*float(baseline["expected_h2h_win_probability"]):.2f}%')
    print(f'Current-week expected:     {float(baseline["current_week_expected_points"]):.2f} ± {float(baseline.get("current_week_sd_points") or 0):.2f} pts')
    print(f'Current-week nominal:      {float(baseline["current_week_nominal_points"]):.2f} pts')
    print(f'Remaining-season lineup:   {float(baseline["season_expected_lineup_ppg"]):.2f} pts/week')
    print(f'Bench insurance:           {float(baseline["bench_insurance_ppg"]):.2f} pts/week above replacement')
    opt = report.get("baseline_option_scarcity") or {}
    print(
        f'Contingent diagnostic:    {float(opt.get("future_option_ppg") or 0):.2f} ppg-equivalent '
        f'(N={int(opt.get("contingent_scenarios") or 0)})'
    )
    print(f'Stress diagnostic:        {float(opt.get("replacement_scarcity_ppg") or 0):.2f} ppg-equivalent')
    print(f'Deterministic bye floor:   {float(baseline["bye_floor_points"]):.2f} pts')

    _print_action_rows("IMMEDIATE FREE-AGENT ACTIONS", report["free_agent_actions"], args.limit, args.show_negative)
    _print_action_rows("WAIVER CLAIM ACTIONS (PROVISIONAL ACQUISITION MODEL)", report["waiver_actions"], args.limit, args.show_negative)
    path = save_action_report(report, args.out)
    pred_path = save_prediction_report(report.get("prediction_snapshot") or {}, args.prediction_out)
    print(f"\nDecision audit: {path}")
    print(f"Prediction audit: {pred_path}")
    all_actions = report["free_agent_actions"] + report["waiver_actions"]
    resolved = [r for r in all_actions if r.get("action_classification") == "ACTIONABLE_EDGE" and float(r.get("expected_delta_utility") or 0) > 0]
    possible = [r for r in all_actions if r.get("action_classification") == "POSSIBLE_EDGE" and float(r.get("expected_delta_utility") or 0) > 0]
    if resolved:
        print("Recommendation: at least one ACTIONABLE_EDGE is supported by the paired counterfactual PLAYER-channel MC; review the ranked action and acquisition layer.")
    elif possible:
        print("Recommendation: HOLD for now — possible player-channel edges exist, but no ACTIONABLE_EDGE is resolved.")
    else:
        print("Recommendation: HOLD — no positive counterfactual player-channel edge is resolved.")
    print("Waiver P(acquire) remains a separate provisional behavior model. K/DST are intentionally excluded; use defense-channel and kicker-channel for specialist management.")



def _parse_id_list(value: str) -> list[int]:
    out = [int(x.strip()) for x in str(value).split(",") if x.strip()]
    if not out:
        raise ValueError("at least one ESPN player id is required")
    return out


def _trade_player_names(rows):
    return ", ".join(str(r.get("name") or r.get("espn_id")) for r in rows)


def _print_specialist_channel(report: dict, *, limit: int = 8) -> None:
    channel = str(report.get("channel") or "SPECIALIST")
    baseline = report.get("baseline") or {}
    owned = report.get("owned") or []
    owned_txt = ", ".join(f"{x.get('name')} ({x.get('team') or '-'})" for x in owned) or "none"
    print(f"Week {report.get('week')} {channel.lower()} channel: {report.get('team_name')}")
    print(f"Owned {report.get('position')}: {owned_txt}")
    print(f"Channel MC: N={int(report.get('mc_scenarios') or 0):,}")
    print(
        f"Static baseline: {float(baseline.get('weighted_mean_ppg') or 0):.2f} weighted pts/week | "
        f"current {float(baseline.get('current_week_mean') or 0):.2f} +/- {float(baseline.get('current_week_sd') or 0):.2f} | "
        f"start {baseline.get('current_week_choice') or '-'}"
    )

    print("\n=== SAME-CHANNEL STATIC SWAPS ===")
    print("L1 diagnostic board; dynamic policy results follow below.")
    swaps = report.get("swap_actions") or []
    if not swaps:
        print("No same-channel static alternatives found.")
    for shown, row in enumerate(swaps[: max(0, int(limit))], start=1):
        drop = f" / DROP {row.get('drop_name')}" if row.get('drop_name') else ""
        lines = [
            f" {shown}. {row.get('action')} {row.get('add_name')} ({row.get('add_team') or '-'}){drop} [{row.get('fantasy_status')}]",
            (
                f"    static channel delta={float(row.get('delta_channel_ppg') or 0):+.3f} pts/week | "
                f"P(channel better)={100*float(row.get('p_channel_better') or 0):.1f}% | "
                f"current-week delta={float(row.get('current_week_delta') or 0):+.2f} | {row.get('classification')}"
            ),
        ]
        print("\n".join(lines), flush=True)

    policy = report.get("one_slot_policy") or {}
    if policy:
        print("\n=== L2 DYNAMIC ONE-SLOT POLICY ===")
        proposal = policy.get("proposal_current_action") or policy.get("current_action") or {"action": "HOLD"}
        recommended = policy.get("recommended_current_action") or {"action": "HOLD"}
        def action_text(action):
            text = str(action.get("action") or "HOLD")
            if action.get("add"):
                text += f" {action.get('add')}"
            if action.get("drop"):
                text += f" / DROP {action.get('drop')}"
            return text
        complete = policy.get("complete_state_delta") or {}
        print(
            f" dynamic policy={float(policy.get('weighted_mean_ppg') or 0):.3f} pts/week | "
            f"delta vs static={float(policy.get('delta_vs_static_ppg') or 0):+.3f}"
        )
        print(f" policy proposal={action_text(proposal)} | current recommendation={action_text(recommended)}")
        print(
            f" complete-state delta={100*float(complete.get('mean') or 0):+.3f} pp | "
            f"68% mean-CI=[{100*float(complete.get('mean_p16') or 0):+.3f}, {100*float(complete.get('mean_p84') or 0):+.3f}] | "
            f"P(+/0/-)={100*float(complete.get('p_better') or 0):.1f}%/"
            f"{100*float(complete.get('p_tie') or 0):.1f}%/{100*float(complete.get('p_worse') or 0):.1f}% | "
            f"{complete.get('classification') or 'UNASSESSED'}"
        )
        print(
            f" market={policy.get('market_model') or '-'} | order={policy.get('transaction_order_model') or '-'} | "
            f"initial guaranteed FA={int(policy.get('guaranteed_free_agents_initial') or 0)} | "
            f"current waivers excluded={int(policy.get('excluded_current_waivers') or 0)}"
        )
        plans = policy.get("weekly_plan") or []
        preview = []
        for row in plans[:6]:
            tx = row.get("transaction") or {}
            move = str(tx.get("action") or "HOLD")
            preview.append(
                f"W{row.get('week')} {row.get('starter_name') or '-'} {float(row.get('expected_points') or 0):.1f} "
                f"vs {row.get('opponent') or '-'} [{move}]"
            )
        if preview:
            print("    " + "; ".join(preview))

    carry = report.get("dynamic_carry_actions") or []
    if carry:
        print("\n=== L3/L4 DYNAMIC SECOND-DST ACTIVATION + TEMPORAL COMPLETE-STATE CONFIRMATION ===")
        print(f" current second-slot recommendation={report.get('carry2_current_recommendation') or 'HOLD_ONE_DST_NOW'}")
        for shown, row in enumerate(carry[: max(0, int(limit))], start=1):
            rel = row.get("player_slot_release") or {}
            full = row.get("complete_state_delta") or {}
            when = "CURRENT" if row.get("current_activation") else "FUTURE"
            release_week = row.get("effective_player_release_week")
            lines = [
                (
                    f" {shown}. ACTIVATE2 W{int(row.get('activation_week') or 0)} [{when}] -> "
                    f"ADD {row.get('add_name') or '-'} ({row.get('add_team') or '-'}) | "
                    f"D2-D1 dynamic channel={float(row.get('dynamic_channel_delta_ppg') or 0):+.3f} pts/week | "
                    f"{row.get('classification') or 'UNASSESSED'}"
                ),
            ]
            if release_week is None:
                lines.append(
                    f"    one-slot={float(row.get('one_slot_policy_ppg') or 0):.3f} | "
                    f"two-slot={float(row.get('two_slot_policy_ppg') or 0):.3f} | "
                    "player release: none (second D/ST not acquired)"
                )
            else:
                lines.append(
                    f"    one-slot={float(row.get('one_slot_policy_ppg') or 0):.3f} | "
                    f"two-slot={float(row.get('two_slot_policy_ppg') or 0):.3f} | "
                    f"player release begins W{int(release_week)}: "
                    f"{rel.get('name') or '-'} ({rel.get('position') or '-'}) "
                    f"[dominant={100*float(rel.get('selection_probability') or 0):.1f}%]"
                )
                distribution = rel.get("selection_distribution") or []
                if len(distribution) > 1:
                    preview = []
                    for item in distribution[:3]:
                        preview.append(
                            f"{item.get('name') or item.get('espn_id') or '-'} "
                            f"{100*float(item.get('selection_probability') or 0):.1f}%"
                        )
                    lines.append("    release-state distribution: " + "; ".join(preview))
                player_state = row.get("player_state_at_release") or {}
                player_path = row.get("player_state_path") or []
                prior_moves = [s.get("transaction") for s in player_path if (s or {}).get("transaction")]
                lines.append(
                    f"    player state: {row.get('player_membership_model') or '-'} | "
                    f"modeled prior swaps={len(prior_moves)} | "
                    f"external market={row.get('external_player_market_model') or '-'}"
                )
                if prior_moves:
                    last = prior_moves[-1] or {}
                    confirm = str(last.get("predictive_classification") or "UNASSESSED")
                    lines.append(
                        f"    latest player-state move: W{int(last.get('week') or 0)} "
                        f"ADD {last.get('add') or '-'} / DROP {last.get('drop') or '-'} | "
                        f"confirm={confirm} N={int(last.get('predictive_scenarios') or 0)} "
                        f"delta={100*float(last.get('predictive_direct_h2h_delta_mean') or 0):+.3f} pp "
                        f"Pbetter={100*float(last.get('predictive_p_better') or 0):.1f}%"
                    )
            if row.get("complete_state_confirmed"):
                lines.append(
                    f"    complete-state delta={100*float(full.get('mean') or 0):+.3f} pp | "
                    f"68% mean-CI=[{100*float(full.get('mean_p16') or 0):+.3f}, {100*float(full.get('mean_p84') or 0):+.3f}] | "
                    f"P(+/0/-)={100*float(full.get('p_better') or 0):.1f}%/"
                    f"{100*float(full.get('p_tie') or 0):.1f}%/{100*float(full.get('p_worse') or 0):.1f}%"
                )
                release = row.get("release_response") or {}
                lines.append(
                    f"    released-player response: P(claimed)={100*float(release.get('p_claimed') or 0):.1f}% | "
                    f"field shift={float(release.get('field_shift_ppg') or 0):+.3f} ppg "
                    f"[order1={float(release.get('first_order_field_shift_ppg') or release.get('field_shift_ppg') or 0):+.3f}, "
                    f"order2+={float(release.get('higher_order_field_shift_ppg') or 0):+.3f}] | "
                    f"current-opp shift={float(release.get('current_opponent_shift_ppg') or 0):+.3f} ppg | "
                    f"timing={release.get('timing_proxy') or '-'}"
                )
                if release.get("cascade_orders") is not None:
                    lines.append(
                        f"    cascade: model={release.get('model') or '-'} | "
                        f"N2+={int(release.get('higher_order_scenarios') or 0)} | "
                        f"orders={len(release.get('cascade_orders') or [])} | "
                        f"pruned_mass={float(release.get('cascade_pruned_probability_mass') or 0):.3f} | "
                        f"stop={','.join(release.get('cascade_stop_reasons') or []) or 'NONE'}"
                    )
            print("\n".join(lines), flush=True)

def cmd_defense_channel(args):
    from src.specialist_policy_v032 import evaluate_defense_channel, save_channel_report
    from src.weekly_manager import load_snapshot
    snapshot = load_snapshot(args.snapshot)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    team_name = args.team or _configured_user_team(args.league)
    print("Evaluating v0.36 bounded league-response cascade + temporal defense market CRN...", flush=True)
    report = evaluate_defense_channel(
        snapshot, league, model, values_path=args.values, team_name=team_name,
        team_id=args.team_id, mc_scenarios=args.mc,
    )
    _print_specialist_channel(report, limit=args.limit)
    path = save_channel_report(report, args.out)
    print(f"\nDecision audit: {path}")


def cmd_kicker_channel(args):
    from src.specialist_policy_v032 import evaluate_kicker_channel, save_channel_report
    from src.weekly_manager import load_snapshot
    snapshot = load_snapshot(args.snapshot)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text())
    team_name = args.team or _configured_user_team(args.league)
    print("Evaluating v0.36 temporal kicker market + complete-state CRN...", flush=True)
    report = evaluate_kicker_channel(
        snapshot, league, model, values_path=args.values, team_name=team_name,
        team_id=args.team_id, mc_scenarios=args.mc,
    )
    _print_specialist_channel(report, limit=args.limit)
    path = save_channel_report(report, args.out)
    print(f"\nDecision audit: {path}")


def cmd_trade_eval(args):
    from src.market_manager import evaluate_trade, save_trade_report
    from src.weekly_manager import load_snapshot, resolve_team

    snapshot = load_snapshot(args.snapshot)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    team_name = args.team or _configured_user_team(args.league)
    user_team = resolve_team(snapshot, team_name=team_name, team_id=args.team_id)
    try:
        report = evaluate_trade(
            snapshot, league, model, values_path=args.values, user_team=user_team,
            partner_team_id=int(args.partner_team_id),
            give_ids=_parse_id_list(args.give), receive_ids=_parse_id_list(args.receive),
            mc_scenarios=args.mc,
        )
    except ValueError as exc:
        print(f"Trade evaluation error: {exc}")
        raise SystemExit(2) from None

    print(f"TRADE EVALUATION v0.31-fixed2 · PLAYER CHANNEL · MC={report['mc_scenarios']}")
    print(f"Us: {report['user_team']['name']}  Partner: {report['partner_team']['name']}")
    print(f"GIVE:    {_trade_player_names(report['give'])}")
    print(f"RECEIVE: {_trade_player_names(report['receive'])}")
    if report.get('user_auto_drops'):
        print(f"Our modeled post-trade release: {_trade_player_names(report['user_auto_drops'])}")
    if report.get('partner_auto_drops'):
        print(f"Partner modeled post-trade release: {_trade_player_names(report['partner_auto_drops'])}")
    if report.get('user_auto_adds'):
        print(f"Our modeled post-trade FA fill: {_trade_player_names(report['user_auto_adds'])}")
    if report.get('partner_auto_adds'):
        print(f"Partner modeled post-trade FA fill: {_trade_player_names(report['partner_auto_adds'])}")
    u = report['user']['delta_season_ppg']
    q = report['partner']['delta_season_ppg']
    print(f"Our season lineup Δ:     {u['mean']:+.3f} ppg  P(better)={u['p_better']:.1%}  mean-CI=[{report['user']['delta_mean_interval_p16']:+.3f},{report['user']['delta_mean_interval_p84']:+.3f}]")
    print(f"Partner season lineup Δ: {q['mean']:+.3f} ppg  P(better)={q['p_better']:.1%}  mean-CI=[{report['partner']['delta_mean_interval_p16']:+.3f},{report['partner']['delta_mean_interval_p84']:+.3f}]")
    r = report['response']
    print(f"Partner response: ACCEPT={r['p_accept']:.1%} COUNTER={r['p_counter']:.1%} REJECT={r['p_reject']:.1%} [{r['model']}]")
    print(f"Expected accepted-offer value: {report['expected_offer_value']:+.3f} season ppg")
    print(f"Classification: {report['classification']}")
    path = save_trade_report(report, args.out)
    print(f"Trade audit: {path}")


def cmd_trade_search(args):
    from src.market_manager import search_trades
    from src.weekly_manager import load_snapshot, resolve_team

    snapshot = load_snapshot(args.snapshot)
    league = load_league(args.league)
    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    team_name = args.team or _configured_user_team(args.league)
    user_team = resolve_team(snapshot, team_name=team_name, team_id=args.team_id)
    rows = search_trades(
        snapshot, league, model, values_path=args.values, user_team=user_team,
        limit=args.limit, mc_scenarios=args.mc,
    )
    print(f"TRADE SEARCH v0.31-fixed2 · PLAYER CHANNEL · one-for-one · results={len(rows)}")
    if not rows:
        print("No screened one-for-one offer survived the current market screen.")
        return
    for i, row in enumerate(rows, 1):
        print(
            f"{i:>2}. {row['partner_name']}: GIVE {row['give_name']} ({row['give_position']}) / "
            f"RECEIVE {row['receive_name']} ({row['receive_position']})"
        )
        print(
            f"    our Δ={float(row['our_delta_season_ppg']):+.3f} ppg P+={float(row['our_p_better']):.1%} · "
            f"partner Δ={float(row['partner_delta_season_ppg']):+.3f} ppg P+={float(row['partner_p_better']):.1%}"
        )
        print(
            f"    accept/counter/reject={float(row['p_accept']):.1%}/{float(row['p_counter']):.1%}/{float(row['p_reject']):.1%} · "
            f"offer EV={float(row['expected_offer_value']):+.3f} · {row['classification']} · MC={row['mc_scenarios']}"
        )


def cmd_chat_report(args):
    """Print and persist a compact diagnosis using the exact GUI service layer."""
    from src.gui.season_service import SeasonGuiError, SeasonGuiService
    try:
        service = SeasonGuiService(
            snapshot_path=args.snapshot,
            league_path=args.league,
            model_path=args.model,
            values_path=args.values,
            team_name=args.team,
            team_id=args.team_id,
            mc_scenarios=args.mc,
        )
        if (args.add_id is None) != (args.drop_id is None):
            raise SeasonGuiError("--add-id and --drop-id must be supplied together")
        trade_fields = [args.trade_partner_id, args.trade_give, args.trade_receive]
        if any(x is not None for x in trade_fields) and not all(x is not None for x in trade_fields):
            raise SeasonGuiError("--trade-partner-id, --trade-give, and --trade-receive must be supplied together")
        trade_result = None
        if args.trade_partner_id is not None:
            trade_result = service.evaluate_trade_offer(
                int(args.trade_partner_id), _parse_id_list(args.trade_give), _parse_id_list(args.trade_receive),
                mc_scenarios=args.mc or service.mc_scenarios,
            )
        result = service.write_chat_report(
            out_dir=args.out,
            add_espn_id=args.add_id,
            drop_espn_id=args.drop_id,
            trade_result=trade_result,
        )
    except SeasonGuiError as exc:
        print(f"Chat report error: {exc}")
        raise SystemExit(2) from None
    print(result["text"], end="")
    print(f"\nChat report TXT: {result['text_path']}")
    print(f"Chat report JSON: {result['json_path']}")



def cmd_closure_capture(args):
    from src.closure import capture_pregame_predictions
    try:
        capture, path = capture_pregame_predictions(
            snapshot_path=args.snapshot,
            league_path=args.league,
            model_path=args.model,
            values_path=args.values,
            team_name=args.team,
            team_id=args.team_id,
            out_dir=args.out,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Closure capture error: {exc}")
        raise SystemExit(2) from None
    players = capture.get("players") or []
    us = sum(1 for row in players if row.get("side") == "US")
    opp = sum(1 for row in players if row.get("side") == "OPP")
    components = sum(len(row.get("component_predictions") or {}) for row in players)
    print(f"Pregame closure capture: {path}")
    print(f"Season/week: {capture.get('season')}/{capture.get('week')}  players={len(players)} (US={us}, OPP={opp})")
    print(f"Component predictions: {components}")
    from src.prospective_measurement_v034 import capture_summary
    measurement = capture_summary(capture)
    print(f"Measurement contract: {measurement.get('measurement_contract') or '-'}")
    print(f"All-league player predictions: {int(measurement.get('league_players') or 0)}")
    print(
        f"Specialist predictions: total={int(measurement.get('specialists') or 0)} "
        f"DST={int(measurement.get('dst') or 0)} K={int(measurement.get('kickers') or 0)}"
    )
    digest = str(measurement.get('snapshot_sha256') or '-')
    print(
        f"Behavior state: teams={int(measurement.get('behavior_teams') or 0)} "
        f"market_players={int(measurement.get('market_players') or 0)} snapshot_sha256={digest[:12]}"
    )
    print(f"Temporal player-state predicted swaps: {int(measurement.get('temporal_player_transactions') or 0)}")
    if measurement.get("cascade_model"):
        print(
            f"League-response cascade: {measurement.get('cascade_model')} "
            f"depth={int(measurement.get('cascade_max_depth') or 0)} "
            f"N2+={int(measurement.get('cascade_scenarios') or 0)}"
        )
    print(f"Capture integrity: {'OK' if measurement.get('integrity_ok') else 'FAILED'}")


def cmd_closure_update(args):
    from src.closure import update_closure
    seasons = [int(x) for x in str(args.seasons).split(",") if str(x).strip()] if args.seasons else None
    try:
        result = update_closure(
            prediction_dir=args.predictions,
            raw_dir=args.raw,
            out_dir=args.out,
            seasons=seasons,
            force=not args.cached,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Closure update error: {exc}")
        raise SystemExit(2) from None
    summary = result["summary"]
    fantasy = summary.get("fantasy") or {}
    print(f"Closure ledger: {result['paths']['ledger']}")
    print(f"Closure summary: {result['paths']['summary']}")
    print(f"Immutable closure snapshot: {result['paths']['snapshot']}")
    print(f"Fantasy observations: {fantasy.get('n', 0)}")
    if fantasy.get("rmse") is not None:
        print(f"Corrected MC RMSE: {float(fantasy['rmse']):.4f}")
        if fantasy.get("base_rmse") is not None:
            print(f"Base MC RMSE: {float(fantasy['base_rmse']):.4f}")
            print(f"Interaction delta-RMSE: {float(fantasy.get('interaction_rmse_improvement') or 0.0):+.4f}")
    pull = summary.get("pull") or {}
    if pull.get("n"):
        print(f"Pulls: n={pull.get('n')} mean={float(pull.get('mean') or 0.0):+.3f} sd={float(pull.get('sd') or 0.0):.3f}")
    availability = summary.get("availability") or {}
    print(f"Availability outcomes with explicit active truth: {availability.get('n', 0)}")


def cmd_closure_status(args):
    from src.closure import load_closure_ledger, load_closure_summary
    summary = load_closure_summary(args.summary)
    ledger = load_closure_ledger(args.ledger)
    fantasy = summary.get("fantasy") or {}
    pull = summary.get("pull") or {}
    availability = summary.get("availability") or {}
    print("DATA/MC CLOSURE v0.29")
    print(f"Ledger rows: {len(ledger)}")
    print(f"Weeks: {', '.join(summary.get('weeks') or []) or '-'}")
    print(f"Fantasy observations: {fantasy.get('n', 0)}")
    if fantasy.get("rmse") is not None:
        print(f"Fantasy bias/MAE/RMSE: {float(fantasy.get('bias') or 0.0):+.4f} / {float(fantasy.get('mae') or 0.0):.4f} / {float(fantasy.get('rmse') or 0.0):.4f}")
        if fantasy.get("base_rmse") is not None:
            print(f"Base -> corrected RMSE: {float(fantasy['base_rmse']):.4f} -> {float(fantasy['rmse']):.4f}  improvement={float(fantasy.get('interaction_rmse_improvement') or 0.0):+.4f}")
    print(f"Pull calibration: n={pull.get('n', 0)} mean={pull.get('mean')} sd={pull.get('sd')}")
    print(f"Availability calibration: n={availability.get('n', 0)} brier={availability.get('brier')}")
    components = summary.get("components") or {}
    if components:
        print("Components:")
        for key in sorted(components):
            row = components[key]
            if int(row.get("n") or 0) <= 0:
                continue
            print(
                f"  {key:<38} n={int(row.get('n') or 0):4d} "
                f"bias={float(row.get('bias') or 0.0):+.4f} RMSE={float(row.get('rmse') or 0.0):.4f} "
                f"base={row.get('base_rmse')} dRMSE={row.get('interaction_rmse_improvement')}"
            )

def cmd_gui(args):
    """Launch the read-only season-management control room."""
    from src.gui.season_app import run_season_gui
    try:
        run_season_gui(
            snapshot_path=args.snapshot,
            league_path=args.league,
            model_path=args.model,
            values_path=args.values,
            secrets_path=args.secrets,
            snapshots_dir=args.snapshots_dir,
            team_name=args.team,
            team_id=args.team_id,
            port=args.port,
            native=args.native,
            mc_scenarios=args.mc,
        )
    except RuntimeError as exc:
        print("\nGUI startup error:")
        print(exc)
        raise SystemExit(2) from None


def cmd_draft_gui(args):
    """Preserve the legacy draft cockpit for archived/replay use."""
    from src.gui.app import run_gui
    try:
        run_gui(
            board_path=args.board,
            state_path=args.state,
            league_path=args.league,
            model_path=args.model,
            port=args.port,
            native=args.native,
        )
    except RuntimeError as exc:
        print("\nDraft GUI startup error:")
        print(exc)
        raise SystemExit(2) from None

def build_parser():
    p = argparse.ArgumentParser(description="Fantasy football draft + season manager")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("league")
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.set_defaults(func=cmd_league)

    s = sub.add_parser("picks")
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.set_defaults(func=cmd_picks)

    s = sub.add_parser("init-draft")
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("record")
    s.add_argument("name")
    s.add_argument("--player-id")
    s.add_argument("--position")
    s.add_argument("--nfl-team")
    s.add_argument("--board", default=None,
                   help="Resolve name against canonical ESPN live board")
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.set_defaults(func=cmd_record)

    s = sub.add_parser("status")
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("score")
    s.add_argument("kind", choices=["offense", "kicker", "dst"])
    s.add_argument("stats")
    s.set_defaults(func=cmd_score)

    s = sub.add_parser("sync-espn", help="Download current ESPN PPR draft market")
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--out", default=str(RAW_ESPN))
    s.set_defaults(func=cmd_sync_espn)

    s = sub.add_parser("sync-nflverse", help="Download canonical players + explicit season-level historical weekly stats")
    s.add_argument("--out", default=str(RAW_NFLVERSE))
    s.add_argument("--model", default=str(DEFAULT_MODEL), help="Use interaction-grid seasons from this model when --seasons is omitted")
    s.add_argument("--seasons", help="Comma-separated player-stat seasons; default comes from interaction_grid.fit.seasons")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_sync_nflverse)

    s = sub.add_parser("interaction-fit", help="Fit v0.28 precomputed player x defense Data/MC correction grids")
    s.add_argument("--stats", default=str(RAW_NFLVERSE / "player_stats.csv.gz"))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--cache", default=str(INTERACTION_CACHE))
    s.add_argument("--out", default=str(INTERACTION_GRID_DIR))
    s.add_argument("--seasons", help="Comma-separated seasons; default comes from config/model.json")
    s.set_defaults(func=cmd_interaction_fit)

    s = sub.add_parser("interaction-status", help="Show fitted v0.28 interaction-grid validation/commissioning status")
    s.add_argument("--artifact", default=str(INTERACTION_GRID_DIR))
    s.set_defaults(func=cmd_interaction_status)

    s = sub.add_parser("build-priors", help="Build baseline veteran historical priors")
    s.add_argument("--stats", default=str(RAW_NFLVERSE / "player_stats.csv.gz"))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--out", default=str(PROCESSED / "historical_priors.csv"))
    s.set_defaults(func=cmd_build_priors)

    s = sub.add_parser("build-master", help="Join ESPN market + nflverse IDs + priors")
    s.add_argument("--espn", default=str(RAW_ESPN / "player_pool_2026.csv"))
    s.add_argument("--players", default=str(RAW_NFLVERSE / "players.csv"))
    s.add_argument("--priors", default=str(PROCESSED / "historical_priors.csv"))
    s.add_argument("--out", default=str(PROCESSED / "player_master.csv"))
    s.set_defaults(func=cmd_build_master)


    s = sub.add_parser("inspect-data", help="Inspect current player-data coverage and joins")
    s.add_argument("--master", default=str(PROCESSED / "player_master.csv"))
    s.add_argument("--priors", default=str(PROCESSED / "historical_priors.csv"))
    s.add_argument("--out", default=str(PROCESSED / "diagnostics"))
    s.add_argument("--top-n", type=int, default=50)
    s.add_argument("--unmatched-limit", type=int, default=20)
    s.add_argument("--board-limit", type=int, default=30)
    s.set_defaults(func=cmd_inspect_data)


    s = sub.add_parser("projection-status", help="Show ESPN projection coverage by core position")
    s.add_argument("--master", default=str(PROCESSED / "player_master.csv"))
    s.set_defaults(func=cmd_projection_status)


    s = sub.add_parser("build-values", help="Build the 2026 latent player-value model")
    s.add_argument("--master", default=str(PROCESSED / "player_master.csv"))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--out", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--calibration", default=str(PROCESSED / "projection_calibration.json"))
    s.add_argument("--stats", default=str(RAW_NFLVERSE / "player_stats.csv.gz"))
    s.add_argument("--transition", default=str(PROCESSED / "transition_calibration.json"))
    s.set_defaults(func=cmd_build_values)

    s = sub.add_parser("value-board", help="Print the current modeled player board")
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--by", choices=["value", "market"], default="market")
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_value_board)


    s = sub.add_parser("build-draft-values", help="Build positional replacement/tier draft values")
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--out", default=str(PROCESSED / "draft_values_2026.csv"))
    s.add_argument("--diagnostics", default=str(PROCESSED / "draft_value_diagnostics.json"))
    s.set_defaults(func=cmd_build_draft_values)

    s = sub.add_parser("draft-board", help="Print position-relative draft board")
    s.add_argument("--values", default=str(PROCESSED / "draft_values_2026.csv"))
    s.add_argument("--by", choices=["score", "vorp", "market"], default="score")
    s.add_argument("--position", choices=["QB", "RB", "WR", "TE"])
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_draft_board)


    s = sub.add_parser("build-market", help="Build current draftability and market pick model")
    s.add_argument("--values", default=str(PROCESSED / "draft_values_2026.csv"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--out", default=str(PROCESSED / "draft_market_2026.csv"))
    s.add_argument("--diagnostics", default=str(PROCESSED / "draft_market_diagnostics.json"))
    s.set_defaults(func=cmd_build_market)

    s = sub.add_parser("survival-board", help="Show conditional availability at a future pick")
    s.add_argument("--values", default=str(PROCESSED / "draft_market_2026.csv"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--current-pick", type=int, required=True)
    s.add_argument("--target-pick", type=int)
    s.add_argument("--by", choices=["value", "urgency", "market"], default="urgency")
    s.add_argument("--position", choices=["QB", "RB", "WR", "TE"])
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_survival_board)


    s = sub.add_parser("build-live-board", help="Build eligibility-aware live draft board")
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--market-pre", default=str(PROCESSED / "player_market_2026.csv"))
    s.add_argument("--draft-values", default=str(PROCESSED / "draft_values_2026.csv"))
    s.add_argument("--out", default=str(PROCESSED / "live_board_2026.csv"))
    s.add_argument("--market-diagnostics", default=str(PROCESSED / "draft_market_diagnostics.json"))
    s.add_argument("--draft-diagnostics", default=str(PROCESSED / "draft_value_diagnostics.json"))
    s.set_defaults(func=cmd_build_live_board)

    s = sub.add_parser("live-board", help="Show state-aware available-player board")
    s.add_argument("--board", default=str(PROCESSED / "live_board_2026.csv"))
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--position", choices=["QB", "RB", "WR", "TE"])
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_live_board)

    s = sub.add_parser("recommend", help="Full-roster draft recommendation / off-turn forecast")
    s.add_argument("--board", default=str(PROCESSED / "live_board_2026.csv"))
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--engine", choices=["fast", "deep"], default="fast")
    s.add_argument("--simulations", type=int)
    s.add_argument("--seed", type=int)
    s.add_argument("--candidates", type=int)
    s.add_argument("--limit", type=int, default=15)
    s.set_defaults(func=cmd_recommend)


    s = sub.add_parser("import-mock", help="Parse a completed ESPN mock-draft markdown export")
    s.add_argument("--file", required=True)
    s.add_argument("--out", default=str(Path("data/mock_drafts")))
    s.add_argument("--teams", type=int, default=12)
    s.set_defaults(func=cmd_import_mock)

    s = sub.add_parser("mock-status", help="Show stored complete mock-draft calibration samples")
    s.add_argument("--dir", default=str(Path("data/mock_drafts")))
    s.set_defaults(func=cmd_mock_status)


    s = sub.add_parser("bank-status", help="Show the persistent conditioned DEEP particle bank")
    s.add_argument("--board", default=str(PROCESSED / "live_board_2026.csv"))
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.set_defaults(func=cmd_bank_status)


    s = sub.add_parser("season-sync", help="Authenticated ESPN + public Sleeper/NFL.com season snapshot")
    s.add_argument("--secrets", default=DEFAULT_SECRETS, help="Defaults to ../config/secrets.json, then config/secrets.json")
    s.add_argument("--out", default=str(SEASON_SNAPSHOTS))
    s.add_argument("--week", type=int)
    s.add_argument("--skip-sleeper", action="store_true")
    s.add_argument("--skip-nfl", action="store_true", help="Skip public NFL.com transaction/injury-page snapshot")
    s.set_defaults(func=cmd_season_sync)

    s = sub.add_parser("season-status", help="Show current team/roster from the latest season snapshot")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.set_defaults(func=cmd_season_status)

    s = sub.add_parser("week-lineup", help="Optimize the legal weekly lineup and injury contingencies")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.set_defaults(func=cmd_week_lineup)

    s = sub.add_parser("week-yields", help="Inspect v0.23 model/ESPN/matchup predictive-yield states for the current roster")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.set_defaults(func=cmd_week_yields)

    s = sub.add_parser("roster-actions", help="Player channel: evaluate QB/RB/WR/TE free-agent/waiver add-drop counterfactuals")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--position", choices=["QB", "RB", "WR", "TE"])
    s.add_argument("--mc", type=int, help="Predictive universes; defaults to configured 16384")
    s.add_argument("--limit", type=int, default=12)
    s.add_argument("--show-negative", action="store_true")
    s.add_argument("--out", default=str(Path("data/season_decisions")))
    s.add_argument("--prediction-out", default=str(Path("data/season_predictions")))
    s.set_defaults(func=cmd_roster_actions)


    s = sub.add_parser("defense-channel", help="Defense channel: static diagnostics, dynamic one-slot streaming, and paired carry2 complete-state response")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--mc", type=int, help="Specialist-channel universes; defaults to configured 2048")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--out", default=str(Path("data/season_decisions")))
    s.set_defaults(func=cmd_defense_channel)

    s = sub.add_parser("kicker-channel", help="Kicker channel: static diagnostics plus dynamic one-slot streaming policy")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--mc", type=int, help="Specialist-channel universes; defaults to configured 2048")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--out", default=str(Path("data/season_decisions")))
    s.set_defaults(func=cmd_kicker_channel)

    s = sub.add_parser("trade-eval", help="Evaluate a hypothetical trade for both managers with paired predictive MC")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--partner-team-id", type=int, required=True)
    s.add_argument("--give", required=True, help="Comma-separated ESPN player IDs from our roster (max 2)")
    s.add_argument("--receive", required=True, help="Comma-separated ESPN player IDs from partner roster (max 2)")
    s.add_argument("--mc", type=int, help="Predictive universes; defaults to configured 16384")
    s.add_argument("--out", default=str(Path("data/season_decisions")))
    s.set_defaults(func=cmd_trade_eval)

    s = sub.add_parser("trade-search", help="Screen league-wide one-for-one trades, then evaluate the best candidates with predictive MC")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--limit", type=int, default=6)
    s.add_argument("--mc", type=int, help="Search-stage predictive universes; defaults to market_manager.trade_search_mc_scenarios")
    s.set_defaults(func=cmd_trade_search)

    s = sub.add_parser("closure-capture", help="Persist an immutable pregame v0.29 component/yield prediction state for later Data/MC closure")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--out", default=str(CLOSURE_PREDICTIONS))
    s.set_defaults(func=cmd_closure_capture)

    s = sub.add_parser("closure-update", help="Ingest nflverse postgame observations and rebuild the prospective Data/MC closure ledger")
    s.add_argument("--predictions", default=str(CLOSURE_PREDICTIONS))
    s.add_argument("--raw", default=str(CLOSURE_RAW))
    s.add_argument("--out", default=str(CLOSURE_ROOT))
    s.add_argument("--seasons", help="Optional comma-separated seasons; defaults to seasons present in pregame captures")
    s.add_argument("--cached", action="store_true", help="Reuse the cached current-season nflverse weekly stats instead of refreshing them")
    s.set_defaults(func=cmd_closure_update)

    s = sub.add_parser("closure-status", help="Show accumulated v0.29 football-component, fantasy-yield, pull, and availability closure")
    s.add_argument("--ledger", default=str(CLOSURE_ROOT / "ledger.csv"))
    s.add_argument("--summary", default=str(CLOSURE_ROOT / "summary.json"))
    s.set_defaults(func=cmd_closure_status)

    s = sub.add_parser("chat-report", help="Generate a compact paste-friendly diagnosis from the season GUI service state")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--add-id", type=int, help="Optional ESPN player ID for a selected add/drop experiment")
    s.add_argument("--drop-id", type=int, help="Optional ESPN player ID for a selected add/drop experiment")
    s.add_argument("--trade-partner-id", type=int, help="Optional partner team id for a selected trade experiment")
    s.add_argument("--trade-give", help="Comma-separated ESPN player IDs we give (max 2)")
    s.add_argument("--trade-receive", help="Comma-separated ESPN player IDs we receive (max 2)")
    s.add_argument("--mc", type=int, help="Predictive Monte Carlo universes (overrides config for this report)")
    s.add_argument("--out", default=str(Path("data/chat_reports")))
    s.set_defaults(func=cmd_chat_report)

    s = sub.add_parser("gui", help="Launch the v0.31-fixed2 local season-management control room")
    s.add_argument("--snapshot", default=str(SEASON_SNAPSHOTS / "latest.json"))
    s.add_argument("--snapshots-dir", default=str(SEASON_SNAPSHOTS))
    s.add_argument("--secrets", default=DEFAULT_SECRETS, help="Used only when Refresh Data is clicked")
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--values", default=str(PROCESSED / "player_values_2026.csv"))
    s.add_argument("--team")
    s.add_argument("--team-id", type=int)
    s.add_argument("--mc", type=int, help="Initial predictive Monte Carlo universes; GUI selector plus Run selected MC can change this later")
    s.add_argument("--port", type=int, default=8080)
    s.add_argument("--native", action="store_true",
                   help="Open a native desktop window (requires NiceGUI native extra)")
    s.set_defaults(func=cmd_gui)

    s = sub.add_parser("draft-gui", help="Launch the archived local NiceGUI draft cockpit")
    s.add_argument("--board", default=str(PROCESSED / "live_board_2026.csv"))
    s.add_argument("--state", default=str(DEFAULT_STATE))
    s.add_argument("--league", default=str(DEFAULT_LEAGUE))
    s.add_argument("--model", default=str(DEFAULT_MODEL))
    s.add_argument("--port", type=int, default=8081)
    s.add_argument("--native", action="store_true",
                   help="Open a native desktop window (requires NiceGUI native extra)")
    s.set_defaults(func=cmd_draft_gui)

    s = sub.add_parser("data-status")
    s.set_defaults(func=cmd_data_status)

    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
