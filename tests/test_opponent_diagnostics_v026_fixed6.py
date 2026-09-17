from pathlib import Path

import numpy as np

from test_season_gui_service_v024 import _build_runtime


def test_chat_report_exposes_symmetric_opponent_diagnostics(tmp_path: Path):
    service = _build_runtime(tmp_path)
    report = service.generate_chat_report()
    payload = report["payload"]
    text = report["text"]

    assert payload["pipeline_symmetry"]["shared"] is True
    assert payload["pipeline_symmetry"]["yield_builder"] == "build_weekly_yield_state"
    assert len(payload["opponent_lineup"]) == 9
    assert "OPPONENT LINEUP" in text
    assert "PREDICTION PIPELINE SYMMETRY" in text
    assert "shared=YES" in text
    assert "OPPONENT KEY UNCERTAINTY" in text

    for row in payload["opponent_lineup"]:
        assert row["mean"] is not None
        assert row["sd"] is not None
        assert row["k"] is not None
        assert row["interaction_factor"] is not None
        assert "interaction_delta_ppg" in row
        assert row["p_active"] is not None
        assert row["p_full_given_active"] is not None
        assert "pre_matchup" in row
        assert "matchup_model" in row
        assert "espn_anchor_kind" in row


def test_opponent_random_streams_are_released_after_reference_build(tmp_path: Path):
    service = _build_runtime(tmp_path)
    assert service.ctx is not None
    ctx = service.ctx
    opponent_id = next(tid for tid in ctx.all_team_rosters if tid != ctx.team_id)
    opponent_pids = {
        int(p["espn_id"])
        for p in ctx.all_team_rosters[opponent_id]
        if p.get("espn_id") is not None
    }

    # Prove stream regeneration is bitwise deterministic before relying on release.
    pid = next(iter(opponent_pids))
    original = ctx.game_normals(pid).copy()
    ctx.release_predictive_streams([pid])
    np.testing.assert_array_equal(ctx.game_normals(pid), original)
    ctx.release_predictive_streams([pid])

    ctx.ensure_predictive_opponent_reference()
    caches = (
        ctx._predictive_uniforms,
        ctx._workload_uniforms,
        ctx._epistemic_normals,
        ctx._game_normals,
        ctx._kinematic_normals,
        ctx._interaction_normals,
    )
    for cache in caches:
        assert opponent_pids.isdisjoint(cache)


def test_opponent_gui_summary_surfaces_availability_and_matchup():
    source = Path("src/gui/season_app.py").read_text(encoding="utf-8")
    assert "A={100*p_active:.0f}%" in source
    assert "F|A={100*p_full_active:.0f}%" in source
    assert "vs {matchup}" in source
