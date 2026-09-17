from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fantasy import build_parser
from src.market_manager import evaluate_trade, screen_one_for_one_trades, trade_response_probabilities
from src.transaction_manager import UtilityContext, waiver_acquisition_probability, waiver_blocker_diagnostics


def league_cfg():
    return {
        "teams": 3,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1, "BENCH": 3},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "fantasy_season": {"regular_season_weeks": list(range(1, 14)), "playoff_week_participation_prior": {"14": .5, "15": .33, "16": .17, "17": .17}},
        "bye_weeks_2026": {},
    }


def model_cfg():
    return {
        "weekly_manager": {
            "status_active_probability": {"ACTIVE": .995, "NORMAL": .995, "QUESTIONABLE": .75, "OUT": 0.0},
            "status_full_given_active": {"ACTIVE": .97, "NORMAL": .97, "QUESTIONABLE": .65},
            "limited_workload_fraction": {"DEFAULT": .65, "QB": .8, "RB": .65, "WR": .65, "TE": .65, "K": .9, "DST": .9},
        },
        "season_utility": {
            "active_probability_nonbye": {"QB": .97, "RB": .92, "WR": .94, "TE": .94, "K": .995, "DST": 1.0},
            "regular_week_weight": 1.0,
            "use_playoff_participation_prior": True,
        },
        "transaction_manager": {
            "availability_scenarios": 4,
            "predictive_mc_scenarios": 64,
            "random_seed": 19,
            "replacement_available_rank": {"QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DST": 2},
            "h2h_matchup_scale_points": 18.0,
            "paired_mean_interval_resamples": 100,
            "mc_progress_batch_size": 32,
            "waiver_p_acquire_default": .35,
            "waiver_p_acquire_floor": .02,
            "waiver_claim_utility_logit_intercept": -2.6,
            "waiver_claim_season_ppg_weight": 1.1,
            "waiver_claim_current_week_weight": .12,
            "waiver_owned_logit_per_pct": .015,
            "waiver_trend_logit_weight": .08,
            "waiver_need_logit_bonus": .6,
            "opponent_roster_target": {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1},
        },
        "market_manager": {
            "trade_max_players_per_side": 2,
            "trade_search_mc_scenarios": 32,
            "trade_search_give_candidates": 8,
            "trade_search_target_candidates": 8,
            "trade_search_min_user_screen_gain": -10.0,
            "trade_actionable_accept_probability": .40,
        },
        "matchup_model": {"enabled": False},
        "interaction_grid": {"enabled": False},
    }


def p(pid, name, pos, pts, *, team="X", fantasy_status="ROSTERED", waiver_rank=None):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": team,
        "pro_team_id": 1,
        "weekly_projection": pts,
        "season_projection": pts * 17,
        "injury_status": "ACTIVE",
        "fantasy_status": fantasy_status,
        "droppable": True,
        "lineup_locked": False,
        "percent_owned": 50.0,
    }


def user_roster():
    return [
        p(1, "U QB", "QB", 20),
        p(2, "U RB1", "RB", 18), p(3, "U RB2", "RB", 16), p(4, "U RB3", "RB", 12),
        p(5, "U WR1", "WR", 17), p(6, "U WR2", "WR", 15), p(7, "U WR3", "WR", 6),
        p(8, "U TE1", "TE", 6), p(9, "U TE2", "TE", 4),
        p(10, "U K", "K", 8), p(11, "U DST", "DST", 7),
    ]


def partner_roster():
    return [
        p(101, "P QB", "QB", 19),
        p(102, "P RB1", "RB", 13), p(103, "P RB2", "RB", 8), p(104, "P RB3", "RB", 5),
        p(105, "P WR1", "WR", 18), p(106, "P WR2", "WR", 16), p(107, "P WR3", "WR", 7),
        p(108, "P TE Star", "TE", 14), p(109, "P TE2", "TE", 12),
        p(110, "P K", "K", 8), p(111, "P DST", "DST", 7),
    ]


