from pathlib import Path


def _source() -> str:
    return Path("src/gui/season_app.py").read_text(encoding="utf-8")


def test_mc_click_handler_acknowledges_synchronously_then_backgrounds_async_work():
    source = _source()
    handler = source.split("def request_selected_mc()", 1)[1].split("async def recompute_dashboard", 1)[0]
    assert "MC REQUEST RECEIVED" in handler
    assert "background_tasks.create(apply_mc_size(new_n))" in handler
    assert "run_mc_button.disable()" in handler
    assert "mc_select.disable()" in handler
    assert "run_mc_button.on_click(request_selected_mc)" in source


def test_mc_controls_are_not_silently_disabled_by_model_progress():
    source = _source()
    block = source.split("def set_mc_controls(disabled: bool)", 1)[1].split("def update_mc_status", 1)[0]
    assert "controls = [sync_button" in block
    assert "mc_select, run_mc_button" not in block


def test_mc_request_has_persistent_gui_exception_surface():
    source = _source()
    assert "ui.on_exception(surface_ui_exception)" in source
    assert "GUI event error:" in source


def test_mc_context_reset_has_visible_pre_mc_phase():
    source = _source()
    apply_block = source.split("async def apply_mc_size(new_n: int)", 1)[1].split("def request_selected_mc", 1)[0]
    assert "Resetting predictive MC streams and clearing predictive caches" in apply_block
    assert "await asyncio.sleep(0)" in apply_block
    assert "MC CONTEXT READY" in apply_block
