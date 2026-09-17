from pathlib import Path


def test_season_gui_waits_for_browser_connection_before_initial_mc():
    source = Path('src/gui/season_app.py').read_text(encoding='utf-8')
    assert '@ui.page("/")' in source
    assert 'await client.connected()' in source
    assert "await refresh_dashboard(False)" in source
    assert 'ui.timer(0.1, refresh_dashboard, once=True)' not in source


def test_season_gui_progress_no_longer_depends_on_ui_timer():
    source = Path('src/gui/season_app.py').read_text(encoding='utf-8')
    assert 'async def progress_pump()' in source
    assert 'asyncio.create_task(progress_pump())' in source
    assert 'await asyncio.sleep(0.15)' in source
    assert 'ui.timer(0.2, update_mc_status)' not in source


def test_season_gui_has_persistent_recompute_and_refresh_failure_state():
    source = Path('src/gui/season_app.py').read_text(encoding='utf-8')
    assert 'Recompute Dashboard' in source
    assert "mc_state['error'] = f'GUI refresh failed: {exc}'" in source
    assert 'recompute_button.on_click(recompute_dashboard)' in source
