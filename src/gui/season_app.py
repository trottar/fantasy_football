from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

try:
    from ..observability.gui_shadow import create_gui_shadow_recorder
except Exception:
    create_gui_shadow_recorder = None

from .season_service import CANONICAL_SLOTS, AVAILABILITY_MODES, SeasonGuiError, SeasonGuiService
from .season_visualizations import (
    action_delta_options,
    action_week_overlay_options,
    closure_residual_options,
    component_bar_options,
    distribution_overlay_options,
    lineup_lab_distribution_options,
    margin_distribution_options,
    matchup_slot_delta_options,
    model_espn_scatter_options,
    player_prediction_options,
    uncertainty_breakdown_options,
)


def _set_echart_options(chart: Any, options: dict[str, Any]) -> None:
    """Replace NiceGUI EChart options without assigning to its read-only property."""
    chart.options.clear()
    chart.options.update(options)
    chart.update()


def run_season_gui(
    *,
    snapshot_path: str = "data/season_snapshots/latest.json",
    league_path: str = "config/league.json",
    model_path: str = "config/model.json",
    values_path: str = "data/processed/player_values_2026.csv",
    secrets_path: str | None = None,
    snapshots_dir: str = "data/season_snapshots",
    team_name: str | None = None,
    team_id: int | None = None,
    port: int = 8080,
    native: bool = False,
    mc_scenarios: int | None = None,
) -> None:
    try:
        from nicegui import Client, background_tasks, run, ui
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "NiceGUI is not installed. Run: python -m pip install -r requirements.txt"
        ) from exc

    try:
        service = SeasonGuiService(
            snapshot_path=snapshot_path,
            league_path=league_path,
            model_path=model_path,
            values_path=values_path,
            secrets_path=secrets_path,
            snapshots_dir=snapshots_dir,
            team_name=team_name,
            team_id=team_id,
            mc_scenarios=mc_scenarios,
        )
    except SeasonGuiError as exc:
        raise RuntimeError(str(exc)) from None

    gui_shadow = None
    if create_gui_shadow_recorder is not None:
        try:
            gui_shadow = create_gui_shadow_recorder()
        except Exception:
            gui_shadow = None

    @ui.page("/")
    async def season_page(client: Client) -> None:
        page_shadow = None
        if gui_shadow is not None:
            try:
                shadow_page = gui_shadow.open_page()
                client.on_connect(
                    lambda _client=None, shadow=shadow_page:
                    shadow.client_connect()
                )
                client.on_disconnect(
                    lambda _client=None, shadow=shadow_page:
                    shadow.client_disconnect()
                )
                client.on_delete(
                    lambda _client=None, shadow=shadow_page:
                    shadow.page_unmount()
                )
                page_shadow = shadow_page
            except Exception:
                page_shadow = None

        def observe_task(name: str, awaitable):
            if page_shadow is None:
                return awaitable
            try:
                return page_shadow.observe_background_task(name, awaitable)
            except Exception:
                return awaitable

        ui.colors(primary="#3b82f6", secondary="#64748b", accent="#22c55e")
        ui.dark_mode().enable()
        ui.add_css('''
            body { background: #0f172a; }
            .season-card { background: #111827; border: 1px solid #334155; border-radius: 10px; }
            .metric { font-size: 1.65rem; font-weight: 700; line-height: 1.1; }
            .metric-small { font-size: 1.25rem; font-weight: 700; }
            .subtle { color: #94a3b8; }
            .good { color: #4ade80; }
            .warn { color: #fbbf24; }
            .bad { color: #f87171; }
            .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
            .lineup-row { border-bottom: 1px solid #1f2937; min-height: 38px; }
        ''')

        dashboard_cache: dict[str, Any] = {}
        roster_cache: list[dict[str, Any]] = []
        available_cache: list[dict[str, Any]] = []
        player_options: dict[int, str] = {}
        lineup_selection: dict[str, int] = {}
        availability_modes: dict[int, str] = {}
        limited_fraction = 0.65
        busy_jobs = 0
        last_action_result: dict[str, Any] | None = None
        last_trade_result: dict[str, Any] | None = None
        lineup_input_controls: list[Any] = []
        mc_state: dict[str, Any] = {
            "running": False, "label": "", "phase": "", "done": 0, "total": 1,
            "started": None, "elapsed": 0.0, "error": None, "completed_at": None,
            "request_pending": False,
        }

        with ui.header().classes('items-center justify-between bg-slate-950 px-4 py-2'):
            with ui.row().classes('items-center gap-3'):
                ui.label('Hail to Pitt · Season Control Room').classes('text-xl font-semibold')
                version_label = ui.label('v0.31').classes('subtle text-sm')
            with ui.row().classes('items-center gap-2'):
                snapshot_label = ui.label('').classes('subtle text-sm mono')
                # Keep the browser-side select values as plain strings. NiceGUI/Quasar
                # choice elements normalize dictionary/numeric keys internally, which made the
                # old auto-change callback unreliable in the local GUI. Selection is now a
                # deliberate two-step operation: choose N, then press Run selected MC.
                mc_option_values = sorted(set(service.mc_options + [service.mc_scenarios]))
                mc_select = ui.select(
                    options=[f"{n:,}" for n in mc_option_values],
                    value=f"{service.mc_scenarios:,}",
                    label='MC universes',
                ).props('outlined dense').classes('w-[150px]')
                run_mc_button = ui.button('Run selected MC', icon='play_arrow', color='primary').props('dense')
                sync_spinner = ui.spinner(size='sm')
                sync_spinner.visible = False
                chat_report_button = ui.button('Chat Diagnosis', icon='summarize', color='secondary')
                sync_button = ui.button('Refresh Data', icon='sync')

        with ui.column().classes('w-full max-w-[1900px] mx-auto p-3 gap-3'):
            with ui.card().classes('season-card p-3 w-full') as mc_status_card:
                with ui.row().classes('w-full items-center gap-3'):
                    mc_run_spinner = ui.spinner(size='md')
                    mc_run_spinner.visible = False
                    mc_status_label = ui.label(f"Waiting for browser connection · MC N={service.mc_scenarios:,}").classes('font-semibold')
                    mc_elapsed_label = ui.label('').classes('subtle mono text-sm ml-auto')
                    recompute_button = ui.button('Recompute Dashboard', icon='refresh', color='secondary').props('dense')
                mc_progress = ui.linear_progress(value=0.0).props('instant-feedback').classes('w-full')
                mc_phase_label = ui.label('Initial UI loaded; waiting for the browser connection before starting MC.').classes('subtle mono text-xs')

            with ui.row().classes('w-full gap-3 flex-wrap'):
                team_card = ui.card().classes('season-card p-3 min-w-[240px]')
                win_card = ui.card().classes('season-card p-3 min-w-[180px]')
                score_card = ui.card().classes('season-card p-3 min-w-[240px]')
                opponent_card = ui.card().classes('season-card p-3 min-w-[240px]')
                waiver_card = ui.card().classes('season-card p-3 min-w-[180px]')
                health_card = ui.card().classes('season-card p-3 flex-1 min-w-[380px]')

            with ui.tabs().classes('w-full') as tabs:
                tab_matchup = ui.tab('Weekly matchup', icon='sports_football')
                tab_lab = ui.tab('Lineup laboratory', icon='science')
                tab_players = ui.tab('Player diagnostics', icon='query_stats')
                tab_actions = ui.tab('Player market', icon='swap_horiz')
                tab_specialists = ui.tab('Specialists', icon='shield')
                tab_trades = ui.tab('Trades', icon='handshake')
                tab_closure = ui.tab('Data / MC', icon='monitoring')

            with ui.tab_panels(tabs, value=tab_matchup).classes('w-full bg-transparent'):
                with ui.tab_panel(tab_matchup).classes('p-0'):
                    with ui.row().classes('w-full gap-3 items-stretch'):
                        with ui.card().classes('season-card p-3 flex-1 min-w-[500px]'):
                            ui.label('Planning lineup').classes('text-lg font-semibold')
                            ui.label('Planning lineup uses P(active) and expected workload; game-day substitutions are evaluated by the lock-aware policy.').classes('subtle text-sm')
                            planning_container = ui.column().classes('w-full gap-0 mt-2')
                        with ui.card().classes('season-card p-3 flex-1 min-w-[500px]'):
                            ui.label('Opponent reference').classes('text-lg font-semibold')
                            opponent_summary = ui.column().classes('w-full gap-2')
                            opponent_roster_container = ui.column().classes('w-full gap-0 mt-2')
                    with ui.row().classes('w-full gap-3 items-stretch'):
                        with ui.card().classes('season-card p-3 flex-1 min-w-[560px]'):
                            score_dist_chart = ui.echart({}).classes('w-full h-[330px]')
                        with ui.card().classes('season-card p-3 flex-1 min-w-[560px]'):
                            margin_chart = ui.echart({}).classes('w-full h-[330px]')
                    with ui.card().classes('season-card p-3 w-full'):
                        ui.label('Where the matchup edge comes from').classes('text-lg font-semibold')
                        ui.label('Conditional pregame starter projections by slot; policy MC separately applies availability states and kickoff locks.').classes('subtle text-sm')
                        matchup_driver_chart = ui.echart({}).classes('w-full h-[300px]')

                with ui.tab_panel(tab_lab).classes('p-0'):
                    with ui.row().classes('w-full gap-3 items-start'):
                        with ui.card().classes('season-card p-3 w-[560px] min-w-[480px]'):
                            ui.label('Hypothetical lineup').classes('text-lg font-semibold')
                            ui.label('Local only. No ESPN lineup changes are submitted.').classes('subtle text-sm')
                            lineup_controls = ui.column().classes('w-full gap-2 mt-2')
                            ui.separator()
                            with ui.row().classes('w-full items-center gap-3'):
                                ui.label('Limited workload fraction').classes('text-sm')
                                limited_slider = ui.slider(min=0.25, max=0.95, step=0.05, value=0.65).classes('flex-1')
                                limited_label = ui.label('65%').classes('mono text-sm')
                            reset_lineup_button = ui.button('Reset to default fixed lineup', icon='restart_alt', color='secondary').classes('w-full')
                        with ui.column().classes('flex-1 min-w-[600px] gap-3'):
                            with ui.row().classes('w-full gap-3 flex-wrap'):
                                lab_win_card = ui.card().classes('season-card p-3 min-w-[180px]')
                                lab_fixed_card = ui.card().classes('season-card p-3 min-w-[180px]')
                                lab_policy_card = ui.card().classes('season-card p-3 min-w-[180px]')
                                lab_idealized_card = ui.card().classes('season-card p-3 min-w-[180px]')
                                lab_delta_card = ui.card().classes('season-card p-3 min-w-[190px]')
                                lab_contingency_card = ui.card().classes('season-card p-3 min-w-[200px]')
                                lab_timing_card = ui.card().classes('season-card p-3 min-w-[190px]')
                                lab_score_card = ui.card().classes('season-card p-3 min-w-[220px]')
                            with ui.card().classes('season-card p-3 w-full'):
                                lab_status_card = ui.column().classes('w-full gap-1')
                            with ui.card().classes('season-card p-3 w-full'):
                                lab_score_chart = ui.echart({}).classes('w-full h-[320px]')
                            with ui.card().classes('season-card p-3 w-full'):
                                lab_margin_chart = ui.echart({}).classes('w-full h-[280px]')
                            with ui.card().classes('season-card p-3 w-full'):
                                ui.label('Selected lineup vs default fixed lineup').classes('text-lg font-semibold')
                                ui.label('This compares fixed selections. The realistic policy can substitute only with information available before each relevant game lock.').classes('subtle text-sm')
                                lab_compare_container = ui.column().classes('w-full mt-2')

                with ui.tab_panel(tab_players).classes('p-0'):
                    with ui.row().classes('w-full gap-3 items-start'):
                        with ui.card().classes('season-card p-3 w-[420px] min-w-[360px]'):
                            ui.label('Player selector').classes('text-lg font-semibold')
                            player_select = ui.select(options={}, with_input=True, label='Roster / opponent / available').props('outlined clearable').classes('w-full')
                            diag_summary = ui.column().classes('w-full gap-1 mt-3')
                        with ui.column().classes('flex-1 min-w-[700px] gap-3'):
                            diag_bridge_cards = ui.row().classes('w-full gap-3 flex-wrap')
                            with ui.row().classes('w-full gap-3 items-stretch'):
                                with ui.card().classes('season-card p-3 flex-1 min-w-[420px]'):
                                    player_chain_chart = ui.echart({}).classes('w-full h-[300px]')
                                with ui.card().classes('season-card p-3 flex-1 min-w-[420px]'):
                                    player_uncertainty_chart = ui.echart({}).classes('w-full h-[300px]')
                            with ui.card().classes('season-card p-3 w-full'):
                                player_component_chart = ui.echart({}).classes('w-full h-[320px]')
                            with ui.card().classes('season-card p-3 w-full'):
                                ui.label('Matchup / uncertainty detail').classes('text-lg font-semibold')
                                diag_detail = ui.column().classes('w-full gap-1')

                with ui.tab_panel(tab_actions).classes('p-0'):
                    with ui.row().classes('w-full gap-3 items-start'):
                        with ui.card().classes('season-card p-3 w-[470px] min-w-[420px]'):
                            ui.label('ADD / DROP experiment').classes('text-lg font-semibold')
                            ui.label('Paired MC uses the same model universes as HOLD. No ESPN transaction is submitted.').classes('subtle text-sm')
                            add_select = ui.select(options={}, with_input=True, label='Add available player').props('outlined clearable').classes('w-full mt-2')
                            drop_select = ui.select(options={}, with_input=True, label='Drop roster player').props('outlined clearable').classes('w-full')
                            evaluate_action_button = ui.button('Evaluate paired MC', icon='analytics').classes('w-full')
                            action_spinner = ui.spinner(size='md')
                            action_spinner.visible = False
                            action_error = ui.label('').classes('bad text-sm')
                        with ui.column().classes('flex-1 min-w-[650px] gap-3'):
                            action_metrics = ui.row().classes('w-full gap-3 flex-wrap')
                            with ui.row().classes('w-full gap-3 items-stretch'):
                                with ui.card().classes('season-card p-3 flex-1 min-w-[500px]'):
                                    action_chart = ui.echart({}).classes('w-full h-[300px]')
                                with ui.card().classes('season-card p-3 flex-1 min-w-[500px]'):
                                    action_week_chart = ui.echart({}).classes('w-full h-[300px]')
                            with ui.card().classes('season-card p-3 w-full'):
                                ui.label('Candidate yield / acquisition layer').classes('text-lg font-semibold')
                                action_detail = ui.column().classes('w-full gap-1')
                    with ui.card().classes('season-card p-3 w-full mt-3'):
                        with ui.row().classes('w-full justify-between items-center gap-2'):
                            ui.label('Available ESPN pool').classes('text-lg font-semibold')
                            pool_filter = ui.input(placeholder='Filter player / team / position').props('outlined dense').classes('w-[360px]')
                        available_table_container = ui.column().classes('w-full mt-2')

                with ui.tab_panel(tab_specialists).classes('p-0'):
                    with ui.row().classes('w-full gap-3 items-start'):
                        with ui.card().classes('season-card p-3 flex-1 min-w-[520px]'):
                            ui.label('Defense channel').classes('text-lg font-semibold')
                            ui.label('D/ST is compared only to D/ST. Two-defense carry value is matchup/bye rotation synergy; any bench-slot cost comes from the player channel.').classes('subtle text-sm')
                            defense_channel_button = ui.button('Evaluate defense channel', icon='shield').classes('w-full mt-2')
                            defense_channel_container = ui.column().classes('w-full mt-3 gap-1')
                        with ui.card().classes('season-card p-3 flex-1 min-w-[520px]'):
                            ui.label('Kicker channel').classes('text-lg font-semibold')
                            ui.label('K is compared only to K. Streaming uses weekly scoring environment and matchup context; carrying a second kicker is disabled by default.').classes('subtle text-sm')
                            kicker_channel_button = ui.button('Evaluate kicker channel', icon='sports_score').classes('w-full mt-2')
                            kicker_channel_container = ui.column().classes('w-full mt-3 gap-1')

                with ui.tab_panel(tab_trades).classes('p-0'):
                    with ui.row().classes('w-full gap-3 items-start'):
                        with ui.card().classes('season-card p-3 w-[520px] min-w-[460px]'):
                            ui.label('Trade laboratory').classes('text-lg font-semibold')
                            ui.label('Evaluate both rosters with the shared predictive model. Partner acceptance/counter/reject is a separate provisional behavior layer. No ESPN trade is submitted.').classes('subtle text-sm')
                            trade_partner_select = ui.select(options={}, with_input=True, label='Trade partner').props('outlined clearable').classes('w-full mt-2')
                            trade_give_select = ui.select(options={}, multiple=True, with_input=True, label='Give (up to 2)').props('outlined use-chips').classes('w-full')
                            trade_receive_select = ui.select(options={}, multiple=True, with_input=True, label='Receive (up to 2)').props('outlined use-chips').classes('w-full')
                            evaluate_trade_button = ui.button('Evaluate trade MC', icon='analytics').classes('w-full')
                            trade_search_button = ui.button('Screen one-for-one offers', icon='manage_search', color='secondary').classes('w-full')
                            trade_error = ui.label('').classes('bad text-sm')
                        with ui.column().classes('flex-1 min-w-[700px] gap-3'):
                            trade_metrics = ui.row().classes('w-full gap-3 flex-wrap')
                            with ui.card().classes('season-card p-3 w-full'):
                                ui.label('Trade interpretation').classes('text-lg font-semibold')
                                trade_detail = ui.column().classes('w-full gap-1 mt-1')
                            with ui.card().classes('season-card p-3 w-full'):
                                ui.label('League-wide one-for-one search').classes('text-lg font-semibold')
                                ui.label('Search-stage MC is candidate generation. Re-evaluate a selected offer at the full GUI MC count before acting.').classes('subtle text-sm')
                                trade_search_container = ui.column().classes('w-full mt-2')

                with ui.tab_panel(tab_closure).classes('p-0'):
                    closure_metrics = ui.row().classes('w-full gap-3 flex-wrap')
                    with ui.row().classes('w-full gap-3 items-stretch'):
                        with ui.card().classes('season-card p-3 flex-1 min-w-[520px]'):
                            closure_scatter_chart = ui.echart({}).classes('w-full h-[330px]')
                        with ui.card().classes('season-card p-3 flex-1 min-w-[520px]'):
                            closure_residual_chart = ui.echart({}).classes('w-full h-[330px]')
                    with ui.card().classes('season-card p-3 w-full'):
                        ui.label('Prediction ledger / data-MC closure').classes('text-lg font-semibold')
                        ui.label('Current-week rows remain a pregame model-vs-ESPN diagnostic. v0.29 prospective postgame closure is accumulated separately from immutable pregame captures.').classes('subtle text-sm')
                        closure_table_container = ui.column().classes('w-full mt-2')
                    with ui.card().classes('season-card p-3 w-full mt-3'):
                        with ui.row().classes('w-full justify-between items-center gap-3'):
                            with ui.column().classes('gap-0'):
                                ui.label('Prospective component closure').classes('text-lg font-semibold')
                                ui.label('Capture the exact pregame GUI/service state before kickoff; after games run closure-update to ingest nflverse observations. Positive ΔRMSE means the v0.28 interaction correction improved prospective closure.').classes('subtle text-sm')
                            closure_capture_button = ui.button('Capture Pregame State', icon='save').props('outline')
                        closure_capture_status = ui.label('No capture written in this GUI session.').classes('mono subtle text-xs')
                        component_closure_container = ui.column().classes('w-full mt-2')

        with ui.dialog() as chat_report_dialog, ui.card().classes('w-[1050px] max-w-[95vw] p-4'):
            ui.label('Chat diagnosis').classes('text-xl font-semibold')
            ui.label('Paste this compressed model-state report into the analysis chat. The same report is saved locally as TXT + JSON.').classes('subtle text-sm')
            chat_report_path_label = ui.label('').classes('mono subtle text-xs')
            chat_report_textarea = ui.textarea(label='Compressed diagnosis').props('outlined readonly autogrow').classes('w-full mono')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Close', on_click=chat_report_dialog.close, color='secondary')

        async def io_call(func, *args, **kwargs):
            nonlocal busy_jobs
            busy_jobs += 1
            try:
                return await run.io_bound(func, *args, **kwargs)
            finally:
                busy_jobs -= 1

        def set_mc_controls(disabled: bool) -> None:
            # Keep the MC selector/run button event-capable while a model job is running.
            # Their own request handler gives an explicit "already running" message instead
            # of leaving the controls silently disabled. This also avoids stale disabled-state
            # propagation after a long initial page calculation.
            controls = [sync_button, chat_report_button, recompute_button, reset_lineup_button,
                        evaluate_action_button, limited_slider, add_select, drop_select,
                        evaluate_trade_button, trade_search_button, trade_partner_select,
                        defense_channel_button, kicker_channel_button,
                        trade_give_select, trade_receive_select]
            controls.extend(lineup_input_controls)
            for control in controls:
                try:
                    control.disable() if disabled else control.enable()
                except Exception:
                    pass

        def update_mc_status() -> None:
            running = bool(mc_state.get('running'))
            if running:
                started = mc_state.get('started')
                elapsed = max(0.0, time.monotonic() - float(started)) if started is not None else 0.0
                mc_state['elapsed'] = elapsed
                total = max(1, int(mc_state.get('total') or 1))
                done = min(total, max(0, int(mc_state.get('done') or 0)))
                frac = done / total
                mc_run_spinner.visible = True
                mc_status_label.set_text(f"MONTE CARLO RUNNING — {mc_state.get('label') or 'model evaluation'}")
                eta_text = ''
                if done > 0 and total > done and elapsed > 0:
                    rate = done / elapsed
                    if rate > 0:
                        eta = (total - done) / rate
                        eta_text = f" · ETA {eta:.1f}s"
                mc_elapsed_label.set_text(f"elapsed {elapsed:.1f}s{eta_text} · N={service.mc_scenarios:,}")
                mc_progress.set_value(frac)
                mc_phase_label.set_text(
                    f"{100*frac:5.1f}% · {mc_state.get('phase') or 'initializing'} · "
                    f"{done:,}/{total:,} scenario-week work units"
                )
            else:
                mc_run_spinner.visible = False
                error = mc_state.get('error')
                if error:
                    mc_status_label.set_text('MONTE CARLO FAILED')
                    mc_phase_label.set_text(str(error))
                    mc_elapsed_label.set_text(f"N={service.mc_scenarios:,}")
                else:
                    elapsed = float(mc_state.get('elapsed') or 0.0)
                    suffix = f" · last run {elapsed:.1f}s" if mc_state.get('completed_at') else ''
                    mc_status_label.set_text(f"MC ready · {service.mc_scenarios:,} universes{suffix}")
                    mc_phase_label.set_text('Results are complete and controls are unlocked.')
                    mc_elapsed_label.set_text('')
                    mc_progress.set_value(1.0)

        async def mc_call(label: str, func, *args, **kwargs):
            nonlocal busy_jobs
            if mc_state.get('running'):
                raise SeasonGuiError(f"Monte Carlo already running: {mc_state.get('label')}")
            mc_state.update({
                'running': True, 'label': str(label), 'phase': 'initializing', 'done': 0, 'total': 1,
                'started': time.monotonic(), 'elapsed': 0.0, 'error': None, 'completed_at': None,
            })
            set_mc_controls(True)
            update_mc_status()

            def progress(done: int, total: int, phase: str) -> None:
                # Worker-thread callback: mutate state only. UI updates stay on the page event loop.
                mc_state['done'] = int(done)
                mc_state['total'] = max(1, int(total))
                mc_state['phase'] = str(phase)

            async def progress_pump() -> None:
                async def _progress_pump_observed_body():
                    while mc_state.get('running'):
                        update_mc_status()
                        await asyncio.sleep(0.15)

                return await observe_task('season.mc_progress_pump', _progress_pump_observed_body())
            pump_task = asyncio.create_task(progress_pump())
            busy_jobs += 1
            try:
                result = await run.io_bound(func, *args, progress_callback=progress, **kwargs)
                mc_state['done'] = int(mc_state.get('total') or 1)
                mc_state['phase'] = 'complete'
                return result
            except Exception as exc:
                mc_state['error'] = str(exc)
                raise
            finally:
                busy_jobs -= 1
                started = mc_state.get('started')
                mc_state['elapsed'] = max(0.0, time.monotonic() - float(started)) if started is not None else 0.0
                mc_state['running'] = False
                mc_state['completed_at'] = time.time()
                pump_task.cancel()
                try:
                    await pump_task
                except asyncio.CancelledError:
                    pass
                set_mc_controls(False)
                update_mc_status()

        def metric_card(card, label: str, value: str, sub: str = '', cls: str = '') -> None:
            card.clear()
            with card:
                ui.label(label).classes('subtle text-xs uppercase')
                ui.label(value).classes(f'metric {cls}')
                if sub:
                    ui.label(sub).classes('subtle text-sm')

        def render_health(rows: list[dict[str, str]]) -> None:
            health_card.clear()
            with health_card:
                ui.label('Data sources').classes('subtle text-xs uppercase')
                with ui.row().classes('gap-x-4 gap-y-1 flex-wrap'):
                    for row in rows:
                        cls = 'good' if row['status'] == 'OK' else 'warn'
                        ui.label(f"{row['source']}: {row['status']}").classes(f'text-sm {cls}')

        def render_lineup(container, rows: list[dict[str, Any]]) -> None:
            container.clear()
            with container:
                for row in rows:
                    with ui.row().classes('w-full lineup-row items-center gap-2'):
                        ui.label(str(row['slot'])).classes('w-[44px] mono text-sm subtle')
                        ui.label(str(row['name'])).classes('w-[210px] font-medium')
                        ui.label(f"{row.get('team') or '-'} vs {row.get('opponent') or '-'}").classes('w-[110px] subtle text-sm')
                        ui.label(f"{float(row['mean']):.2f} ± {float(row['sd']):.2f}").classes('w-[115px] mono text-sm')
                        ui.label(f"K={float(row['k']):.3f}").classes('w-[72px] mono text-sm')
                        ui.label(f"I={float(row.get('interaction_factor') or 1.0):.3f}").classes('w-[72px] mono text-sm')
                        p = float(row['p_active'])
                        cls = 'good' if p >= .95 else 'warn' if p >= .5 else 'bad'
                        ui.label(f"A={p:.0%}").classes(f'w-[58px] mono text-sm {cls}')
                        ui.label(f"F|A={float(row.get('p_full_given_active') or 0):.0%}").classes('w-[72px] mono subtle text-sm')
                        ui.label(str(row.get('lock_group') or 'UNKNOWN')).classes('w-[92px] mono subtle text-xs')

        def render_opponent_roster(rows: list[dict[str, Any]]) -> None:
            opponent_roster_container.clear()
            with opponent_roster_container:
                for row in rows:
                    with ui.column().classes('w-full lineup-row gap-0 py-1'):
                        with ui.row().classes('w-full items-center gap-2'):
                            ui.label(str(row.get('slot') or row.get('position') or '?')).classes('w-[46px] mono subtle')
                            ui.label(str(row.get('name'))).classes('w-[220px]')
                            ui.label(f"{float(row.get('mean') or 0):.2f} ± {float(row.get('sd') or 0):.2f}").classes('mono text-sm')
                            ui.label(f"K={float(row.get('k') or 1):.3f}").classes('mono subtle text-sm')
                            ui.label(f"I={float(row.get('interaction_factor') or 1.0):.3f}").classes('mono subtle text-sm')
                        p_active = float(row.get('p_active') or 0.0)
                        p_full_active = float(row.get('p_full_given_active') or 0.0)
                        matchup = str(row.get('opponent') or '-')
                        status = str(row.get('status') or '-')
                        ui.label(
                            f"vs {matchup} · A={100*p_active:.0f}% · F|A={100*p_full_active:.0f}% · {status} · {row.get('lock_group') or 'UNKNOWN'}"
                        ).classes('subtle mono text-xs ml-[54px]')

        async def refresh_dashboard(reload_service: bool = False) -> None:
            nonlocal dashboard_cache, roster_cache, available_cache, player_options, lineup_selection, availability_modes, last_action_result, last_trade_result
            try:
                if reload_service:
                    await io_call(service.reload)
                dashboard_cache = await mc_call('Dashboard / policy MC', service.dashboard_state)
                roster_cache = await io_call(service.roster_players)
                opponent_rows = await io_call(service.opponent_players)
                available_cache = await io_call(service.available_players)
                lineup_selection = await io_call(service.default_lineup_selection)
                last_action_result = None
                last_trade_result = None
                availability_modes = {int(r['espn_id']): 'MODEL' for r in roster_cache}
                snapshot_label.set_text(str(dashboard_cache.get('snapshot_utc') or 'snapshot unknown'))
                metric_card(team_card, f"Week {dashboard_cache['week']}", str(dashboard_cache['team_name']), f"Season {dashboard_cache['season']}")
                fixed_win = dashboard_cache.get('fixed_planning_win_probability')
                contingency = dashboard_cache.get('realistic_backup_policy_value')
                idealized_active = dashboard_cache.get('idealized_active_policy_win_probability')
                idealized = dashboard_cache.get('idealized_policy_win_probability')
                status_timing = dashboard_cache.get('status_timing_inflation')
                workload_info = dashboard_cache.get('workload_information_inflation')
                win_sub = 'realistic lock-aware MC'
                if fixed_win is not None and contingency is not None:
                    win_sub += f" · fixed {100*float(fixed_win):.1f}% · backup {100*float(contingency):+.1f} pp"
                if idealized_active is not None and status_timing is not None:
                    win_sub += f" · ideal-active {100*float(idealized_active):.1f}% · status timing {100*float(status_timing):+.1f} pp"
                if idealized is not None and workload_info is not None:
                    win_sub += f" · ideal-full {100*float(idealized):.1f}% · workload info {100*float(workload_info):+.1f} pp"
                metric_card(win_card, 'Projected win', f"{100*float(dashboard_cache['weekly_win_probability']):.1f}%", win_sub)
                metric_card(score_card, 'Our score', f"{dashboard_cache['user_week']['mean']:.1f} ± {dashboard_cache['user_week']['sd']:.1f}", f"lock-aware MC N={int(dashboard_cache.get('mc_scenarios') or service.mc_scenarios):,} · p10–p90 {dashboard_cache['user_week']['p10']:.1f}–{dashboard_cache['user_week']['p90']:.1f}")
                metric_card(opponent_card, str(dashboard_cache['opponent_name']), f"{dashboard_cache['opponent_week']['mean']:.1f} ± {dashboard_cache['opponent_week']['sd']:.1f}", 'opponent predictive MC')
                metric_card(waiver_card, 'Waiver rank', str(dashboard_cache.get('waiver_rank') or '-'), 'provisional acquisition model')
                render_health(dashboard_cache['source_health'])
                render_lineup(planning_container, dashboard_cache['planning_lineup'])
                opponent_summary.clear()
                with opponent_summary:
                    ui.label(f"Mean {dashboard_cache['opponent_week']['mean']:.2f} · SD {dashboard_cache['opponent_week']['sd']:.2f}").classes('metric-small')
                    ui.label(f"Matchup margin mean {dashboard_cache['margin']['mean']:+.2f} points").classes('subtle text-sm')
                render_opponent_roster(dashboard_cache.get('opponent_planning_lineup') or [])
                _set_echart_options(score_dist_chart, distribution_overlay_options(dashboard_cache['user_week']['histogram'], dashboard_cache['opponent_week']['histogram']))
                _set_echart_options(margin_chart, margin_distribution_options(dashboard_cache['margin']['histogram']))
                _set_echart_options(matchup_driver_chart, matchup_slot_delta_options(dashboard_cache.get('matchup_slot_deltas') or []))

                all_players = roster_cache + opponent_rows + available_cache
                player_options = {
                    int(r['espn_id']): f"{r['name']} · {r['position']} {r.get('team') or ''} · {r['scope']}"
                    for r in all_players if r.get('espn_id') is not None
                }
                player_select.set_options(player_options)
                player_select.update()
                add_select.set_options({int(r['espn_id']): f"{r['name']} ({r['position']}, {r.get('team') or 'FA'}) · {r.get('fantasy_status') or ''} · {float(r['operational_mean']):.2f}" for r in available_cache if str(r.get('position') or '').upper() in {'QB','RB','WR','TE'}})
                add_select.update()
                drops = await io_call(service.legal_drop_players)
                drop_select.set_options({int(r['espn_id']): f"{r['name']} ({r['position']}) · {float(r['operational_mean']):.2f}" for r in drops})
                drop_select.update()
                partners = await io_call(service.trade_partners)
                trade_partner_select.set_options({int(r['team_id']): str(r['name']) for r in partners})
                trade_partner_select.update()
                trade_give_select.set_options({int(r['espn_id']): f"{r['name']} ({r['position']}) · season {float(r.get('season_ppg') or 0):.2f}" for r in roster_cache if r.get('espn_id') is not None and r.get('droppable') is not False and str(r.get('position') or '').upper() in {'QB','RB','WR','TE'}})
                trade_give_select.update()
                if trade_partner_select.value is not None:
                    try:
                        trade_rows = await io_call(service.trade_partner_players, int(trade_partner_select.value))
                        trade_receive_select.set_options({int(r['espn_id']): f"{r['name']} ({r['position']}) · season {float(r.get('season_ppg') or 0):.2f}" for r in trade_rows if r.get('espn_id') is not None and str(r.get('position') or '').upper() in {'QB','RB','WR','TE'}})
                    except Exception:
                        trade_receive_select.set_options({})
                    trade_receive_select.update()
                render_lineup_controls()
                render_available_table()
                await render_closure()
                await recompute_lab()
            except Exception as exc:
                mc_state['error'] = f'GUI refresh failed: {exc}'
                update_mc_status()
                print(f'GUI refresh failed: {exc}')
                ui.notify(f'GUI refresh failed: {exc}', color='negative', timeout=12000)

        def render_lineup_controls() -> None:
            lineup_controls.clear()
            lineup_input_controls.clear()
            with lineup_controls:
                for slot in CANONICAL_SLOTS:
                    options = service.lineup_options(slot)
                    option_map = {int(r['espn_id']): f"{r['name']} ({r['position']}) · {float(r['operational_mean']):.2f}" for r in options}
                    with ui.row().classes('w-full gap-2 items-center'):
                        ui.label(slot).classes('w-[46px] mono subtle')
                        sel = ui.select(options=option_map, value=lineup_selection.get(slot), with_input=True).props('outlined dense').classes('flex-1')
                        mode = ui.select(options=sorted(AVAILABILITY_MODES), value=availability_modes.get(lineup_selection.get(slot, -1), 'MODEL')).props('outlined dense').classes('w-[115px]')
                        lineup_input_controls.extend([sel, mode])

                        async def on_player(e, slot_name=slot, mode_select=mode):
                            if e.value is None:
                                return
                            lineup_selection[slot_name] = int(e.value)
                            mode_select.value = availability_modes.get(int(e.value), 'MODEL')
                            await recompute_lab()

                        async def on_mode(e, slot_name=slot):
                            pid = lineup_selection.get(slot_name)
                            if pid is not None:
                                availability_modes[int(pid)] = str(e.value)
                                await recompute_lab()

                        sel.on_value_change(on_player)
                        mode.on_value_change(on_mode)

        async def recompute_lab() -> None:
            nonlocal limited_fraction
            if set(lineup_selection) != set(CANONICAL_SLOTS) or mc_state.get('running'):
                return
            try:
                result = await mc_call(
                    'Lineup laboratory MC', service.evaluate_hypothetical_lineup,
                    dict(lineup_selection),
                    availability_modes=dict(availability_modes),
                    limited_fractions={int(pid): limited_fraction for pid in availability_modes},
                )
                selected_win = 100 * float(result['win_probability'])
                fixed_win = 100 * float(result['fixed_baseline_win_probability'])
                policy_win = 100 * float(result['realistic_policy_win_probability'])
                idealized_active_win = 100 * float(result['idealized_active_policy_win_probability'])
                idealized_win = 100 * float(result['idealized_policy_win_probability'])
                delta_fixed_pp = 100 * float(result['delta_vs_fixed_win_probability'])
                contingency_pp = 100 * float(result['realistic_backup_policy_value'])
                status_timing_pp = 100 * float(result['status_timing_inflation'])
                workload_info_pp = 100 * float(result['workload_information_inflation'])
                timing_pp = 100 * float(result['information_timing_inflation'])
                metric_card(lab_win_card, 'Selected fixed lineup', f"{selected_win:.1f}%", 'no substitutions')
                metric_card(lab_fixed_card, 'Default fixed lineup', f"{fixed_win:.1f}%", 'same nine pregame starters')
                metric_card(lab_policy_card, 'Realistic policy', f"{policy_win:.1f}%", 'lock-aware information flow')
                metric_card(lab_idealized_card, 'Idealized policy', f"{idealized_win:.1f}%", f"active-only {idealized_active_win:.1f}% · full state upper bound")
                metric_card(lab_delta_card, 'Δ vs default fixed', f"{delta_fixed_pp:+.2f} pp", 'effect of your lineup/scenario edits', 'good' if delta_fixed_pp > .25 else 'bad' if delta_fixed_pp < -.25 else '')
                metric_card(lab_contingency_card, 'Real backup value', f"{contingency_pp:+.2f} pp", 'realistic − fixed', 'good' if contingency_pp > .25 else '')
                metric_card(lab_timing_card, 'Idealized information', f"{timing_pp:+.2f} pp", f"status timing {status_timing_pp:+.2f} · workload info {workload_info_pp:+.2f}", 'warn' if timing_pp > .25 else '')
                metric_card(lab_score_card, 'Selected score', f"{result['team']['mean']:.1f} ± {result['team']['sd']:.1f}", f"MC={result['mc_scenarios']}")

                lab_status_card.clear()
                with lab_status_card:
                    ui.label('Scenario interpretation').classes('subtle text-xs uppercase')
                    active = [r for r in result['rows'] if r['mode'] != 'MODEL']
                    ui.label('Model availability for all selected players' if not active else ', '.join(f"{r['name']}={r['mode']}" for r in active)).classes('text-sm')
                    ui.label('The top dashboard uses the realistic lock-aware policy; this laboratory evaluates the exact fixed nine-player lineup you selected and shows the idealized upper bound separately.').classes('subtle text-sm')

                _set_echart_options(
                    lab_score_chart,
                    lineup_lab_distribution_options(
                        result['team']['histogram'],
                        result['fixed_baseline_team']['histogram'],
                        result['opponent']['histogram'],
                    ),
                )
                _set_echart_options(lab_margin_chart, margin_distribution_options(result['margin']['histogram'], title='Selected-lineup matchup margin MC'))

                compare_rows = []
                for r in result['changes']:
                    compare_rows.append({
                        'slot': r['slot'],
                        'baseline': r['baseline_name'],
                        'selected': r['selected_name'],
                        'mode': r['mode'],
                        'base_mean': round(float(r['baseline_mean']), 2),
                        'sel_mean': round(float(r['selected_mean']), 2),
                        'delta': round(float(r['delta_mean']), 2),
                        'changed': 'YES' if r['changed'] else '',
                    })
                lab_compare_container.clear()
                with lab_compare_container:
                    columns = [
                        {'name':'slot','label':'Slot','field':'slot','sortable':False},
                        {'name':'baseline','label':'Default fixed','field':'baseline','align':'left'},
                        {'name':'selected','label':'Selected','field':'selected','align':'left'},
                        {'name':'mode','label':'Availability','field':'mode'},
                        {'name':'base_mean','label':'Default MC μ','field':'base_mean'},
                        {'name':'sel_mean','label':'Selected MC μ','field':'sel_mean'},
                        {'name':'delta','label':'Δ pts','field':'delta'},
                        {'name':'changed','label':'Changed','field':'changed'},
                    ]
                    ui.table(columns=columns, rows=compare_rows, row_key='slot', pagination=9).classes('w-full').props('dense hide-pagination')
            except Exception as exc:
                lab_status_card.clear()
                with lab_status_card:
                    ui.label('Invalid hypothetical state').classes('bad font-semibold')
                    ui.label(str(exc)).classes('bad text-sm')

        async def show_player_diagnostic(e) -> None:
            if e.value is None:
                return
            try:
                diag = await io_call(service.player_diagnostic, int(e.value))
            except Exception as exc:
                ui.notify(str(exc), color='negative')
                return
            diag_summary.clear()
            with diag_summary:
                ui.label(str(diag['name'])).classes('text-lg font-semibold')
                ui.label(f"{diag['position']} · {diag.get('team') or '-'} vs {diag.get('opponent') or '-'}").classes('subtle')
                ui.label(f"Operational {float(diag['operational_mean']):.2f} ± {float(diag['total_sd']):.2f}").classes('metric-small')
                ui.label(f"P(active) {float(diag['p_active']):.1%} · P(full|active) {float(diag.get('p_full_given_active') or 0):.1%} · {diag['status']} [{diag['status_source']}]").classes('text-sm')
                ui.label(
                    f"FULL/LIMITED/OUT {float(diag.get('p_full') or 0):.1%}/{float(diag.get('p_limited') or 0):.1%}/{float(diag.get('p_out') or 0):.1%} · evidence {diag.get('availability_evidence_level') or '-'}"
                ).classes('subtle text-sm')

            diag_bridge_cards.clear()
            with diag_bridge_cards:
                cards = [ui.card().classes('season-card p-3 min-w-[180px]') for _ in range(7)]
                model = float(diag.get('model_mean') or 0.0)
                kin = float(diag.get('matchup_model_mean') or model)
                op = float(diag.get('operational_mean') or 0.0)
                espn = diag.get('espn_anchor')
                metric_card(cards[0], 'Base model', f"{model:.2f}", str(diag.get('projection_source') or ''))
                metric_card(cards[1], 'K-adjusted', f"{kin:.2f}", f"ΔK {kin-model:+.2f}")
                metric_card(cards[2], 'ESPN anchor', '-' if espn is None else f"{float(espn):.2f}", str(diag.get('espn_anchor_kind') or 'no anchor'))
                metric_card(cards[3], 'Interaction', f"{float(diag.get('interaction_factor') or 1):.3f}", f"ΔI {float(diag.get('interaction_delta_ppg') or 0):+.2f} · σI {float(diag.get('interaction_sd_ppg') or 0):.2f}")
                metric_card(cards[4], 'Operational', f"{op:.2f}", str(diag.get('interaction_source') or ''))
                metric_card(cards[5], 'K', f"{float(diag['k']):.3f}", f"σK {float(diag['kinematic_sd']):.2f}")
                anchor_z = diag.get('anchor_z')
                metric_card(cards[6], 'Model−ESPN', '-' if diag.get('delta_model_espn') is None else f"{float(diag['delta_model_espn']):+.2f}", 'z -' if anchor_z is None else f"z {float(anchor_z):+.2f}")

            _set_echart_options(player_chain_chart, player_prediction_options(diag))
            _set_echart_options(player_uncertainty_chart, uncertainty_breakdown_options(diag))
            _set_echart_options(player_component_chart, component_bar_options(diag))
            diag_detail.clear()
            with diag_detail:
                with ui.row().classes('gap-6 flex-wrap'):
                    ui.label(f"game/model/K/I SD = {float(diag['game_sd']):.2f}/{float(diag['model_sd']):.2f}/{float(diag['kinematic_sd']):.2f}/{float(diag.get('interaction_sd_ppg') or 0):.2f}").classes('mono')
                    ui.label(f"total predictive SD = {float(diag['total_sd']):.2f}").classes('mono')
                    ui.label(f"ESPN anchor weight = {float(diag.get('anchor_weight') or 0):.2f}").classes('mono')
                    implied = diag.get('team_implied_points')
                    ui.label('team implied points = -' if implied is None else f"team implied points = {float(implied):.1f}").classes('mono')
                ui.label(f"K source: {diag.get('kinematic_source')} · defense-current shrinkage weight {float(diag.get('defense_current_weight') or 0):.3f}").classes('subtle text-sm')
                ui.label(
                    f"Interaction: {diag.get('interaction_source') or '-'} · artifact={diag.get('interaction_artifact_id') or '-'} · "
                    f"baseline={diag.get('interaction_baseline_source') or '-'} · support~{float(diag.get('interaction_support') or 0):.0f}"
                ).classes('subtle text-sm')
                interaction_components = diag.get('interaction_components') or {}
                if interaction_components:
                    for name, item in interaction_components.items():
                        ui.label(
                            f"I[{name}] C={float(item.get('correction') or 1):.3f} ± {float(item.get('correction_sd') or 0):.3f} "
                            f"base={float(item.get('baseline_value') or 0):.3f} → {float(item.get('corrected_value') or 0):.3f} "
                            f"vs {item.get('defense_feature') or '-'} z={float(item.get('defense_z') or 0):+.2f} N~{float(item.get('support') or 0):.0f} "
                            f"{'commissioned' if item.get('commissioned') else 'shadow'}"
                        ).classes('mono text-xs')
                ui.separator()
                ui.label('Availability posterior').classes('subtle text-xs uppercase')
                ui.label(
                    f"prior A/F|A = {float(diag.get('base_p_active') or 0):.1%}/{float(diag.get('base_p_full_given_active') or 0):.1%} → "
                    f"posterior {float(diag.get('p_active') or 0):.1%}/{float(diag.get('p_full_given_active') or 0):.1%}"
                ).classes('mono text-sm')
                sequence = diag.get('practice_sequence') or []
                practice_text = 'none' if not sequence else f"{diag.get('practice_source') or '-'}:" + ' → '.join(str(x) for x in sequence)
                ui.label(
                    f"evidence={diag.get('availability_evidence_level') or '-'} · method={diag.get('availability_posterior_method') or '-'} · practice={practice_text}"
                ).classes('text-sm')
                ui.label(
                    f"calibration={diag.get('availability_calibration_status') or '-'}" + (
                        '' if diag.get('hours_to_kickoff') is None else f" · {float(diag.get('hours_to_kickoff')):.1f} h to kickoff at snapshot"
                    )
                ).classes('warn text-xs' if str(diag.get('availability_calibration_status') or '').startswith('UNCALIBRATED') else 'subtle text-xs')
                for item in diag.get('availability_evidence') or []:
                    used = 'USED' if item.get('used') else 'context'
                    ui.label(
                        f"{used}: {item.get('source')} {item.get('kind')}={item.get('value')} · LR(A)={float(item.get('active_likelihood_ratio') or 1):.2f} LR(F|A)={float(item.get('full_likelihood_ratio') or 1):.2f}"
                    ).classes('mono subtle text-xs')
                ui.separator()
                components = diag.get('kinematic_components') or {}
                zscores = diag.get('kinematic_zscores') or {}
                if components:
                    ranked = sorted(components.items(), key=lambda kv: abs(float(kv[1])), reverse=True)[:6]
                    ui.label('Largest matchup coordinates: ' + ' · '.join(
                        f"{k}={float(v):+.3f}" + (f" (z={float(zscores[k]):+.2f})" if k in zscores else '')
                        for k, v in ranked
                    )).classes('text-sm')
                if diag.get('dst_components'):
                    c = diag['dst_components']
                    ui.label(f"DST components: sacks={float(c.get('sacks_mean') or 0):.2f}, TO={float(c.get('turnovers_mean') or 0):.2f}, PA={float(c.get('points_allowed_mean') or 0):.1f}, YA={float(c.get('yards_allowed_mean') or 0):.0f}").classes('text-sm')

        async def evaluate_action() -> None:
            nonlocal last_action_result
            if add_select.value is None or drop_select.value is None:
                ui.notify('Choose both an add and a drop.', color='warning')
                return
            evaluate_action_button.disable()
            action_spinner.visible = True
            action_error.set_text('')
            try:
                result = await mc_call('Paired add/drop MC', service.evaluate_single_add_drop, int(add_select.value), int(drop_select.value))
                last_action_result = result
                action_metrics.clear()
                with action_metrics:
                    cards = [ui.card().classes('season-card p-3 min-w-[180px]') for _ in range(7)]
                    metric_card(cards[0], 'Direct ΔH2H', f"{100*result['delta_h2h_mean']:+.3f} pp", f"68% mean-CI {100*result['delta_h2h_p16']:+.3f}…{100*result['delta_h2h_p84']:+.3f}")
                    metric_card(cards[1], 'Pdirect(+ / 0 / -)', f"{result['p_better']:.0%}/{result['p_tie']:.0%}/{result['p_worse']:.0%}", result.get('raw_classification', 'UNASSESSED'))
                    metric_card(cards[2], 'P(acquire)', f"{result['p_acquire']:.1%}", result['fantasy_status'])
                    metric_card(cards[3], 'League-state EVΔ', f"{100*result['expected_delta_utility']:+.3f} pp", result['classification'])
                    metric_card(cards[4], 'Season lineup Δ', f"{result['season_ppg_delta']:+.2f}", f"week {result['week_delta']:+.2f}")
                    metric_card(cards[5], 'HOLD week μ', f"{result['baseline_week_distribution']['mean']:.2f}", f"SD {result['baseline_week_distribution']['sd']:.2f}")
                    metric_card(cards[6], 'Action week μ', f"{result['action_week_distribution']['mean']:.2f}", f"SD {result['action_week_distribution']['sd']:.2f}")
                _set_echart_options(action_chart, action_delta_options(result['utility_delta_distribution']['histogram']))
                _set_echart_options(action_week_chart, action_week_overlay_options(result['baseline_week_distribution']['histogram'], result['action_week_distribution']['histogram']))
                action_detail.clear()
                with action_detail:
                    add = result['add']; drop = result['drop']; y = result['candidate_yield']
                    ui.label(f"ADD {add['name']} ({add['position']}, {add.get('team') or 'FA'}) / DROP {drop['name']} ({drop['position']})").classes('font-semibold')
                    model_text = '-' if y.get('model_mean_ppg') is None else f"{float(y['model_mean_ppg']):.2f}"
                    espn_text = '-' if y.get('espn_anchor_ppg') is None else f"{float(y['espn_anchor_ppg']):.2f}"
                    ui.label(f"Yield: operational={float(y['operational_mean_ppg']):.2f}, model={model_text}, ESPN={espn_text}, K={float(y['kinematic_factor_mean']):.3f}, I={float(y.get('interaction_factor_mean') or 1):.3f} ΔI={float(y.get('interaction_delta_ppg') or 0):+.2f}").classes('mono text-sm')
                    ui.label(f"Insurance Δ {result['insurance_delta']:+.2f} · bye-floor Δ {result['bye_floor_delta']:+.2f} · MC={result['mc_scenarios']}").classes('subtle text-sm')
                    rr = result.get('release_response') or {}
                    ui.label(
                        f"Release response: P(claimed) {float(rr.get('p_claimed') or 0):.1%} · "
                        f"recipient gain {float(rr.get('expected_recipient_gain_ppg') or 0):+.2f} ppg · "
                        f"field shift {float(rr.get('field_shift_ppg') or 0):+.2f} ppg · "
                        f"N={int(rr.get('scenarios') or 0)}"
                    ).classes('subtle text-sm')
                    os = result.get('option_scarcity') or {}
                    ui.label(
                        f"Contingent diagnostic only: option-depth Δ {float(os.get('delta_future_option_ppg') or 0):+.2f} ppg · "
                        f"stress-depth Δ {float(os.get('delta_replacement_scarcity_ppg') or 0):+.2f} ppg"
                    ).classes('subtle text-sm')
                    b = result['baseline_utility']; a = result['action_utility']
                    ui.label(f"Absolute season utility: HOLD {100*float(b['expected_h2h_win_probability']):.2f}% → action {100*float(a['expected_h2h_win_probability']):.2f}% if acquired").classes('text-sm')
                    blockers = result.get('waiver_blockers') or []
                    if blockers:
                        ui.label('Higher-priority waiver blockers').classes('font-semibold mt-2')
                        for row in blockers:
                            ui.label(
                                f"#{row.get('waiver_rank')} {row.get('team_name')}: P(claim)={float(row.get('claim_probability') or 0):.1%} · "
                                f"modeled Δseason={float(row.get('delta_season_ppg') or 0):+.2f} · best drop={row.get('best_drop_name') or '-'}"
                            ).classes('mono subtle text-xs')
                    if result['classification'] == 'NO_RESOLVED_EDGE':
                        ui.label('Interpretation: the action does not resolve beyond model/MC uncertainty; HOLD remains the practical baseline.').classes('warn text-sm')
            except Exception as exc:
                action_error.set_text(str(exc))
            finally:
                action_spinner.visible = False
                evaluate_action_button.enable()

        def render_specialist_channel(container, report: dict[str, Any]) -> None:
            container.clear()
            with container:
                base = report.get('baseline') or {}
                owned = ', '.join(str(x.get('name')) for x in report.get('owned') or []) or 'none'
                ui.label(f"Owned: {owned}").classes('font-semibold')
                ui.label(
                    f"L1 static baseline {float(base.get('weighted_mean_ppg') or 0):.2f} pts/week | "
                    f"current {float(base.get('current_week_mean') or 0):.2f} +/- {float(base.get('current_week_sd') or 0):.2f}"
                ).classes('mono text-sm')

                swaps = report.get('swap_actions') or []
                ui.label('L1 static same-channel board').classes('subtle text-xs uppercase mt-2')
                if not swaps:
                    ui.label('No same-channel static candidates.').classes('subtle text-sm')
                for row in swaps[:6]:
                    drop = f" / {row.get('drop_name')}" if row.get('drop_name') else ''
                    ui.label(
                        f"{row.get('add_name')}{drop}: delta={float(row.get('delta_channel_ppg') or 0):+.2f} pts/wk | "
                        f"P+={float(row.get('p_channel_better') or 0):.0%} | W{report.get('week')} {float(row.get('current_week_delta') or 0):+.2f}"
                    ).classes('mono text-sm')

                policy = report.get('one_slot_policy') or {}
                if policy:
                    ui.label('L2 dynamic one-slot policy').classes('subtle text-xs uppercase mt-3')
                    proposal = policy.get('proposal_current_action') or policy.get('current_action') or {'action': 'HOLD'}
                    action = policy.get('recommended_current_action') or {'action': 'HOLD'}
                    action_txt = str(action.get('action') or 'HOLD')
                    if action.get('add'):
                        action_txt += f" {action.get('add')}"
                    if action.get('drop'):
                        action_txt += f" / DROP {action.get('drop')}"
                    complete = policy.get('complete_state_delta') or {}
                    ui.label(
                        f"policy {float(policy.get('weighted_mean_ppg') or 0):.2f} pts/wk | "
                        f"delta static {float(policy.get('delta_vs_static_ppg') or 0):+.2f} | recommendation {action_txt}"
                    ).classes('mono text-sm')
                    ui.label(
                        f"complete-state {100*float(complete.get('mean') or 0):+.2f} pp | "
                        f"P+ {float(complete.get('p_better') or 0):.0%} | {complete.get('classification') or 'UNASSESSED'}"
                    ).classes('mono text-sm')
                    ui.label(
                        f"market={policy.get('market_model') or '-'} | order={policy.get('transaction_order_model') or '-'}"
                    ).classes('subtle text-xs')

                carry = report.get('dynamic_carry_actions') or []
                if carry:
                    ui.label('L3/L4 dynamic second-DST activation + complete-state confirmation').classes('subtle text-xs uppercase mt-3')
                    for row in carry[:5]:
                        rel = row.get('player_slot_release') or {}
                        full = row.get('complete_state_delta') or {}
                        ui.label(
                            f"W{int(row.get('activation_week') or 0)} -> {row.get('add_name') or '-'}: D2-D1 {float(row.get('dynamic_channel_delta_ppg') or 0):+.2f} pts/wk | "
                            f"whole-state {100*float(full.get('mean') or 0):+.2f} pp | "
                            f"release {rel.get('name') or '-'} | {row.get('classification') or 'UNASSESSED'}"
                        ).classes('mono text-sm')

        async def evaluate_defense_channel_gui() -> None:
            try:
                report = await io_call(service.defense_channel, min(service.mc_scenarios, 4096))
                render_specialist_channel(defense_channel_container, report)
            except Exception as exc:
                defense_channel_container.clear()
                with defense_channel_container:
                    ui.label(str(exc)).classes('bad text-sm')

        async def evaluate_kicker_channel_gui() -> None:
            try:
                report = await io_call(service.kicker_channel, min(service.mc_scenarios, 4096))
                render_specialist_channel(kicker_channel_container, report)
            except Exception as exc:
                kicker_channel_container.clear()
                with kicker_channel_container:
                    ui.label(str(exc)).classes('bad text-sm')

        async def load_trade_partner(e) -> None:
            trade_receive_select.value = []
            trade_receive_select.set_options({})
            trade_receive_select.update()
            if e.value is None:
                return
            try:
                rows = await io_call(service.trade_partner_players, int(e.value))
                trade_receive_select.set_options({
                    int(r['espn_id']): f"{r['name']} ({r['position']}) · season {float(r.get('season_ppg') or 0):.2f}"
                    for r in rows if r.get('espn_id') is not None
                })
                trade_receive_select.update()
            except Exception as exc:
                trade_error.set_text(str(exc))

        def _selected_ids(value) -> list[int]:
            if value is None:
                return []
            if isinstance(value, (list, tuple, set)):
                return [int(x) for x in value]
            return [int(value)]

        async def evaluate_trade_offer_gui() -> None:
            nonlocal last_trade_result
            trade_error.set_text('')
            partner_id = trade_partner_select.value
            give_ids = _selected_ids(trade_give_select.value)
            receive_ids = _selected_ids(trade_receive_select.value)
            if partner_id is None or not give_ids or not receive_ids:
                trade_error.set_text('Select a partner plus at least one GIVE and RECEIVE player.')
                return
            if len(give_ids) > 2 or len(receive_ids) > 2:
                trade_error.set_text('v0.31 player trade channel supports at most two players per side.')
                return
            try:
                result = await mc_call(
                    'Trade paired MC', service.evaluate_trade_offer,
                    int(partner_id), give_ids, receive_ids, mc_scenarios=service.mc_scenarios,
                )
                last_trade_result = result
                trade_metrics.clear()
                with trade_metrics:
                    cards = [ui.card().classes('season-card p-3 min-w-[185px]') for _ in range(6)]
                    u = result['user']['delta_season_ppg']; p = result['partner']['delta_season_ppg']; r = result['response']
                    metric_card(cards[0], 'Our season Δ', f"{float(u['mean']):+.3f} ppg", f"P(better) {float(u['p_better']):.1%}")
                    metric_card(cards[1], 'Partner season Δ', f"{float(p['mean']):+.3f} ppg", f"P(better) {float(p['p_better']):.1%}")
                    metric_card(cards[2], 'P(accept)', f"{float(r['p_accept']):.1%}", r['model'])
                    metric_card(cards[3], 'P(counter)', f"{float(r['p_counter']):.1%}", 'provisional behavior')
                    metric_card(cards[4], 'P(reject)', f"{float(r['p_reject']):.1%}", 'provisional behavior')
                    metric_card(cards[5], 'Offer EV', f"{float(result['expected_offer_value']):+.3f}", result['classification'])
                trade_detail.clear()
                with trade_detail:
                    give_names = ', '.join(str(x.get('name')) for x in result.get('give') or [])
                    receive_names = ', '.join(str(x.get('name')) for x in result.get('receive') or [])
                    ui.label(f"GIVE {give_names} / RECEIVE {receive_names}").classes('font-semibold')
                    ui.label(
                        f"Our current-week Δ {float(result['user']['delta_current_week']['mean']):+.2f} · "
                        f"partner current-week Δ {float(result['partner']['delta_current_week']['mean']):+.2f} · "
                        f"partner market Δ {float(result['partner']['market_delta']):+.2f}"
                    ).classes('mono text-sm')
                    if result.get('user_auto_drops'):
                        ui.label('Our modeled post-trade release: ' + ', '.join(str(x.get('name')) for x in result['user_auto_drops'])).classes('warn text-sm')
                    if result.get('partner_auto_drops'):
                        ui.label('Partner modeled post-trade release: ' + ', '.join(str(x.get('name')) for x in result['partner_auto_drops'])).classes('warn text-sm')
                    if result.get('user_auto_adds'):
                        ui.label('Our modeled post-trade FA fill: ' + ', '.join(str(x.get('name')) for x in result['user_auto_adds'])).classes('good text-sm')
                    if result.get('partner_auto_adds'):
                        ui.label('Partner modeled post-trade FA fill: ' + ', '.join(str(x.get('name')) for x in result['partner_auto_adds'])).classes('good text-sm')
                    ui.label('Trade valuation and partner response are intentionally separate. Acceptance probabilities are uncalibrated until this league generates trade behavior.').classes('subtle text-sm')
            except Exception as exc:
                trade_error.set_text(str(exc))

        async def screen_trade_offers_gui() -> None:
            trade_error.set_text('')
            trade_search_button.disable()
            try:
                rows = await io_call(service.trade_search_screen, 20)
                trade_search_container.clear()
                with trade_search_container:
                    if not rows:
                        ui.label('No one-for-one screen candidates passed the current filter.').classes('subtle text-sm')
                    else:
                        table_rows = [{
                            'partner': r.get('partner_name'),
                            'give': r.get('give_name'),
                            'receive': r.get('receive_name'),
                            'our_screen': round(float(r.get('user_screen_gain_ppg') or 0), 2),
                            'partner_screen': round(float(r.get('partner_screen_gain_ppg') or 0), 2),
                            'partner_id': r.get('partner_team_id'),
                            'give_id': r.get('give_id'),
                            'receive_id': r.get('receive_id'),
                        } for r in rows]
                        columns = [
                            {'name':'partner','label':'Partner','field':'partner','align':'left'},
                            {'name':'give','label':'Give','field':'give','align':'left'},
                            {'name':'receive','label':'Receive','field':'receive','align':'left'},
                            {'name':'our_screen','label':'Our screen Δ','field':'our_screen','sortable':True},
                            {'name':'partner_screen','label':'Partner screen Δ','field':'partner_screen','sortable':True},
                            {'name':'partner_id','label':'Team ID','field':'partner_id'},
                            {'name':'give_id','label':'Give ID','field':'give_id'},
                            {'name':'receive_id','label':'Receive ID','field':'receive_id'},
                        ]
                        ui.table(columns=columns, rows=table_rows, row_key='receive_id', pagination=20).classes('w-full').props('dense')
            except Exception as exc:
                trade_error.set_text(str(exc))
            finally:
                trade_search_button.enable()

        def render_available_table() -> None:
            text = str(pool_filter.value or '').casefold().strip()
            rows = []
            for r in available_cache:
                blob = f"{r['name']} {r['position']} {r.get('team') or ''} {r.get('fantasy_status') or ''}".casefold()
                if text and text not in blob:
                    continue
                rows.append({
                    'name': r['name'], 'pos': r['position'], 'team': r.get('team'), 'status': r.get('fantasy_status'),
                    'mean': round(float(r.get('operational_mean') or 0), 2), 'sd': round(float(r.get('predictive_sd') or 0), 2),
                    'espn': None if r.get('espn_anchor') is None else round(float(r['espn_anchor']), 2),
                    'k': round(float(r.get('k') or 1), 3), 'opp': r.get('opponent'), 'adds24h': r.get('adds24h'),
                })
                if len(rows) >= 200:
                    break
            columns = [
                {'name':'name','label':'Player','field':'name','sortable':True,'align':'left'},
                {'name':'pos','label':'Pos','field':'pos','sortable':True},
                {'name':'team','label':'Team','field':'team','sortable':True},
                {'name':'status','label':'ESPN','field':'status','sortable':True},
                {'name':'mean','label':'Our μ','field':'mean','sortable':True},
                {'name':'sd','label':'σ','field':'sd','sortable':True},
                {'name':'espn','label':'ESPN proj','field':'espn','sortable':True},
                {'name':'k','label':'K','field':'k','sortable':True},
                {'name':'opp','label':'Opp','field':'opp','sortable':True},
                {'name':'adds24h','label':'Adds 24h','field':'adds24h','sortable':True},
            ]
            available_table_container.clear()
            with available_table_container:
                ui.table(columns=columns, rows=rows, row_key='name', pagination=25).classes('w-full').props('dense')
                if len(rows) >= 200:
                    ui.label('Showing first 200 matching players; use the filter to narrow the pool.').classes('subtle text-xs')

        async def render_closure() -> None:
            rows = await io_call(service.prediction_ledger)
            summary = await io_call(service.prediction_ledger_summary)
            prospective = await io_call(service.prospective_closure_summary)
            component_rows = await io_call(service.component_closure_summary_rows)
            table_rows = []
            for r in rows:
                table_rows.append({
                    'name': r['name'], 'pos': r['position'],
                    'data': None if r['observed'] is None else round(float(r['observed']), 2),
                    'mc': None if r['operational'] is None else round(float(r['operational']), 2),
                    'base_mc': None if r.get('base_mc') is None else round(float(r['base_mc']), 2),
                    'delta_i': None if r.get('interaction_delta_ppg') is None else round(float(r['interaction_delta_ppg']), 2),
                    'model': None if r['model'] is None else round(float(r['model']), 2),
                    'espn': None if r['espn'] is None else round(float(r['espn']), 2),
                    'ratio': None if r['data_over_mc'] is None else round(float(r['data_over_mc']), 3),
                    'model_espn': None if r['model_minus_espn'] is None else round(float(r['model_minus_espn']), 2),
                    'k': round(float(r['k']), 3),
                })

            closure_metrics.clear()
            with closure_metrics:
                cards = [ui.card().classes('season-card p-3 min-w-[190px]') for _ in range(8)]
                metric_card(cards[0], 'Roster predictions', str(summary['players']), f"ESPN anchors {summary['anchor_coverage']}")
                ma = summary.get('mean_abs_model_minus_espn')
                metric_card(cards[1], 'Mean |model−ESPN|', '-' if ma is None else f"{float(ma):.2f} pts", 'current pregame external-anchor check')
                fantasy = prospective.get('fantasy') or {}
                metric_card(cards[2], 'Prospective observations', str(fantasy.get('n', 0)), ', '.join(prospective.get('weeks') or []) or 'run closure-update after games')
                prmse = fantasy.get('rmse')
                metric_card(cards[3], 'Prospective RMSE', '-' if prmse is None else f"{float(prmse):.2f} pts", 'observed vs interaction-corrected MC')
                pimp = fantasy.get('interaction_rmse_improvement')
                metric_card(cards[4], 'Interaction ΔRMSE', '-' if pimp is None else f"{float(pimp):+.2f} pts", 'base-MC RMSE minus corrected-MC RMSE')
                pulls = prospective.get('pull') or {}
                pull_text = '-' if pulls.get('mean') is None else f"{float(pulls.get('mean')):+.2f} / {float(pulls.get('sd') or 0):.2f}"
                metric_card(cards[5], 'Pull μ / σ', pull_text, f"n={pulls.get('n',0)}; target ~0 / 1")
                availability = prospective.get('availability') or {}
                brier = availability.get('brier')
                metric_card(cards[6], 'Availability Brier', '-' if brier is None else f"{float(brier):.3f}", f"explicit truth n={availability.get('n',0)}")
                mx = summary.get('max_abs_model_minus_espn')
                metric_card(cards[7], 'Max |model−ESPN|', '-' if mx is None else f"{float(mx):.2f} pts", 'current diagnostic outlier scale')

            _set_echart_options(closure_scatter_chart, model_espn_scatter_options(rows))
            _set_echart_options(closure_residual_chart, closure_residual_options(rows))

            columns = [
                {'name':'name','label':'Player','field':'name','sortable':True,'align':'left'},
                {'name':'pos','label':'Pos','field':'pos','sortable':True},
                {'name':'data','label':'Observed data','field':'data','sortable':True},
                {'name':'mc','label':'Corrected MC','field':'mc','sortable':True},
                {'name':'base_mc','label':'Base MC','field':'base_mc','sortable':True},
                {'name':'delta_i','label':'Δ interaction','field':'delta_i','sortable':True},
                {'name':'model','label':'Base model','field':'model','sortable':True},
                {'name':'espn','label':'ESPN anchor','field':'espn','sortable':True},
                {'name':'ratio','label':'Data/MC','field':'ratio','sortable':True},
                {'name':'model_espn','label':'Model−ESPN','field':'model_espn','sortable':True},
                {'name':'k','label':'K','field':'k','sortable':True},
            ]
            closure_table_container.clear()
            with closure_table_container:
                ui.table(columns=columns, rows=table_rows, row_key='name', pagination=20).classes('w-full').props('dense')

            component_closure_container.clear()
            with component_closure_container:
                if not component_rows:
                    ui.label('No prospective component observations yet. Capture the pregame state before kickoff, then run closure-update after games.').classes('subtle text-sm')
                else:
                    comp_table_rows = []
                    for r in component_rows:
                        comp_table_rows.append({
                            'position': r.get('position'),
                            'component': r.get('component'),
                            'n': r.get('n'),
                            'bias': None if r.get('bias') is None else round(float(r.get('bias')), 4),
                            'rmse': None if r.get('rmse') is None else round(float(r.get('rmse')), 4),
                            'base_rmse': None if r.get('base_rmse') is None else round(float(r.get('base_rmse')), 4),
                            'delta_rmse': None if r.get('interaction_rmse_improvement') is None else round(float(r.get('interaction_rmse_improvement')), 4),
                            'ratio': None if r.get('mean_data_over_mc') is None else round(float(r.get('mean_data_over_mc')), 4),
                        })
                    comp_columns = [
                        {'name':'position','label':'Pos','field':'position','sortable':True},
                        {'name':'component','label':'Component','field':'component','sortable':True,'align':'left'},
                        {'name':'n','label':'N','field':'n','sortable':True},
                        {'name':'bias','label':'Bias','field':'bias','sortable':True},
                        {'name':'rmse','label':'Corrected RMSE','field':'rmse','sortable':True},
                        {'name':'base_rmse','label':'Base RMSE','field':'base_rmse','sortable':True},
                        {'name':'delta_rmse','label':'ΔRMSE','field':'delta_rmse','sortable':True},
                        {'name':'ratio','label':'Mean Data/MC','field':'ratio','sortable':True},
                    ]
                    ui.table(columns=comp_columns, rows=comp_table_rows, row_key='component', pagination=25).classes('w-full').props('dense')

        async def capture_pregame_state() -> None:
            closure_capture_button.disable()
            try:
                result = await io_call(service.capture_pregame_closure)
                closure_capture_status.set_text(
                    f"Captured {result.get('season')}/W{int(result.get('week') or 0):02d} · "
                    f"players={result.get('players')} components={result.get('components')} · {result.get('path')}"
                )
                ui.notify('Immutable pregame closure state saved.', color='positive')
            except Exception as exc:
                closure_capture_status.set_text(f'Capture failed: {exc}')
                ui.notify(f'Pregame closure capture failed: {exc}', color='negative', timeout=12000)
            finally:
                closure_capture_button.enable()

        async def generate_chat_diagnosis() -> None:
            chat_report_button.disable()
            try:
                selected_action = last_action_result
                if selected_action is not None:
                    add = selected_action.get('add') or {}
                    drop = selected_action.get('drop') or {}
                    if add_select.value is None or drop_select.value is None or int(add.get('espn_id') or -1) != int(add_select.value) or int(drop.get('espn_id') or -1) != int(drop_select.value):
                        selected_action = None
                selected_trade = last_trade_result
                if selected_trade is not None:
                    selected_partner = int(trade_partner_select.value) if trade_partner_select.value is not None else None
                    report_partner = int((selected_trade.get('partner_team') or {}).get('team_id') or -1)
                    if selected_partner != report_partner:
                        selected_trade = None
                report = await mc_call(
                    'Chat diagnosis MC', service.write_chat_report,
                    out_dir='data/chat_reports',
                    selection=dict(lineup_selection),
                    availability_modes=dict(availability_modes),
                    limited_fraction=float(limited_fraction),
                    action_result=selected_action,
                    trade_result=selected_trade,
                )
                chat_report_textarea.value = report['text']
                chat_report_textarea.update()
                chat_report_path_label.set_text(f"TXT: {report['text_path']} · JSON: {report['json_path']}")
                print('\n=== CHAT DIAGNOSIS ===')
                print(report['text'], end='')
                print(f"Chat report TXT: {report['text_path']}")
                print(f"Chat report JSON: {report['json_path']}")
                chat_report_dialog.open()
            except Exception as exc:
                ui.notify(f'Chat diagnosis failed: {exc}', color='negative', timeout=12000)
            finally:
                chat_report_button.enable()

        async def sync_data() -> None:
            sync_button.disable()
            sync_spinner.visible = True
            try:
                result = await io_call(service.sync_and_reload)
                ui.notify(f"Snapshot refreshed: {Path(result['snapshot']).name}", color='positive')
                await refresh_dashboard(False)
            except Exception as exc:
                ui.notify(f'Sync failed: {exc}', color='negative', timeout=15000)
            finally:
                sync_spinner.visible = False
                sync_button.enable()

        async def reset_lineup() -> None:
            nonlocal lineup_selection, availability_modes
            lineup_selection = await io_call(service.default_lineup_selection)
            availability_modes = {int(r['espn_id']): 'MODEL' for r in roster_cache}
            render_lineup_controls()
            await recompute_lab()

        async def change_limited(e) -> None:
            nonlocal limited_fraction
            limited_fraction = float(e.value)
            limited_label.set_text(f'{limited_fraction:.0%}')
            await recompute_lab()

        def selected_mc_scenarios() -> int:
            value = mc_select.value
            if value is None:
                return int(service.mc_scenarios)
            return int(str(value).replace(',', '').strip())

        def sync_mc_select_to_service() -> None:
            mc_select.value = f"{service.mc_scenarios:,}"
            mc_select.update()

        async def apply_mc_size(new_n: int) -> None:
            async def _apply_mc_size_observed_body():
                """Execute an already-accepted MC resize request.

                The browser click itself is handled synchronously by request_selected_mc so the
                user gets immediate visible acknowledgement before any context rebuild begins.
                """
                try:
                    mc_state['request_pending'] = True
                    mc_run_spinner.visible = True
                    mc_status_label.set_text(f'MC REQUEST RECEIVED — preparing N={int(new_n):,}')
                    mc_phase_label.set_text('Resetting predictive MC streams and clearing predictive caches…')
                    mc_elapsed_label.set_text('request accepted')
                    mc_progress.set_value(0.0)
                    mc_select.disable()
                    run_mc_button.disable()
                    # Give NiceGUI one event-loop turn to flush the acknowledgement to Firefox
                    # before context construction starts in the worker thread.
                    await asyncio.sleep(0)

                    # v0.27 resizes only predictive streams/caches. Static league/player
                    # data are retained, and the expensive opponent-reference MC is deferred
                    # into the visible dashboard progress job.
                    reset_started = time.monotonic()
                    await io_call(service.set_mc_scenarios, int(new_n))
                    reset_elapsed = time.monotonic() - reset_started
                    sync_mc_select_to_service()
                    mc_status_label.set_text(f'MC CONTEXT READY — starting N={service.mc_scenarios:,}')
                    mc_elapsed_label.set_text(f'context reset {reset_elapsed:.2f}s')
                    mc_phase_label.set_text('Starting dashboard / policy Monte Carlo…')
                    await asyncio.sleep(0)
                    await refresh_dashboard(False)
                except Exception as exc:
                    mc_state['error'] = f'Could not start selected MC size: {exc}'
                    sync_mc_select_to_service()
                    update_mc_status()
                    ui.notify(str(mc_state['error']), color='negative', timeout=12000)
                finally:
                    mc_state['request_pending'] = False
                    mc_select.enable()
                    run_mc_button.enable()

            return await observe_task('season.apply_mc_size', _apply_mc_size_observed_body())
        def request_selected_mc() -> None:
            """Synchronous browser-click handler which visibly acknowledges the click."""
            if mc_state.get('running') or mc_state.get('request_pending'):
                current = int(service.mc_scenarios)
                mc_status_label.set_text(f'MC request ignored — N={current:,} is still running/preparing')
                mc_phase_label.set_text('Wait for the current Monte Carlo job to finish, then press Run selected MC again.')
                ui.notify('Monte Carlo is already running or preparing.', color='warning')
                return
            try:
                new_n = selected_mc_scenarios()
            except Exception as exc:
                mc_state['error'] = f'Invalid MC universe selection: {exc}'
                update_mc_status()
                return

            # This state/UI mutation occurs inside the synchronous click event itself. If the
            # browser event arrives, the page changes immediately, independently of the long
            # worker task that follows. NiceGUI background_tasks then owns the async work.
            mc_state['request_pending'] = True
            mc_state['error'] = None
            mc_run_spinner.visible = True
            mc_status_label.set_text(f'MC REQUEST RECEIVED — N={new_n:,}')
            mc_phase_label.set_text('Queueing predictive-stream reset…')
            mc_elapsed_label.set_text('request accepted')
            mc_progress.set_value(0.0)
            mc_select.disable()
            run_mc_button.disable()
            background_tasks.create(apply_mc_size(new_n))

        async def recompute_dashboard() -> None:
            if mc_state.get('running'):
                ui.notify('Wait for the current Monte Carlo run to finish before recomputing.', color='warning')
                return
            try:
                # Explicitly rebuild the same-N context so this recovery button cannot return
                # cached baseline arrays while claiming to recompute the dashboard.
                await io_call(service.set_mc_scenarios, service.mc_scenarios)
                sync_mc_select_to_service()
                await refresh_dashboard(False)
            except Exception as exc:
                ui.notify(f'Dashboard recompute failed: {exc}', color='negative', timeout=12000)

        def surface_ui_exception(exc: Exception) -> None:
            """Keep browser-event failures visible instead of losing them in server logs."""
            mc_state['error'] = f'GUI event error: {exc}'
            print(mc_state['error'])
            try:
                update_mc_status()
            except Exception:
                pass

        ui.on_exception(surface_ui_exception)

        chat_report_button.on_click(generate_chat_diagnosis)
        closure_capture_button.on_click(capture_pregame_state)
        sync_button.on_click(sync_data)
        recompute_button.on_click(recompute_dashboard)
        run_mc_button.on_click(request_selected_mc)
        reset_lineup_button.on_click(reset_lineup)
        limited_slider.on_value_change(change_limited)
        player_select.on_value_change(show_player_diagnostic)
        evaluate_action_button.on_click(evaluate_action)
        defense_channel_button.on_click(evaluate_defense_channel_gui)
        kicker_channel_button.on_click(evaluate_kicker_channel_gui)
        trade_partner_select.on_value_change(load_trade_partner)
        evaluate_trade_button.on_click(evaluate_trade_offer_gui)
        trade_search_button.on_click(screen_trade_offers_gui)
        pool_filter.on_value_change(lambda _e: render_available_table())

        # Establish the websocket before any long-running model work. This guarantees
        # the initial shell and subsequent MC status updates are visible to the browser.
        await client.connected()
        mc_status_label.set_text(f'Browser connected · starting dashboard MC with N={service.mc_scenarios:,}')
        mc_phase_label.set_text('Initializing deterministic model streams and policy evaluation…')
        mc_progress.set_value(0.0)
        await refresh_dashboard(False)

    ui.run(
        title='Hail to Pitt · Season Control Room',
        port=int(port),
        reload=False,
        native=bool(native),
        window_size=(1700, 1050) if native else None,
        show=not native,
    )
