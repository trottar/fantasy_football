from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

import pandas as pd

from .bootstrap import GuiStartupError, ensure_gui_runtime
from .controller import (
    DraftController,
    compute_deep_forecast_from_paths,
    compute_fast_forecast_from_paths,
    compute_fast_recommendations_from_paths,
    compute_recommendations_from_paths,
)
from .paste_parser import preview_is_committable
from .visualizations import tier_heatmap_options, value_survival_options


def run_gui(
    board_path: str = "data/processed/live_board_2026.csv",
    state_path: str = "data/draft_state.json",
    league_path: str = "config/league.json",
    model_path: str = "config/model.json",
    port: int = 8080,
    native: bool = False,
) -> None:
    try:
        from nicegui import run, ui
    except ImportError as exc:  # pragma: no cover - exercised only by user runtime
        raise RuntimeError(
            "NiceGUI is not installed. Run: python -m pip install -r requirements.txt"
        ) from exc

    try:
        bootstrap = ensure_gui_runtime(
            board_path=board_path,
            state_path=state_path,
            league_path=league_path,
            model_path=model_path,
        )
    except GuiStartupError as exc:
        raise RuntimeError(str(exc)) from None

    for message in bootstrap.messages:
        print(f"[GUI bootstrap] {message}")

    controller = DraftController(board_path, state_path, league_path, model_path)
    recommendation_rows: list[dict[str, Any]] = []
    model_task: asyncio.Task | None = None
    model_generation = 0

    ui.colors(primary="#3b82f6", secondary="#64748b", accent="#22c55e")
    ui.dark_mode().enable()

    ui.add_css('''
        body { background: #0f172a; }
        .cockpit-card { background: #111827; border: 1px solid #334155; border-radius: 10px; }
        .metric { font-size: 1.65rem; font-weight: 700; line-height: 1.1; }
        .subtle { color: #94a3b8; }
        .on-clock { color: #4ade80; }
        .short-turn { color: #fbbf24; }
        .long-turn { color: #60a5fa; }
        .pick-pill { border: 1px solid #475569; border-radius: 9999px; padding: 2px 8px; }
        .roster-slot { min-height: 34px; border-bottom: 1px solid #1f2937; }
        .recommend-1 { border-left: 4px solid #22c55e; }
    ''')

    with ui.header().classes('items-center justify-between bg-slate-950 px-4 py-2'):
        ui.label('Hail to Pitt · Draft Cockpit').classes('text-xl font-semibold')
        status_label = ui.label('')

    with ui.column().classes('w-full max-w-[1800px] mx-auto p-3 gap-3'):
        # Top status strip
        with ui.row().classes('w-full gap-3 flex-wrap'):
            pick_card = ui.card().classes('cockpit-card p-3 min-w-[180px]')
            mode_card = ui.card().classes('cockpit-card p-3 min-w-[220px]')
            next_card = ui.card().classes('cockpit-card p-3 min-w-[220px]')
            available_card = ui.card().classes('cockpit-card p-3 min-w-[180px]')
            bank_card = ui.card().classes('cockpit-card p-3 min-w-[300px]')

        with ui.row().classes('w-full gap-3 items-stretch'):
            # Input/control column
            with ui.column().classes('w-[360px] min-w-[320px] gap-3'):
                with ui.card().classes('cockpit-card p-3 w-full'):
                    ui.label('Record pick').classes('text-lg font-semibold')
                    player_select = ui.select(
                        options={},
                        with_input=True,
                        label='Search available player',
                    ).props('outlined clearable').classes('w-full')
                    with ui.row().classes('w-full gap-2'):
                        record_button = ui.button('Record', icon='add_task').classes('flex-1')
                        undo_button = ui.button('Undo', icon='undo', color='secondary').classes('flex-1')
                    reset_button = ui.button(
                        'New Mock / Reset Draft', icon='restart_alt', color='negative'
                    ).props('outline').classes('w-full')

                    with ui.dialog() as reset_dialog, ui.card().classes('cockpit-card p-4 min-w-[420px]'):
                        ui.label('Reset current mock draft?').classes('text-lg font-semibold')
                        ui.label(
                            'This clears the 192-pick draft state and the conditioned DEEP particle bank. '
                            'Player data, projections, model files, and saved mock-calibration samples are preserved.'
                        ).classes('subtle text-sm')
                        with ui.row().classes('w-full justify-end gap-2 mt-3'):
                            reset_cancel_button = ui.button('Cancel', color='secondary').props('flat')
                            reset_confirm_button = ui.button(
                                'Reset Draft', icon='restart_alt', color='negative'
                            )

                with ui.card().classes('cockpit-card p-3 w-full'):
                    ui.label('Paste recent ESPN picks').classes('text-lg font-semibold')
                    paste_box = ui.textarea(
                        placeholder='Paste one or many recent draft lines here…'
                    ).props('outlined autogrow').classes('w-full')
                    with ui.row().classes('w-full gap-2'):
                        preview_button = ui.button('Preview', icon='preview').classes('flex-1')
                        commit_button = ui.button('Commit batch', icon='playlist_add_check').classes('flex-1')
                    remove_picked_button = ui.button(
                        'Remove Already Picked', icon='filter_alt_off', color='secondary'
                    ).classes('w-full')
                    remove_picked_button.visible = False
                    preview_container = ui.column().classes('w-full gap-1 mt-2')

                with ui.card().classes('cockpit-card p-3 w-full'):
                    ui.label('Your roster').classes('text-lg font-semibold')
                    roster_container = ui.column().classes('w-full gap-0')

                with ui.card().classes('cockpit-card p-3 w-full'):
                    ui.label('Recent picks').classes('text-lg font-semibold')
                    recent_container = ui.column().classes('w-full gap-1')

            # Main decision area
            with ui.column().classes('flex-1 min-w-0 gap-3'):
                with ui.card().classes('cockpit-card p-3 w-full'):
                    with ui.row().classes('w-full justify-between items-center flex-wrap gap-2'):
                        with ui.column().classes('gap-0'):
                            ui.label('Recommendations').classes('text-lg font-semibold')
                            recommendation_subtitle = ui.label('Run Fast or Deep at any time; opponent turns forecast your next pick.').classes('subtle text-sm')
                        with ui.row().classes('gap-2 items-center'):
                            elapsed_label = ui.label('').classes('subtle text-sm')
                            cancel_button = ui.button('Cancel', icon='stop_circle', color='negative')
                            fast_button = ui.button('Fast', icon='bolt')
                            deep_button = ui.button('Deep', icon='analytics', color='secondary')
                    with ui.row().classes('w-full items-center gap-2 mt-2') as worker_status_row:
                        worker_spinner = ui.spinner(size='sm')
                        worker_status_label = ui.label('')
                    worker_status_row.visible = False
                    cancel_button.visible = False
                    recommendation_container = ui.column().classes('w-full gap-2 mt-2')

                with ui.row().classes('w-full gap-3 items-stretch'):
                    with ui.card().classes('cockpit-card p-3 flex-1 min-w-[520px]'):
                        ui.label('Value vs next-turn survival').classes('text-lg font-semibold')
                        survival_caption = ui.label('').classes('subtle text-sm')
                        survival_chart_container = ui.column().classes('w-full')
                    with ui.card().classes('cockpit-card p-3 flex-1 min-w-[520px]'):
                        ui.label('Available positional tiers').classes('text-lg font-semibold')
                        ui.label('Heat intensity = dynamic draft value; columns are current positional rank.').classes('subtle text-sm')
                        tier_chart_container = ui.column().classes('w-full')

                with ui.card().classes('cockpit-card p-3 w-full'):
                    ui.label('Exact available board').classes('text-lg font-semibold')
                    exact_table_container = ui.column().classes('w-full')

    def render_status() -> None:
        info = controller.turn_info()
        dyn, _ = controller.available_dynamic()
        status_label.set_text(
            'YOU ARE ON CLOCK' if info.user_on_clock else f'{info.opponent_picks_until_user} picks until your turn'
        )
        status_label.classes(remove='on-clock')
        if info.user_on_clock:
            status_label.classes(add='on-clock font-bold')

        pick_card.clear()
        with pick_card:
            ui.label('Next overall').classes('subtle text-xs uppercase')
            ui.label(str(info.next_overall)).classes('metric')

        mode_card.clear()
        with mode_card:
            ui.label('Cadence mode').classes('subtle text-xs uppercase')
            cls = 'metric '
            cls += 'short-turn' if info.mode == 'SHORT TURN' else 'long-turn' if info.mode == 'LONG TURN' else ''
            ui.label(info.mode).classes(cls)
            if info.user_on_clock and info.opponent_picks_after_user is not None:
                ui.label(f'{info.opponent_picks_after_user} opponent picks after this selection').classes('subtle text-sm')

        next_card.clear()
        with next_card:
            ui.label('User pick geometry').classes('subtle text-xs uppercase')
            if info.user_on_clock:
                ui.label(f'{info.next_overall} → {info.later_user_pick or "—"}').classes('metric')
            else:
                ui.label(f'next: {info.next_user_pick or "—"}').classes('metric')
            ui.label('short-turn logic activates automatically').classes('subtle text-xs')

        available_card.clear()
        with available_card:
            ui.label('Available modeled').classes('subtle text-xs uppercase')
            ui.label(str(len(dyn))).classes('metric')

        bank = controller.deep_bank_status()
        bank_card.clear()
        with bank_card:
            ui.label('DEEP particle bank').classes('subtle text-xs uppercase')
            if not bank.get('exists'):
                ui.label('No bank yet').classes('text-lg font-semibold')
                ui.label('Run DEEP to initialize reusable scenarios.').classes('subtle text-xs')
            elif not bank.get('valid'):
                ui.label('STALE / INVALID').classes('text-lg font-semibold text-red-300')
                ui.label(str(bank.get('message') or 'Rerun DEEP.')).classes('subtle text-xs')
            else:
                particles = int(bank.get('particles') or 0)
                ess = float(bank.get('ess') or 0.0)
                frac = 100.0 * float(bank.get('ess_fraction') or 0.0)
                ui.label(f'{ess:.0f} ESS / {particles} particles').classes('text-lg font-semibold')
                ui.label(
                    f'anchor {bank.get("anchor_pick")} · conditioned through {bank.get("conditioned_through")} · {frac:.0f}% effective'
                ).classes('subtle text-xs')
                if bank.get('selected_branch_name'):
                    ui.label(f'Chosen anchor branch: {bank.get("selected_branch_name")}').classes('text-xs text-green-300')
                if bank.get('degraded'):
                    ui.label('Bank degraded — next DEEP will refresh more aggressively.').classes('text-xs text-amber-300')

    def render_player_options() -> None:
        opts = controller.quick_player_options()
        player_select.set_options(opts)
        player_select.value = None
        player_select.update()

    def render_roster() -> None:
        roster_container.clear()
        roster = controller.user_roster()
        slots = ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'FLEX', 'DST', 'K']
        used = set()
        assignments = []

        for slot in slots:
            found = None
            for i, p in enumerate(roster):
                if i in used:
                    continue
                pos = p.get('position')
                if pos == slot or (slot == 'FLEX' and pos in {'RB', 'WR', 'TE'}):
                    found = (i, p)
                    break
            if found:
                used.add(found[0])
                assignments.append((slot, found[1]))
            else:
                assignments.append((slot, None))

        with roster_container:
            for slot, p in assignments:
                with ui.row().classes('w-full roster-slot items-center gap-2'):
                    ui.label(slot).classes('w-12 text-xs font-bold text-slate-400')
                    ui.label(p['player_name'] if p else '—').classes('flex-1')
                    if p:
                        ui.label(p.get('position') or '').classes('pick-pill text-xs')

            bench = [p for i, p in enumerate(roster) if i not in used]
            if bench:
                ui.separator().classes('my-1')
                ui.label('BENCH').classes('text-xs font-bold text-slate-400')
                for p in bench:
                    ui.label(f'{p["player_name"]} · {p.get("position") or "?"}').classes('text-sm')

    def render_recent() -> None:
        recent_container.clear()
        recent = controller.recent_picks(8)
        if not recent:
            with recent_container:
                ui.label('No picks recorded.').classes('subtle text-sm')
            return
        for p in reversed(recent):
            with recent_container:
                with ui.row().classes('w-full items-center gap-2'):
                    ui.label(str(p['overall'])).classes('pick-pill text-xs')
                    ui.label(p['player_name']).classes('flex-1 text-sm')
                    ui.label(p.get('position') or '?').classes('text-xs subtle')

    def render_preview(rows=None) -> None:
        preview_container.clear()
        rows = rows or []
        removable = sum(r.status == 'already_recorded' for r in rows)
        remove_picked_button.visible = removable > 0

        if not rows:
            with preview_container:
                ui.label(
                    'Overlapping picks already in the draft state are safe to paste; '
                    'they will be recognized and ignored.'
                ).classes('subtle text-xs')
            commit_button.disable()
            return

        for r in rows:
            with preview_container:
                with ui.row().classes('w-full gap-2 items-center'):
                    ui.label(str(r.overall or '?')).classes('pick-pill text-xs')
                    if r.status == 'resolved':
                        ui.icon('check_circle').classes('text-green-400')
                        ui.label(
                            f'{r.name} · {r.position} {r.nfl_team}'
                        ).classes('text-sm flex-1')
                    elif r.status == 'already_recorded':
                        ui.icon('content_copy').classes('text-amber-400')
                        ui.label(
                            f'{r.name} · {r.message}'
                        ).classes('text-sm flex-1 text-amber-200')
                    else:
                        ui.icon('error').classes('text-red-400')
                        ui.label(
                            r.message or r.raw_text
                        ).classes('text-sm flex-1 text-red-300')

        if removable:
            with preview_container:
                ui.label(
                    f'{removable} already-recorded pick'
                    f'{"s" if removable != 1 else ""} will be ignored on commit.'
                ).classes('subtle text-xs')

        if preview_is_committable(rows):
            commit_button.enable()
        else:
            commit_button.disable()

    def render_visuals() -> None:
        frame, target = controller.survival_frame(55)
        survival_caption.set_text(
            f'X = probability of still being available at pick {target}; upper-left means high value and dangerous to wait.'
            if target else 'No later user pick remains.'
        )
        survival_chart_container.clear()
        with survival_chart_container:
            ui.echart(value_survival_options(frame, target)).classes('w-full h-[390px]')

        tiers = controller.tier_frame(12)
        tier_chart_container.clear()
        with tier_chart_container:
            ui.echart(tier_heatmap_options(tiers)).classes('w-full h-[390px]')

        exact_table_container.clear()
        dyn, _ = controller.available_dynamic()
        dyn = dyn.sort_values('dynamic_draft_value', ascending=False).head(35)
        rows = []
        for _, r in dyn.iterrows():
            rows.append({
                'name': r['name'],
                'pos': r['position'],
                'adp': round(float(r['espn_adp']), 1) if pd.notna(r['espn_adp']) else None,
                'tier': int(r['tier']) if pd.notna(r['tier']) else None,
                'value': round(float(r['dynamic_draft_value']), 2),
                'ppg': round(float(r['latent_mean_ppg']), 2),
                'sd': round(float(r['latent_mean_sd_ppg']), 2),
            })
        columns = [
            {'name': 'name', 'label': 'Player', 'field': 'name', 'align': 'left', 'sortable': True},
            {'name': 'pos', 'label': 'Pos', 'field': 'pos', 'sortable': True},
            {'name': 'adp', 'label': 'ADP', 'field': 'adp', 'sortable': True},
            {'name': 'tier', 'label': 'Tier', 'field': 'tier', 'sortable': True},
            {'name': 'value', 'label': 'Dyn value', 'field': 'value', 'sortable': True},
            {'name': 'ppg', 'label': 'PPG', 'field': 'ppg', 'sortable': True},
            {'name': 'sd', 'label': 'σmean', 'field': 'sd', 'sortable': True},
        ]
        with exact_table_container:
            ui.table(columns=columns, rows=rows, row_key='name', pagination=15).classes('w-full')

    def render_recommendations() -> None:
        recommendation_container.clear()
        info = controller.turn_info()
        if not recommendation_rows:
            with recommendation_container:
                if info.user_on_clock:
                    msg = 'Run Fast or Deep for a current-pick recommendation.'
                else:
                    msg = (
                        f'Run Fast or Deep now to forecast your board at pick '
                        f'{info.next_user_pick}; rerun after each opponent pick to condition the forecast.'
                    )
                ui.label(msg).classes('subtle')
            return

        forecast_mode = recommendation_rows[0].get('analysis_mode') == 'forecast'

        for i, r in enumerate(recommendation_rows[:10], start=1):
            with recommendation_container:
                card_cls = 'cockpit-card p-3 w-full'
                if i == 1:
                    card_cls += ' recommend-1'
                with ui.card().classes(card_cls):
                    with ui.row().classes('w-full items-start justify-between gap-3'):
                        with ui.column().classes('gap-0 min-w-0'):
                            ui.label(f'{i}. {r["name"]}').classes('text-lg font-semibold')
                            adp = r.get('espn_adp')
                            adp_text = f'{float(adp):.1f}' if adp is not None and pd.notna(adp) else '—'
                            ui.label(
                                f'{r["position"]} {r.get("nfl_team", "")} · '
                                f'ADP {adp_text} · Tier {r.get("tier", "?")}'
                            ).classes('subtle text-sm')

                        if forecast_mode:
                            ui.label(
                                f'{100*float(r.get("p_best_target", 0)):.0f}% best'
                            ).classes('metric')
                        else:
                            ui.label(f'{float(r["mc_objective"]):.2f}').classes('metric')

                    with ui.row().classes('w-full gap-5 flex-wrap mt-1'):
                        if forecast_mode:
                            ui.label(
                                f'P(available @ {int(r["target_pick"])}) '
                                f'{100*float(r.get("p_available_target", 0)):.0f}%'
                            )
                            ui.label(
                                f'Target value {float(r.get("target_value_estimate", 0)):.2f}'
                            )
                            ui.label(
                                f'P(best @ {int(r["target_pick"])}) '
                                f'{100*float(r.get("p_best_target", 0)):.0f}%'
                            )
                        else:
                            ui.label(f'Roster Δ now {float(r.get("immediate_draft_value", 0)):.2f}')
                            if r.get('final_roster_utility_mean') is not None:
                                ui.label(
                                    f'Final roster {float(r.get("final_roster_utility_mean", 0)):.2f} '
                                    f'± {float(r.get("final_roster_utility_sd", 0)):.2f}'
                                )
                            if r.get('final_starter_value_mean') is not None:
                                ui.label(
                                    f'Healthy starters {float(r.get("final_starter_value_mean", 0)):.2f} · '
                                    f'Bench insurance {float(r.get("final_bench_insurance_mean", r.get("final_bench_value_mean", 0))):.2f}'
                                )
                            if r.get('final_expected_h2h_win_probability_mean') is not None:
                                ui.label(
                                    f'H2H weekly win ~{100*float(r.get("final_expected_h2h_win_probability_mean", 0)):.1f}%'
                                )
                            if r.get('final_bye_loss_ppg_mean') is not None:
                                ui.label(
                                    f'Bye loss {float(r.get("final_bye_loss_ppg_mean", 0)):.2f} PPG · '
                                    f'Weekly floor {float(r.get("final_weekly_floor_ppg_mean", 0)):.2f}'
                                )
                            if r.get('next_turn_option_mean') is not None:
                                ui.label(
                                    f'Next-turn option {float(r.get("next_turn_option_mean", 0)):.2f} '
                                    f'± {float(r.get("next_turn_option_sd", 0)):.2f}'
                                )

                        if r.get('engine'):
                            ui.label(str(r['engine'])).classes('pick-pill text-xs')
                        if r.get('deep_bank_particles') is not None:
                            bank_particles = int(r.get('deep_bank_particles') or 0)
                            bank_ess = float(r.get('deep_bank_ess') or 0.0)
                            ui.label(f'DEEP bank {bank_ess:.0f}/{bank_particles} ESS').classes('pick-pill text-xs')

                    if forecast_mode:
                        ui.label(
                            f'Projected option at pick {int(r["target_pick"])} after '
                            f'{int(r.get("opponent_picks_to_target", 0))} remaining opponent picks.'
                        ).classes('text-sm text-slate-300')
                    else:
                        if r.get('most_common_best_next'):
                            pct = 100*float(r.get("p_most_common_best_next", 0))
                            suffix = (
                                'of exact short-turn outcomes'
                                if str(r.get('engine', '')).startswith('SHORT-EXACT')
                                else 'of rollouts'
                            )
                            ui.label(
                                f'Common best next turn: {r["most_common_best_next"]} '
                                f'({pct:.0f}% {suffix})'
                            ).classes('text-sm text-slate-300')

                        if r.get('expected_final_RB') is not None:
                            ui.label(
                                'Expected final core: '
                                f'QB {float(r.get("expected_final_QB", 0)):.1f} · '
                                f'RB {float(r.get("expected_final_RB", 0)):.1f} · '
                                f'WR {float(r.get("expected_final_WR", 0)):.1f} · '
                                f'TE {float(r.get("expected_final_TE", 0)):.1f}'
                            ).classes('text-sm text-slate-300')

                        if r.get('final_max_starter_bye_conflict_mean') is not None:
                            bye_text = (
                                f'Bye profile: max starter overlap '
                                f'{float(r.get("final_max_starter_bye_conflict_mean", 0)):.1f} · '
                                f'worst week ~{int(r.get("final_worst_bye_week_mode", 0))}'
                            )
                            if float(r.get('final_playoff_bye_starters_mean', 0) or 0) > 0.05:
                                bye_text += (
                                    f' · playoff-bye starters '
                                    f'{float(r.get("final_playoff_bye_starters_mean", 0)):.1f}'
                                )
                            ui.label(bye_text).classes('text-sm text-cyan-200')

                        contingency_parts = []
                        for j in range(1, 4):
                            name = r.get(f'contingency_{j}_name')
                            prob = r.get(f'contingency_{j}_prob')
                            if name and prob is not None:
                                contingency_parts.append(
                                    f'{name} {100*float(prob):.0f}%'
                                )
                        if contingency_parts:
                            ui.label(
                                'Next-pick plan: ' + ' · '.join(contingency_parts)
                            ).classes('text-sm text-amber-200')

    def invalidate_analysis_for_state_change() -> None:
        """Invalidate any analysis created from the previous draft snapshot."""
        nonlocal model_generation, model_task, recommendation_rows
        model_generation += 1
        recommendation_rows = []
        if model_task is not None and not model_task.done():
            model_task.cancel()
        model_task = None
        worker_status_row.visible = False
        cancel_button.visible = False
        fast_button.enable()
        deep_button.enable()
        elapsed_label.set_text('')
        recommendation_subtitle.set_text(
            'Draft state changed; displayed result cleared. DEEP bank retained and conditioned to the new picks.'
        )

    def refresh_all() -> None:
        nonlocal recommendation_rows
        recommendation_rows = []
        render_status()
        render_player_options()
        render_roster()
        render_recent()
        render_preview([])
        render_visuals()
        render_recommendations()

    def record_selected() -> None:
        if player_select.value is None:
            ui.notify('Choose a player first.', color='warning')
            return
        try:
            pick = controller.record_player(int(player_select.value))
            invalidate_analysis_for_state_change()
            ui.notify(f'Recorded {pick["overall"]}: {pick["player_name"]}', color='positive')
            refresh_all()
        except Exception as exc:
            ui.notify(str(exc), color='negative', timeout=6000)

    def undo() -> None:
        try:
            pick = controller.undo_last_pick()
            if pick is None:
                ui.notify('No pick to undo.', color='warning')
            else:
                ui.notify(f'Undid {pick["overall"]}: {pick["player_name"]}', color='warning')
                invalidate_analysis_for_state_change()
            refresh_all()
        except Exception as exc:
            ui.notify(str(exc), color='negative')

    def open_reset_dialog() -> None:
        reset_dialog.open()

    def reset_current_draft() -> None:
        try:
            reset_dialog.close()
            result = controller.reset_draft()
            invalidate_analysis_for_state_change()
            player_select.value = None
            paste_box.value = ''
            refresh_all()
            recommendation_subtitle.set_text(
                'New mock ready. Run DEEP to create a fresh particle bank for this draft.'
            )
            removed_text = (
                ' DEEP particle bank cleared.' if result.get('bank_removed') else ''
            )
            ui.notify(
                f'Reset draft: cleared {int(result.get("previous_picks", 0))} picks.'
                + removed_text,
                color='positive', timeout=6000,
            )
        except Exception as exc:
            ui.notify(str(exc), color='negative', timeout=8000)

    def preview() -> None:
        rows = controller.preview_paste(paste_box.value or '')
        render_preview(rows)
        if not rows:
            ui.notify('No draft lines recognized.', color='warning')

    def remove_already_picked() -> None:
        rows, removed = controller.remove_already_picked_from_preview()
        if removed <= 0:
            ui.notify('No already-recorded picks in this preview.', color='warning')
            return

        # Rewrite the paste box to the canonical set of remaining recognized
        # lines so clicking Preview again does not reintroduce the overlap.
        paste_box.value = '\n'.join(r.raw_text for r in rows)
        render_preview(rows)
        ui.notify(
            f'Removed {removed} already-recorded pick'
            f'{"s" if removed != 1 else ""}.',
            color='positive',
        )

    def commit_batch() -> None:
        try:
            picks = controller.commit_preview()
            if picks:
                invalidate_analysis_for_state_change()
            ui.notify(f'Committed {len(picks)} picks.', color='positive')
            paste_box.value = ''
            refresh_all()
        except Exception as exc:
            ui.notify(str(exc), color='negative', timeout=6000)

    async def _elapsed_ticker(started: float, generation: int) -> None:
        while generation == model_generation and model_task is not None and not model_task.done():
            elapsed_label.set_text(f'{time.monotonic() - started:.1f}s')
            await asyncio.sleep(0.25)

    async def _run_model_job(deep: bool, generation: int) -> None:
        nonlocal recommendation_rows, model_task
        info = controller.turn_info()
        on_clock = info.user_on_clock
        short = (
            info.mode == 'SHORT TURN'
            if on_clock
            else info.opponent_picks_until_user <= 2
        )

        if on_clock:
            if deep:
                simulations = 30
                candidates = 10
                worker = compute_recommendations_from_paths
                engine_text = 'DEEP · full-draft team-aware rollout'
            else:
                simulations = 40
                candidates = 10
                worker = compute_fast_recommendations_from_paths
                engine_text = (
                    'FAST · exact next-turn contingency + full-draft rollout'
                    if short
                    else 'FAST · full-draft market rollout'
                )
            task_text = 'current-pick recommendation'
        else:
            target = info.next_user_pick
            if deep:
                # Off-turn deep forecast is one rollout set, not nested per
                # candidate, so a few hundred sequential simulations are useful
                # while waiting without the explosive v0.10 cost.
                simulations = 300 if not short else 500
                candidates = 16
                worker = compute_deep_forecast_from_paths
                engine_text = 'DEEP · team-aware next-pick forecast'
            else:
                simulations = 6000 if not short else 10000
                candidates = 16
                worker = compute_fast_forecast_from_paths
                engine_text = (
                    'FAST · short-horizon next-pick forecast'
                    if short
                    else 'FAST · vectorized next-pick forecast'
                )
            task_text = f'forecast for user pick {target}'

        analysis_state_signature = controller.state_signature()
        started = time.monotonic()
        fast_button.disable()
        deep_button.disable()
        cancel_button.visible = True
        worker_status_row.visible = True
        worker_status_label.set_text(engine_text)
        elapsed_label.set_text('0.0s')
        recommendation_subtitle.set_text(
            f'{engine_text} · {task_text} · {candidates} displayed candidates'
            + f' · {simulations} full-draft rollouts'
        )
        ticker = asyncio.create_task(_elapsed_ticker(started, generation))
        try:
            rows = await run.cpu_bound(
                worker,
                str(controller.board_path),
                str(controller.state_path),
                str(controller.league_path),
                str(controller.model_path),
                simulations,
                candidates,
                None,
            )
            if generation != model_generation:
                return
            if controller.state_signature() != analysis_state_signature:
                recommendation_rows = []
                render_recommendations()
                recommendation_subtitle.set_text(
                    'Draft state changed while analysis was running; stale result discarded.'
                )
                ui.notify(
                    'Stale analysis discarded because the draft state changed.',
                    color='warning', timeout=5000,
                )
                return

            proposed_rows = rows or []
            valid_rows, stale_names = controller.recommendation_rows_match_current_state(
                proposed_rows
            )
            if not valid_rows:
                recommendation_rows = []
                render_recommendations()
                recommendation_subtitle.set_text(
                    'Analysis failed availability validation; stale result discarded.'
                )
                ui.notify(
                    'Discarded recommendation containing unavailable player(s): '
                    + ', '.join(stale_names[:4]),
                    color='negative', timeout=8000,
                )
                return

            recommendation_rows = proposed_rows
            render_recommendations()
            elapsed = time.monotonic() - started
            row_engine = (
                recommendation_rows[0].get('engine')
                if recommendation_rows
                else engine_text
            )
            if on_clock:
                summary = f'{row_engine} completed in {elapsed:.2f}s · current-pick decision'
                if recommendation_rows and recommendation_rows[0].get('deep_bank_particles') is not None:
                    br = recommendation_rows[0]
                    summary += (
                        f' · DEEP bank ESS {float(br.get("deep_bank_ess", 0)):.0f}/'
                        f'{int(br.get("deep_bank_particles", 0))}'
                    )
            else:
                summary = (
                    f'{row_engine} completed in {elapsed:.2f}s · projected board '
                    f'for pick {info.next_user_pick}; rerun after each recorded pick'
                )
            recommendation_subtitle.set_text(summary)
        except asyncio.CancelledError:
            if generation == model_generation:
                recommendation_subtitle.set_text(
                    'Analysis cancelled; draft state is unchanged.'
                )
            raise
        except Exception as exc:
            if generation == model_generation:
                recommendation_rows = []
                render_recommendations()
                ui.notify(str(exc), color='negative', timeout=10000)
        finally:
            ticker.cancel()
            try:
                await ticker
            except asyncio.CancelledError:
                pass
            if generation == model_generation:
                worker_status_row.visible = False
                cancel_button.visible = False
                fast_button.enable()
                deep_button.enable()
                elapsed_label.set_text('')
            model_task = None

    def start_model(deep: bool = False) -> None:
        nonlocal model_task, model_generation
        info = controller.turn_info()
        if info.next_user_pick is None and not info.user_on_clock:
            ui.notify('No later user draft pick remains.', color='warning')
            return
        if model_task is not None and not model_task.done():
            ui.notify('A recommendation job is already running.', color='warning')
            return
        model_generation += 1
        generation = model_generation
        model_task = asyncio.create_task(_run_model_job(deep, generation))

    def cancel_model() -> None:
        nonlocal model_generation, model_task
        if model_task is None or model_task.done():
            return
        # Cancels/ignores the UI job immediately. Depending on the process-pool
        # backend, a CPU worker which has already started may finish privately;
        # its result cannot overwrite the current draft state or UI.
        model_generation += 1
        model_task.cancel()
        model_task = None
        worker_status_row.visible = False
        cancel_button.visible = False
        fast_button.enable()
        deep_button.enable()
        elapsed_label.set_text('')
        recommendation_subtitle.set_text('Cancelled; ready for a new state or recommendation.')
        ui.notify('Recommendation cancelled.', color='warning')


    record_button.on_click(record_selected)
    undo_button.on_click(undo)
    reset_button.on_click(open_reset_dialog)
    reset_cancel_button.on_click(reset_dialog.close)
    reset_confirm_button.on_click(reset_current_draft)
    preview_button.on_click(preview)
    remove_picked_button.on_click(remove_already_picked)
    commit_button.on_click(commit_batch)
    fast_button.on_click(lambda: start_model(False))
    deep_button.on_click(lambda: start_model(True))
    cancel_button.on_click(cancel_model)


    refresh_all()

    ui.run(
        title='Hail to Pitt · Draft Cockpit',
        port=int(port),
        reload=False,
        native=bool(native),
        window_size=(1600, 1000) if native else None,
        show=not native,
    )
