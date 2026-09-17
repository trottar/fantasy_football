from pathlib import Path

import numpy as np
import pytest

from src.gui.season_service import SeasonGuiError
from src.transaction_manager import evaluate_roster_predictive
from test_season_gui_service_v024 import _build_runtime


def test_gui_service_mc_override_resizes_streams_and_clears_caches(tmp_path: Path):
    service = _build_runtime(tmp_path)
    service.dashboard_state()
    assert service._baseline_cache is not None

    assert service.set_mc_scenarios(128) == 128
    assert service.mc_scenarios == 128
    assert service.ctx is not None
    assert service.ctx.predictive_scenarios == 128
    assert service._baseline_cache is None
    assert service._idealized_active_baseline_cache is None
    assert service._idealized_baseline_cache is None

    with pytest.raises(SeasonGuiError):
        service.set_mc_scenarios(64)


def test_mc_batch_size_does_not_change_predictive_universes(tmp_path: Path):
    service = _build_runtime(tmp_path)
    assert service.ctx is not None
    ctx = service.ctx

    ctx.cfg["mc_progress_batch_size"] = 3
    result_a, utility_a, weekly_a = evaluate_roster_predictive(ctx.roster, ctx)

    ctx.cfg["mc_progress_batch_size"] = 7
    result_b, utility_b, weekly_b = evaluate_roster_predictive(ctx.roster, ctx)

    np.testing.assert_array_equal(weekly_a, weekly_b)
    np.testing.assert_array_equal(utility_a, utility_b)
    assert result_a.expected_h2h_win_probability == pytest.approx(result_b.expected_h2h_win_probability)


def test_predictive_progress_is_monotonic_and_completes(tmp_path: Path):
    service = _build_runtime(tmp_path)
    assert service.ctx is not None
    ctx = service.ctx
    ctx.cfg["mc_progress_batch_size"] = 3
    events: list[tuple[int, int, str]] = []

    evaluate_roster_predictive(
        ctx.roster,
        ctx,
        progress_callback=lambda done, total, phase: events.append((done, total, phase)),
        progress_label="test",
    )

    assert events
    totals = {total for _, total, _ in events}
    assert len(totals) == 1
    total = totals.pop()
    dones = [done for done, _, _ in events]
    assert dones == sorted(dones)
    assert dones[-1] == total
    assert any("week" in phase for _, _, phase in events)


def test_gui_source_exposes_large_mc_status_and_selector():
    source = Path("src/gui/season_app.py").read_text(encoding="utf-8")
    assert "MC universes" in source
    assert "MONTE CARLO RUNNING" in source
    assert "scenario-week work units" in source
    assert "mc_progress" in source
    assert "Run selected MC" in source
    assert "run_mc_button.on_click(request_selected_mc)" in source


def test_mc_resize_is_lazy_and_dashboard_progress_includes_opponent_reference(tmp_path: Path):
    service = _build_runtime(tmp_path)
    assert service.ctx is not None
    ctx = service.ctx
    assert ctx._opponent_predictive is None

    # Resizing N must not perform the hidden whole-league opponent simulation.
    assert service.set_mc_scenarios(128) == 128
    assert service.ctx is ctx
    assert ctx._opponent_predictive is None

    events: list[tuple[int, int, str]] = []
    dashboard = service.dashboard_state(
        progress_callback=lambda done, total, phase: events.append((done, total, phase))
    )
    assert dashboard["mc_scenarios"] == 128
    assert ctx._opponent_predictive is not None
    assert events
    assert any("opponent reference" in phase for _, _, phase in events)
    totals = {total for _, total, _ in events}
    assert len(totals) == 1
    dones = [done for done, _, _ in events]
    assert dones == sorted(dones)
    assert dones[-1] == next(iter(totals))


def test_gui_source_reports_context_reset_and_eta():
    source = Path("src/gui/season_app.py").read_text(encoding="utf-8")
    assert "Resetting predictive MC streams" in source
    assert "context reset" in source
    assert "ETA" in source
