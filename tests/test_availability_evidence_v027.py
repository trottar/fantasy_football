from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.availability_timing import availability_state_model
from src.weekly_manager import optimize_lineup


def _model() -> dict:
    return {
        "weekly_manager": {
            "status_active_probability": {
                "ACTIVE": 0.995,
                "QUESTIONABLE": 0.75,
                "DOUBTFUL": 0.15,
                "OUT": 0.0,
            },
            "status_full_given_active": {
                "ACTIVE": 0.97,
                "QUESTIONABLE": 0.65,
                "DOUBTFUL": 0.40,
            },
            "limited_workload_fraction": {"WR": 0.65, "DEFAULT": 0.65},
            "availability_evidence_likelihood_ratios": {
                "practice": {
                    "NFL_OFFICIAL": {
                        "DNP": {"active": 0.50, "full": 0.35},
                        "LIMITED": {"active": 1.00, "full": 0.65},
                        "FULL": {"active": 2.00, "full": 3.00},
                    },
                    "SLEEPER": {
                        "DNP": {"active": 0.70, "full": 0.55},
                        "LIMITED": {"active": 0.95, "full": 0.75},
                        "FULL": {"active": 1.50, "full": 2.00},
                    },
                },
                "practice_trend": {
                    "IMPROVING": {"active": 1.40, "full": 1.50},
                    "WORSENING": {"active": 0.75, "full": 0.65},
                    "STABLE_DNP": {"active": 0.60, "full": 0.60},
                    "STABLE_LIMITED": {"active": 0.95, "full": 0.80},
                    "STABLE_FULL": {"active": 1.10, "full": 1.25},
                    "MIXED": {"active": 1.00, "full": 1.00},
                },
            },
        }
    }


def _q_player() -> dict:
    return {
        "espn_id": 1,
        "name": "Questionable WR",
        "position": "WR",
        "nfl_team": "ABC",
        "injury_status": "QUESTIONABLE",
    }


def _posterior(prior: float, lr: float) -> float:
    odds = prior / (1.0 - prior)
    odds *= lr
    return odds / (1.0 + odds)


def test_v027_status_only_is_exact_backward_compatible_prior():
    state = availability_state_model(_q_player(), _model())
    assert state.p_active == pytest.approx(0.75)
    assert state.p_full_given_active == pytest.approx(0.65)
    assert state.base_p_active == pytest.approx(0.75)
    assert state.base_p_full_given_active == pytest.approx(0.65)
    assert state.evidence_level == "STATUS_ONLY"
    assert state.posterior_method == "STATUS_PRIOR_FALLBACK"


def test_v027_improving_official_practice_updates_both_posteriors():
    player = _q_player()
    player["official_practice"] = {
        "Wednesday": "DNP",
        "Thursday": "Limited Participation",
        "Friday": "Full Participation",
    }
    state = availability_state_model(player, _model(), hours_to_kickoff=42.0)
    expected_active = _posterior(0.75, 2.00 * 1.40)
    expected_full = _posterior(0.65, 3.00 * 1.50)
    assert state.p_active == pytest.approx(expected_active)
    assert state.p_full_given_active == pytest.approx(expected_full)
    assert state.evidence_level == "OFFICIAL_PRACTICE"
    assert state.practice_source == "NFL_OFFICIAL"
    assert state.practice_sequence == ("DNP", "LIMITED", "FULL")
    assert state.hours_to_kickoff == pytest.approx(42.0)
    assert state.calibration_status == "UNCALIBRATED_LIKELIHOOD_PRIORS"
    used = [e for e in state.evidence if e.used]
    assert {e.kind for e in used} == {"PRACTICE_LATEST", "PRACTICE_TREND"}


def test_v027_persistent_dnp_moves_active_and_full_down():
    player = _q_player()
    player["official_practice"] = {"Wed": "DNP", "Thu": "DNP", "Fri": "DNP"}
    state = availability_state_model(player, _model())
    assert state.p_active == pytest.approx(_posterior(0.75, 0.50 * 0.60))
    assert state.p_full_given_active == pytest.approx(_posterior(0.65, 0.35 * 0.60))
    assert state.p_active < state.base_p_active
    assert state.p_full_given_active < state.base_p_full_given_active


def test_v027_official_practice_supersedes_sleeper_instead_of_double_counting():
    player = _q_player()
    player["official_practice"] = {"Fri": "Full"}
    player["sleeper_practice_participation"] = "DNP"
    state = availability_state_model(player, _model())
    assert state.practice_source == "NFL_OFFICIAL"
    assert state.practice_sequence == ("FULL",)
    assert state.p_active == pytest.approx(_posterior(0.75, 2.0))
    assert state.p_full_given_active == pytest.approx(_posterior(0.65, 3.0))