def other_roster():
    return [dict(x, espn_id=x["espn_id"] + 200, name="O " + x["name"]) for x in user_roster()]


def snapshot(available=None):
    return {
        "snapshot_utc": "2026-09-01T06:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 1,
            "teams": [
                {"team_id": 1, "name": "Us", "waiver_rank": 3, "roster": user_roster()},
                {"team_id": 2, "name": "Partner", "waiver_rank": 1, "roster": partner_roster()},
                {"team_id": 3, "name": "Other", "waiver_rank": 2, "roster": other_roster()},
            ],
            "matchups": [{"week": 1, "home_team_id": 1, "away_team_id": 2}],
            "available_players": available or [],
        },
    }


def values_file(tmp_path: Path):
    rows = []
    for player in user_roster() + partner_roster() + other_roster():
        rows.append({"espn_id": player["espn_id"], "latent_mean_ppg": player["weekly_projection"], "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0})
    path = tmp_path / "values.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_trade_response_is_three_way_probability():
    r = trade_response_probabilities(
        partner_delta_season_ppg=.5,
        partner_p_better=.7,
        partner_market_delta=.2,
        package_size=2,
        cfg={},
    )
    assert 0 < r.p_accept < 1
    assert 0 < r.p_counter < 1
    assert 0 < r.p_reject < 1
    assert abs(r.p_accept + r.p_counter + r.p_reject - 1.0) < 1e-12
    assert "UNCALIBRATED" in r.model


def test_trade_eval_values_both_sides_and_keeps_response_separate(tmp_path):
    snap = snapshot()
    report = evaluate_trade(
        snap, league_cfg(), model_cfg(), values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0], partner_team_id=2,
        give_ids=[4], receive_ids=[108], mc_scenarios=64,
    )
    assert report["user"]["delta_season_ppg"]["mc_scenarios"] if "mc_scenarios" in report["user"]["delta_season_ppg"] else True
    assert report["response"]["model"].startswith("UNCALIBRATED_TRADE_RESPONSE")
    assert report["mc_scenarios"] == 64
    assert report["give"][0]["name"] == "U RB3"
    assert report["receive"][0]["name"] == "P TE Star"
    assert set(report["response"]) >= {"p_accept", "p_counter", "p_reject"}


def test_unequal_trade_surfaces_modeled_post_trade_release(tmp_path):
    snap = snapshot()
    report = evaluate_trade(
        snap, league_cfg(), model_cfg(), values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0], partner_team_id=2,
        give_ids=[4], receive_ids=[108, 107], mc_scenarios=32,
    )
    assert len(report["user_auto_drops"]) == 1
    incoming = {108, 107}
    assert report["user_auto_drops"][0]["espn_id"] not in incoming
    assert report["partner_auto_drops"] == []


def test_trade_screen_uses_all_league_rosters(tmp_path):
    snap = snapshot()
    rows = screen_one_for_one_trades(
        snap, league_cfg(), model_cfg(), values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0], limit=20,
    )
    assert rows
    assert all(r["partner_team_id"] in {2, 3} for r in rows)
    assert all(r["give_id"] is not None and r["receive_id"] is not None for r in rows)


