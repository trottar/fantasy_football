from pathlib import Path

from test_season_gui_service_v024 import _build_runtime


def test_same_n_mc_reset_rebuilds_context_and_clears_predictive_caches(tmp_path: Path):
    service = _build_runtime(tmp_path)
    # The shared test runtime intentionally uses N=16 for speed; promote it to
    # the GUI's valid minimum before exercising the public resize method.
    assert service.set_mc_scenarios(128) == 128
    service.dashboard_state()
    assert service._baseline_cache is not None
    old_ctx = service.ctx
    n = service.mc_scenarios

    assert service.set_mc_scenarios(n) == n
    assert service.ctx is old_ctx
    assert service.ctx._opponent_predictive is None
    assert service._baseline_cache is None
    assert service._idealized_active_baseline_cache is None
    assert service._idealized_baseline_cache is None


def test_gui_mc_selection_uses_explicit_run_button_not_auto_select_callback():
    source = Path('src/gui/season_app.py').read_text(encoding='utf-8')
    assert "Run selected MC" in source
    assert "run_mc_button.on_click(request_selected_mc)" in source
    assert "await io_call(service.set_mc_scenarios, int(new_n))" in source
    assert "await refresh_dashboard(False)" in source
    assert "mc_select.on_value_change(change_mc_size)" not in source
    assert "options=[f\"{n:,}\" for n in mc_option_values]" in source


def test_recompute_dashboard_invalidates_same_n_context_before_refresh():
    source = Path('src/gui/season_app.py').read_text(encoding='utf-8')
    recompute = source.split('async def recompute_dashboard()', 1)[1].split('chat_report_button.on_click', 1)[0]
    assert "await io_call(service.set_mc_scenarios, service.mc_scenarios)" in recompute
    assert "await refresh_dashboard(False)" in recompute