def test_v027_sleeper_practice_is_used_when_official_is_absent():
    player = _q_player()
    player["sleeper_practice_participation"] = "Limited Participation"
    state = availability_state_model(player, _model())
    assert state.practice_source == "SLEEPER"
    assert state.evidence_level == "SLEEPER_PRACTICE"
    assert state.p_active == pytest.approx(_posterior(0.75, 0.95))
    assert state.p_full_given_active == pytest.approx(_posterior(0.65, 0.75))


def test_v027_hard_out_remains_zero_even_with_full_practice():
    player = _q_player()
    player["injury_status"] = "OUT"
    player["official_practice"] = {"Fri": "Full"}
    state = availability_state_model(player, _model())
    assert state.p_active == 0.0
    assert state.p_full == 0.0
    assert state.p_limited == 0.0
    assert state.p_out == 1.0
    assert state.evidence_level == "HARD_UNAVAILABLE"
    assert state.posterior_method == "HARD_CONSTRAINT"


def test_v027_state_probabilities_close_exactly():
    player = _q_player()
    player["official_practice"] = {"Wed": "DNP", "Fri": "Limited"}
    state = availability_state_model(player, _model())
    assert state.p_full + state.p_limited == pytest.approx(state.p_active)
    assert state.p_full + state.p_limited + state.p_out == pytest.approx(1.0)


def test_v027_lineup_optimizer_respects_evidence_conditioned_active_probability():
    league = {"roster": {"QB": 0, "RB": 0, "WR": 1, "TE": 0, "FLEX": 0, "K": 0, "DST": 0}}
    model = _model()
    # A has the higher raw projection but a low posterior; B should win on expected yield.
    roster = [
        {
            **_q_player(),
            "espn_id": 1,
            "name": "A",
            "projection_points": 20.0,
            "active_probability": 0.30,
            "expected_workload_given_active": 1.0,
        },
        {
            **_q_player(),
            "espn_id": 2,
            "name": "B",
            "projection_points": 12.0,
            "active_probability": 0.90,
            "expected_workload_given_active": 1.0,
        },
    ]
    result = optimize_lineup(roster, league, model, use_expected_availability=True)
    assert result.rows[0]["name"] == "B"
    assert result.rows[0]["active_probability"] == pytest.approx(0.90)


def test_v027_distribution_config_defaults_to_16384_mc():
    model = json.loads(Path("config/model.json").read_text(encoding="utf-8"))
    assert model["transaction_manager"]["predictive_mc_scenarios"] == 16384
    assert 16384 in model["transaction_manager"]["gui_mc_options"]


def test_v027_utility_context_uses_current_week_evidence_posterior(tmp_path: Path):
    from test_availability_timing_v026 import _context

    ctx = _context(tmp_path)
    ctx.model["weekly_manager"]["availability_evidence_likelihood_ratios"] = _model()["weekly_manager"]["availability_evidence_likelihood_ratios"]
    late = next(p for p in ctx.roster if int(p["espn_id"]) == 2)
    late["official_practice"] = {"Wed": "DNP", "Thu": "Limited", "Fri": "Full"}
    ctx._availability_state_cache.clear()
    ctx._yield_state_cache.clear()

    state = ctx.availability_state(late, 1)
    yield_state = ctx.yield_state(late, 1)
    assert state.evidence_level == "OFFICIAL_PRACTICE"
    assert state.p_active > state.base_p_active
    assert yield_state.availability_probability == pytest.approx(state.p_active)


def test_v027_player_diagnostic_and_chat_report_expose_evidence(tmp_path: Path):
    from test_season_gui_service_v024 import _build_runtime

    service = _build_runtime(tmp_path)
    roster = service.roster_players()
    pid = int(roster[0]["espn_id"])
    diag = service.player_diagnostic(pid)
    assert "availability_evidence_level" in diag
    assert "availability_posterior_method" in diag
    assert "availability_calibration_status" in diag
    assert isinstance(diag.get("availability_evidence"), list)

    report = service.generate_chat_report()
    assert " ev=" in report["text"]
    assert report["payload"]["pipeline_symmetry"]["availability_builder"] == "availability_state_model:v0.27-evidence"


def test_v027_gui_player_diagnostics_contains_availability_posterior_panel():
    source = Path("src/gui/season_app.py").read_text(encoding="utf-8")
    assert "Availability posterior" in source
    assert "availability_evidence_level" in source
    assert "availability_calibration_status" in source