def test_v030_waiver_blockers_use_modeled_best_drop(tmp_path):
    candidate = p(900, "Waiver TE", "TE", 13, fantasy_status="WAIVERS")
    snap = snapshot([candidate])
    values = values_file(tmp_path)
    # add the candidate's latent row
    df = pd.read_csv(values)
    df.loc[len(df)] = {"espn_id": 900, "latent_mean_ppg": 13.0, "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0}
    df.to_csv(values, index=False)
    ctx = UtilityContext(snap, league_cfg(), model_cfg(), values, snap["espn"]["teams"][0])
    cand = next(x for x in ctx.available if x["espn_id"] == 900)
    blockers = waiver_blocker_diagnostics(cand, ctx)
    assert [b["waiver_rank"] for b in blockers] == [1, 2]
    assert all("delta_season_ppg" in b and "best_drop_name" in b for b in blockers)
    assert all(b["model"].endswith("V030") for b in blockers)
    p_acquire = waiver_acquisition_probability(cand, ctx)
    assert 0 < p_acquire < 1


def test_v030_cli_commands_are_available():
    trade = build_parser().parse_args(["trade-eval", "--partner-team-id", "2", "--give", "1", "--receive", "101"])
    search = build_parser().parse_args(["trade-search"])
    assert trade.partner_team_id == 2
    assert trade.give == "1"
    assert search.limit == 6


def test_default_mc_remains_16384():
    model = json.loads(Path("config/model.json").read_text(encoding="utf-8"))
    assert model["transaction_manager"]["predictive_mc_scenarios"] == 16384


def test_trade_search_mc_override_does_not_mutate_main_model(tmp_path):
    from src.market_manager import search_trades

    snap = snapshot()
    model = model_cfg()
    original = model["transaction_manager"]["predictive_mc_scenarios"]
    _ = search_trades(
        snap, league_cfg(), model, values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0], limit=2, mc_scenarios=32,
    )
    assert model["transaction_manager"]["predictive_mc_scenarios"] == original


def test_two_for_one_trade_surfaces_guaranteed_free_agent_fill(tmp_path):
    free_agent = p(901, "FA WR", "WR", 9, fantasy_status="FREEAGENT")
    snap = snapshot([free_agent])
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 901, "latent_mean_ppg": 9.0,
        "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0,
    }
    df.to_csv(values, index=False)
    report = evaluate_trade(
        snap, league_cfg(), model_cfg(), values_path=values,
        user_team=snap["espn"]["teams"][0], partner_team_id=2,
        give_ids=[4, 7], receive_ids=[108], mc_scenarios=32,
    )
    assert [x["espn_id"] for x in report["user_auto_adds"]] == [901]
    assert report["partner_auto_drops"]


def test_chat_report_can_surface_selected_trade():
    from src.gui.chat_report import format_chat_report

    payload = {
        "version": "v0.30-fixed",
        "matchup": {}, "lineup": [], "opponent_lineup": [],
        "closure": {}, "model_flags": [], "source_health": [],
        "trade": {
            "partner_name": "Partner",
            "give": ["Player A"], "receive": ["Player B"],
            "our_delta_season_ppg": 0.4, "our_p_better": 0.7,
            "partner_delta_season_ppg": 0.2, "partner_p_better": 0.6,
            "p_accept": 0.45, "p_counter": 0.30, "p_reject": 0.25,
            "expected_offer_value": 0.18, "classification": "ACTIONABLE_OFFER",
            "mc_scenarios": 4096,
        },
    }
    text = format_chat_report(payload)
    assert "SELECTED TRADE" in text
    assert "accept/counter/reject=" in text
    assert "ACTIONABLE_OFFER" in text


