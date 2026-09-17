from pathlib import Path

import numpy as np

from test_season_gui_service_v024 import _build_runtime


def test_resize_preserves_static_context_and_resets_only_n_dependent_streams(tmp_path: Path):
    service = _build_runtime(tmp_path)
    assert service.ctx is not None
    ctx = service.ctx

    # Populate N-dependent arrays and the lazy opponent reference.
    pid = int(ctx.roster[0]["espn_id"])
    old_uniforms = ctx.predictive_uniforms(pid)
    old_opponent = ctx.opponent_predictive
    old_roster = ctx.roster
    old_availability = ctx.availability_state(ctx.roster[0], ctx.week)

    assert old_uniforms.shape[0] == 16
    assert old_opponent.shape[0] == 16

    service.set_mc_scenarios(128)

    assert service.ctx is ctx
    assert ctx.roster is old_roster
    assert ctx.availability_state(ctx.roster[0], ctx.week) is old_availability
    assert ctx._opponent_predictive is None
    assert ctx._predictive_uniforms == {}
    assert ctx._workload_uniforms == {}
    assert ctx._epistemic_normals == {}
    assert ctx._game_normals == {}
    assert ctx._kinematic_normals == {}

    new_uniforms = ctx.predictive_uniforms(pid)
    assert new_uniforms.shape[0] == 128
    np.testing.assert_array_equal(new_uniforms[:16], old_uniforms)


def test_opponent_reference_reuses_actual_opponent_simulation(tmp_path: Path, monkeypatch):
    service = _build_runtime(tmp_path)
    assert service.ctx is not None
    ctx = service.ctx

    import src.transaction_manager as tm

    original = tm._simulate_predictive_weekly_points
    calls: list[int] = []

    def wrapped(roster, *args, **kwargs):
        calls.append(int(roster[0]["espn_id"]))
        return original(roster, *args, **kwargs)

    monkeypatch.setattr(tm, "_simulate_predictive_weekly_points", wrapped)
    ctx.ensure_predictive_opponent_reference()

    # The 2-team fixture has exactly one non-user roster. It should be simulated once,
    # not once for the league reference and again for the actual Week 1 opponent.
    assert len(calls) == 1