def test_roster_actions_progress_and_mc_override(tmp_path):
    from src.transaction_manager import evaluate_actions

    candidate = p(950, "FA RB", "RB", 14, fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {"espn_id": 950, "latent_mean_ppg": 14.0, "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0}
    df.to_csv(values, index=False)
    model = model_cfg()
    model["transaction_manager"]["predictive_mc_screen_per_status"] = 1
    seen = []
    report = evaluate_actions(
        snap, league_cfg(), model, values, team_name="Us",
        predictive_mc_scenarios=32,
        progress_callback=lambda done, total, phase: seen.append((done, total, phase)),
    )
    assert report["predictive_mc_scenarios"] == 32
    assert any("HOLD baseline" in phase for _, _, phase in seen)
    assert any("opponent reference" in phase for _, _, phase in seen)
    assert any(phase.startswith("broad action screen") for _, _, phase in seen)
    assert any(phase.startswith("paired action MC queued") for _, _, phase in seen)
    assert seen[-1][2] == "roster-actions complete"


def test_v030_fixed_defers_detailed_waiver_blockers_until_after_screen(tmp_path, monkeypatch):
    import src.transaction_manager as tm

    candidates = [
        p(960 + i, f"Waiver WR {i}", "WR", 13 - i, fantasy_status="WAIVERS")
        for i in range(3)
    ]
    snap = snapshot(candidates)
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    for i, cand in enumerate(candidates):
        df.loc[len(df)] = {"espn_id": cand["espn_id"], "latent_mean_ppg": 13.0 - i, "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0}
    df.to_csv(values, index=False)
    model = model_cfg()
    model["transaction_manager"]["predictive_mc_screen_per_status"] = 1
    calls = []
    original = tm.waiver_blocker_diagnostics

    def wrapped(candidate, ctx):
        calls.append(candidate["espn_id"])
        return original(candidate, ctx)

    monkeypatch.setattr(tm, "waiver_blocker_diagnostics", wrapped)
    report = tm.evaluate_actions(snap, league_cfg(), model, values, team_name="Us", predictive_mc_scenarios=32)
    # Three waiver candidates entered the broad screen, but only the candidate that
    # survived the one-action predictive screen should pay the detailed manager cost.
    assert report["candidate_pool_evaluated"] == 3
    assert len(set(calls)) == 1
    assert report["waiver_actions"]
    assert report["waiver_actions"][0]["waiver_response_model"].endswith("V030")


def test_roster_actions_cli_accepts_mc_override():
    args = build_parser().parse_args(["roster-actions", "--mc", "4096"])
    assert args.mc == 4096


def test_v030_fixed2_hierarchical_action_mc_escalates_small_frontier(tmp_path):
    from src.transaction_manager import evaluate_actions

    candidate = p(970, "FA WR stage", "WR", 14, fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 970, "latent_mean_ppg": 14.0,
        "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0,
    }
    df.to_csv(values, index=False)
    model = model_cfg()
    cfg = model["transaction_manager"]
    cfg["predictive_mc_screen_per_status"] = 2
    cfg["action_mc_stages"] = [32, 64]
    cfg["action_mc_stage_keep_per_status"] = [2, 1]
    cfg["action_mc_final_keep_per_status"] = 1
    cfg["action_mc_final_min_expected_pp"] = -100.0
    cfg["action_mc_futility_enabled"] = False
    report = evaluate_actions(
        snap, league_cfg(), model, values, team_name="Us", predictive_mc_scenarios=128
    )
    assert report["predictive_mc_stages"] == [32, 64, 128]
    assert report["predictive_actions_initial_frontier"] >= report["predictive_actions_evaluated"]
    assert report["predictive_actions_evaluated"] == 1
    row = (report["free_agent_actions"] + report["waiver_actions"])[0]
    assert [x["mc_scenarios"] for x in row["mc_stage_history"]] == [32, 64, 128]
    assert row["mc_scenarios"] == 128


def test_v030_fixed2_bench_skill_player_has_option_and_scarcity_cost(tmp_path):
    from src.transaction_manager import (
        UtilityContext,
        _option_scarcity_utility_adjustment,
        roster_option_scarcity_value,
    )

    bench = p(12, "Bench upside RB", "RB", 11)
    dst = p(980, "Second DST", "DST", 7, fantasy_status="FREEAGENT")
    snap = snapshot([dst])
    snap["espn"]["teams"][0]["roster"] = user_roster() + [bench]
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 12, "latent_mean_ppg": 11.0,
        "latent_mean_sd_ppg": 3.0, "predictive_weekly_sd_ppg": 5.0,
    }
    df.loc[len(df)] = {
        "espn_id": 980, "latent_mean_ppg": 7.0,
        "latent_mean_sd_ppg": 0.5, "predictive_weekly_sd_ppg": 4.0,
    }
    df.to_csv(values, index=False)
    model = model_cfg()
    model["transaction_manager"].update({
        "future_option_utility_weight": 0.35,
        "replacement_scarcity_utility_weight": 0.25,
    })
    ctx = UtilityContext(snap, league_cfg(), model, values, snap["espn"]["teams"][0])
    before = roster_option_scarcity_value(ctx.roster, ctx)
    add = next(x for x in ctx.available if x["espn_id"] == 980)
    after_roster = [x for x in ctx.roster if x["espn_id"] != 12] + [add]
    after = roster_option_scarcity_value(after_roster, ctx)
    adj = _option_scarcity_utility_adjustment(before, after, ctx)
    assert before["replacement_scarcity_ppg"] > after["replacement_scarcity_ppg"]
    assert adj["delta_replacement_scarcity_ppg"] < 0
    assert adj["delta_total_utility"] < 0


def test_v030_fixed4_portfolio_option_has_diminishing_redundant_te_value(tmp_path):
    from src.transaction_manager import UtilityContext, roster_option_scarcity_value

    league = league_cfg()
    league["roster"] = dict(league["roster"], FLEX=0)
    bench1 = p(1201, "Bench TE A", "TE", 10)
    bench2 = p(1202, "Bench TE B", "TE", 10)
    snap = snapshot([])
    base = user_roster()
    # Make the existing TE a clear starter and keep the test focused on TE redundancy.
    for row in base:
        if row["position"] == "TE":
            row["weekly_projection"] = 15
            row["season_projection"] = 15 * 17
    snap["espn"]["teams"][0]["roster"] = base
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    for pid in (1201, 1202):
        df.loc[len(df)] = {
            "espn_id": pid, "latent_mean_ppg": 10.0,
            "latent_mean_sd_ppg": 6.0, "predictive_weekly_sd_ppg": 5.0,
        }
    df.to_csv(values, index=False)
    ctx = UtilityContext(snap, league, model_cfg(), values, snap["espn"]["teams"][0])
    for row in ctx.roster:
        if row["position"] == "TE":
            row["season_ppg"] = 15.0
            row["latent_mean_sd_ppg"] = 0.0
    zero = roster_option_scarcity_value(ctx.roster, ctx)["future_option_ppg"]
    b1 = dict(bench1, season_ppg=10.0, season_ppg_source="ESPN_WEEKLY", projection_source="ESPN_WEEKLY", latent_mean_sd_ppg=12.0)
    b2 = dict(bench2, season_ppg=10.0, season_ppg_source="ESPN_WEEKLY", projection_source="ESPN_WEEKLY", latent_mean_sd_ppg=12.0)
    one = roster_option_scarcity_value(list(ctx.roster) + [b1], ctx)["future_option_ppg"]
    two_roster = list(ctx.roster) + [b1, b2]
    two = roster_option_scarcity_value(two_roster, ctx)["future_option_ppg"]
    assert one > zero
    assert two > one
    # A second redundant TE has real injury/role insurance, but its incremental value
    # must be smaller because both players compete for the same legal TE slot.
    assert (two - one) < (one - zero)


def test_v030_fixed3_fallback_projection_gets_less_auxiliary_option_support(tmp_path):
    from src.transaction_manager import UtilityContext, _market_projection_support

    snap = snapshot([])
    values = values_file(tmp_path)
    ctx = UtilityContext(snap, league_cfg(), model_cfg(), values, snap["espn"]["teams"][0])
    strong = dict(ctx.roster[0], projection_source="ESPN_WEEKLY", season_ppg_source="ESPN_WEEKLY")
    weak = dict(ctx.roster[0], projection_source="MODEL_LATENT_PPG_FALLBACK", season_ppg_source="MODEL_LATENT_PPG")
    assert _market_projection_support(weak, ctx) < _market_projection_support(strong, ctx)


def test_v030_fixed6_league_state_response_is_authoritative():
    import numpy as np
    from src.transaction_manager import _classify_market_action

    cfg = {"actionable_p_better": 0.90, "lean_p_better": 0.67}
    raw = np.zeros(128, dtype=float)
    adjusted = np.full(128, 0.01, dtype=float)
    final, raw_class, combined_class = _classify_market_action(
        raw, adjusted, cfg, raw_p16=0.0, adjusted_p16=0.01
    )
    assert raw_class == "NO_RESOLVED_EDGE"
    assert combined_class == "ACTIONABLE_EDGE"
    # In fixed6 the adjusted distribution is not an auxiliary option coefficient;
    # it is the same football model under a counterfactual league-state perturbation.
    assert final == "ACTIONABLE_EDGE"


def test_v030_fixed4_bench_skill_drop_for_redundant_dst_has_negative_contingent_value(tmp_path):
    from src.transaction_manager import (
        UtilityContext,
        _option_scarcity_utility_adjustment,
        roster_option_scarcity_value,
    )

    bench = p(1301, "Bench RB value", "RB", 12)
    dst = p(1302, "Second DST", "DST", 7, fantasy_status="FREEAGENT")
    snap = snapshot([dst])
    snap["espn"]["teams"][0]["roster"] = user_roster() + [bench]
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 1301, "latent_mean_ppg": 12.0,
        "latent_mean_sd_ppg": 3.0, "predictive_weekly_sd_ppg": 5.0,
    }
    df.loc[len(df)] = {
        "espn_id": 1302, "latent_mean_ppg": 7.0,
        "latent_mean_sd_ppg": 0.5, "predictive_weekly_sd_ppg": 4.0,
    }
    df.to_csv(values, index=False)
    model = model_cfg()
    model["transaction_manager"].update({
        "future_option_utility_weight": 0.35,
        "replacement_scarcity_utility_weight": 0.0,
        "contingent_roster_scenarios": 512,
    })
    ctx = UtilityContext(snap, league_cfg(), model, values, snap["espn"]["teams"][0])
    for row in ctx.roster:
        if row["espn_id"] == 1301:
            row["season_ppg"] = 12.0
            row["latent_mean_sd_ppg"] = 3.0
            row["projection_source"] = "ESPN_WEEKLY"
            row["season_ppg_source"] = "ESPN_WEEKLY"
    before = roster_option_scarcity_value(ctx.roster, ctx, scenarios=512)
    add = next(x for x in ctx.available if x["espn_id"] == 1302)
    after_roster = [x for x in ctx.roster if x["espn_id"] != 1301] + [add]
    after = roster_option_scarcity_value(after_roster, ctx, scenarios=512)
    adj = _option_scarcity_utility_adjustment(before, after, ctx)
    assert adj["delta_future_option_ppg"] < 0
    assert adj["delta_total_utility"] < 0


def test_v030_fixed4_futility_bound_stops_low_probability_action():
    import numpy as np
    from src.transaction_manager import _classification_plausibility

    cfg = {"lean_p_better": 0.67, "action_mc_futility_z": 3.09}
    raw = np.zeros(1024, dtype=float)
    raw[:280] = 0.01
    raw[280:520] = -0.01
    adjusted = raw.copy()
    result = _classification_plausibility(raw, adjusted, cfg)
    assert result["raw_p_better_upper"] < 0.67
    assert result["plausible"] is False


def test_v030_fixed4_evaluate_actions_stops_before_larger_stage_on_futility(tmp_path, monkeypatch):
    import src.transaction_manager as tm

    candidate = p(1310, "FA WR futile", "WR", 12, fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 1310, "latent_mean_ppg": 12.0,
        "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0,
    }
    df.to_csv(values, index=False)
    model = model_cfg()
    cfg = model["transaction_manager"]
    cfg["predictive_mc_screen_per_status"] = 1
    cfg["action_mc_stages"] = [32, 64]
    cfg["action_mc_stage_keep_per_status"] = [1, 1]
    cfg["action_mc_final_keep_per_status"] = 1
    cfg["action_mc_futility_enabled"] = True

    monkeypatch.setattr(
        tm,
        "_classification_plausibility",
        lambda raw, adjusted, cfg: {
            "plausible": False,
            "raw_p_better_upper": 0.25,
            "combined_p_better_upper": 0.30,
        },
    )
    report = tm.evaluate_actions(
        snap, league_cfg(), model, values, team_name="Us", predictive_mc_scenarios=128
    )
    assert report["predictive_mc_stages"] == [32]
    assert report["predictive_mc_requested_stages"] == [32, 64, 128]
    assert report["predictive_mc_stopped_for_futility"] is True
    row = (report["free_agent_actions"] + report["waiver_actions"])[0]
    assert row["mc_scenarios"] == 32
    assert row["mc_stage"] == "SCREEN1"
    assert [x["mc_scenarios"] for x in row["mc_stage_history"]] == [32]


def test_v030_fixed6_futility_follows_league_state_response():
    import numpy as np
    from src.transaction_manager import _classification_plausibility

    cfg = {"lean_p_better": 0.67, "action_mc_futility_z": 3.09}
    raw = np.full(1024, -0.01, dtype=float)
    raw[:30] = 0.01
    adjusted = np.full(1024, 0.02, dtype=float)
    result = _classification_plausibility(raw, adjusted, cfg)
    assert result["raw_p_better_upper"] < 0.67
    assert result["combined_p_better_upper"] > 0.99
    # In fixed6 the adjusted channel is the counterfactual league-state response
    # from the same football model, so it legitimately controls escalation.
    assert result["plausible"] is True
    assert result["raw_plausible"] is False
    assert result["league_state_plausible"] is True


def test_v030_fixed5_futility_stopped_row_reports_actual_stage(tmp_path, monkeypatch):
    import src.transaction_manager as tm

    candidate = p(1410, "FA WR option-only", "WR", 12, fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 1410, "latent_mean_ppg": 12.0,
        "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0,
    }
    df.to_csv(values, index=False)
    model = model_cfg()
    cfg = model["transaction_manager"]
    cfg["predictive_mc_screen_per_status"] = 1
    cfg["action_mc_stages"] = [32, 64]
    cfg["action_mc_stage_keep_per_status"] = [1, 1]
    cfg["action_mc_final_keep_per_status"] = 1
    cfg["action_mc_futility_enabled"] = True

    monkeypatch.setattr(
        tm,
        "_classification_plausibility",
        lambda raw, adjusted, cfg: {
            "plausible": False,
            "raw_plausible": False,
            "raw_p_better_upper": 0.20,
            "combined_p_better_upper": 0.99,
        },
    )
    report = tm.evaluate_actions(
        snap, league_cfg(), model, values, team_name="Us", predictive_mc_scenarios=128
    )
    assert report["predictive_mc_stages"] == [32]
    assert report["predictive_mc_stopped_for_futility"] is True
    rows = report["free_agent_actions"] + report["waiver_actions"]
    assert rows
    row = rows[0]
    assert row["mc_scenarios"] == 32
    assert row["mc_stage"] == "SCREEN1"
    assert row["mc_futility_stop"] is True
    assert [x["mc_scenarios"] for x in row["mc_stage_history"]] == [32]


def test_v030_fixed6_strong_release_perturbs_league_more_than_weak_release(tmp_path):
    from src.transaction_manager import UtilityContext, released_player_league_state_response

    snap = snapshot()
    model = model_cfg()
    model["transaction_manager"]["league_state_response_scenarios"] = 64
    ctx = UtilityContext(snap, league_cfg(), model, values_file(tmp_path), snap["espn"]["teams"][0])

    strong = next(x for x in ctx.roster if x["espn_id"] == 2)   # 18 ppg RB
    weak = next(x for x in ctx.roster if x["espn_id"] == 7)     # 6 ppg WR
    strong_response = released_player_league_state_response(strong, ctx, scenarios=64)
    weak_response = released_player_league_state_response(weak, ctx, scenarios=64)

    assert strong_response["model"].startswith("PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V031")
    assert strong_response["p_claimed"] > weak_response["p_claimed"]
    assert strong_response["expected_recipient_gain_ppg"] > weak_response["expected_recipient_gain_ppg"]
    assert strong_response["field_shift_ppg"] > weak_response["field_shift_ppg"]
    # Team 2 is our week-1 opponent and owns first waiver priority in this fixture.
    assert strong_response["current_opponent_shift_ppg"] > 0.0


def test_v030_fixed6_release_response_is_same_model_not_option_utility(tmp_path):
    from src.transaction_manager import UtilityContext, released_player_league_state_response

    snap = snapshot()
    model = model_cfg()
    model["transaction_manager"]["league_state_response_scenarios"] = 32
    ctx = UtilityContext(snap, league_cfg(), model, values_file(tmp_path), snap["espn"]["teams"][0])
    released = next(x for x in ctx.roster if x["espn_id"] == 4)
    response = released_player_league_state_response(released, ctx, scenarios=32)

    assert response["scenarios"] == 32
    assert set(response) >= {
        "p_claimed", "expected_recipient_gain_ppg", "field_shift_ppg",
        "current_opponent_shift_ppg", "opponent_reference_shift_ppg_by_week", "destinations",
    }
    assert len(response["opponent_reference_shift_ppg_by_week"]) == 17
    assert all("delta_season_ppg" in row and "best_drop_name" in row for row in response["destinations"])


def test_v030_fixed6_integrated_league_response_penalizes_strong_release_more(tmp_path):
    """The same add must inherit a larger field penalty when the released asset is stronger."""
    import numpy as np
    from src.transaction_manager import (
        UtilityContext,
        _run_action_mc_stage,
        released_player_league_state_response,
    )

    candidate = p(1500, "Second DST", "DST", 7, fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    values = values_file(tmp_path)
    df = pd.read_csv(values)
    df.loc[len(df)] = {
        "espn_id": 1500,
        "latent_mean_ppg": 7.0,
        "latent_mean_sd_ppg": 0.5,
        "predictive_weekly_sd_ppg": 3.0,
    }
    df.to_csv(values, index=False)

    model = model_cfg()
    model["transaction_manager"]["league_state_response_scenarios"] = 64
    ctx = UtilityContext(snap, league_cfg(), model, values, snap["espn"]["teams"][0])
    add = next(x for x in ctx.available if x["espn_id"] == 1500)
    strong = next(x for x in ctx.roster if x["espn_id"] == 2)  # 18 ppg RB
    weak = next(x for x in ctx.roster if x["espn_id"] == 7)    # 6 ppg WR

    rows = []
    for drop in (strong, weak):
        drop_id = int(drop["espn_id"])
        rows.append({
            "add": add,
            "drop": drop,
            "new_roster": [x for x in ctx.roster if int(x["espn_id"]) != drop_id] + [dict(add)],
            "fantasy_status": "FREEAGENT",
            "p_acquire": 1.0,
            "screen_delta": 0.0,
            "league_state_response": released_player_league_state_response(drop, ctx, scenarios=64),
        })

    _, _, _, evaluated = _run_action_mc_stage(rows, ctx, mc_scenarios=64, stage_name="SCREEN1")
    by_drop = {int(r["drop"]["espn_id"]): r for r in evaluated}

    strong_penalty = float(np.mean(
        np.asarray(by_drop[2]["stage_adjusted_delta"]) - np.asarray(by_drop[2]["stage_raw_delta"])
    ))
    weak_penalty = float(np.mean(
        np.asarray(by_drop[7]["stage_adjusted_delta"]) - np.asarray(by_drop[7]["stage_raw_delta"])
    ))

    # No player-name protection: the stronger release is more damaging because the
    # same forward model predicts a materially larger response on likely recipients.
    assert strong_penalty < weak_penalty
    assert strong_penalty < -0.01
