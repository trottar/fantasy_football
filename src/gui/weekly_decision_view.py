"""Local, read-only native weekly decision presentation for the portable NiceGUI.

A decision is never inferred from a screen: only existing native MC receipts are
presented.  This module does not import the operator, run MC, contact ESPN, or
write any file.  The GUI may refresh the view without changing an evidence epoch.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 64 * 1024 * 1024
CHANNEL_ORDER = (
    'lineup_availability', 'player_waiver_free_agent', 'dst_waiver_free_agent',
    'kicker_waiver_free_agent', 'ir_reserve_open_slot_injury_replacement',
    'trade_one_for_one_player', 'trade_multi_player_unequal',
    'trade_specialist_inclusive', 'prospective_capture_provenance',
)
TRADE_KEYS = frozenset(CHANNEL_ORDER[5:8])


class DecisionViewBlocked(ValueError):
    pass


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise DecisionViewBlocked(reason)


def read_json(path: Path) -> dict:
    need(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size <= MAX_FILE_BYTES,
         'PRIVATE_EVIDENCE_UNAVAILABLE_OR_UNSAFE')
    obj = json.loads(path.read_text(encoding='utf-8-sig'))
    need(isinstance(obj, dict), 'PRIVATE_EVIDENCE_NOT_OBJECT')
    return obj


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean_text(value: Any, limit: int = 100) -> str:
    # Local UI may display public athlete names, but never expose identifiers,
    # provider raw data, exception text, or arbitrary nested evidence content.
    if not isinstance(value, str) or not (1 <= len(value) <= limit) or not value.isprintable():
        return 'Unavailable'
    if any(c in value for c in ('\n', '\r', '\x00')):
        return 'Unavailable'
    return value


def _trade_asset_label(row: dict, singular: str, plural: str) -> str | None:
    """Only source-provided identities; never invent or infer trade assets."""
    names = row.get(plural)
    if isinstance(names, list) and 1 <= len(names) <= 2:
        if all(isinstance(n, str) and _clean_text(n, 100) == n for n in names):
            return ' + '.join(names)
        return None
    one = row.get(singular)
    if one is None:
        one = row.get({'give_name': 'give', 'receive_name': 'receive'}.get(singular, singular))
    if isinstance(one, str) and _clean_text(one, 130) == one:
        return one
    return None


def _specialist_row_key(row: dict) -> tuple | None:
    """Exact native numeric tuple for unique saved action-to-evidence matching."""
    fields = ('expected_offer_value', 'p_accept', 'our_delta_season_ppg',
              'partner_delta_season_ppg')
    values = tuple(_finite_number(row.get(k)) for k in fields)
    family = row.get('package_family')
    if None in values or not isinstance(family, str) or not family:
        return None
    return (family, str(row.get('classification')), *values)


def _resolve_trade_assets(key: str, row: dict, action_rows: list) -> tuple[str, str] | None:
    """Use receipt-retained native identities only; fail closed on ambiguity."""
    give = _trade_asset_label(row, 'give_name', 'give_names')
    receive = _trade_asset_label(row, 'receive_name', 'receive_names')
    if give and receive:
        return give, receive
    if key != 'trade_specialist_inclusive':
        return None
    target = _specialist_row_key(row)
    if target is None:
        return None
    matches = [r for r in action_rows if isinstance(r, dict)
               and _specialist_row_key(r) == target]
    if len(matches) != 1:
        return None
    give = _trade_asset_label(matches[0], 'give_name', 'give_names')
    receive = _trade_asset_label(matches[0], 'receive_name', 'receive_names')
    return (give, receive) if give and receive else None


def _finite_number(value: Any):
    import math
    if isinstance(value, bool):
        return None
    try:
        n = float(value)
    except (ValueError, TypeError):
        return None
    return n if math.isfinite(n) else None


def _bye_map(source: Path) -> dict:
    """Source-grounded official calendar, extracted as literal without importing code."""
    if not source.is_file() or source.is_symlink():
        return {}
    try:
        tree = ast.parse(source.read_text(encoding='utf-8-sig'))
        values = [node.value for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'OFFICIAL_2026_BYES'
                          for t in node.targets)]
        if len(values) != 1:
            return {}
        byes = ast.literal_eval(values[0])
        if not isinstance(byes, dict) or len(byes) != 32:
            return {}
        if not all(isinstance(k, str) and type(v) is int and 1 <= v <= 18
                   for k, v in byes.items()):
            return {}
        return byes
    except (OSError, ValueError, SyntaxError):
        return {}


def _verified_bye(name: str, *, week: int, native: dict, snapshot: dict,
                  league: dict, official: dict) -> bool:
    """Require three-way official/league/frozen-schedule and unique owned name."""
    if not official or not name:
        return False
    teamid = native.get('team_id')
    espn = snapshot.get('espn') or {}
    if espn.get('week') != week or espn.get('season') != 2026:
        return False
    teams = espn.get('teams') or []
    owned = [t for t in teams if isinstance(t, dict) and t.get('team_id') == teamid]
    if len(owned) != 1:
        return False
    players = [p for p in (owned[0].get('roster') or [])
               if isinstance(p, dict) and p.get('name') == name]
    if len(players) != 1:
        return False
    team = str(players[0].get('nfl_team') or '').upper()
    league_byes = league.get('bye_weeks_2026') or {}
    frozen_schedule = (snapshot.get('matchup_context') or {}).get('team_week') or {}
    scheduled = frozen_schedule.get(team)
    return (team in official and official[team] == week
            and str(league_byes.get(team)) == str(week)
            and isinstance(scheduled, dict)
            and scheduled.get(str(week)) is None)


def _parse_trial(runtime: Path) -> tuple[dict, dict, str]:
    folder = runtime / 'data/season_decisions'
    need(folder.is_dir() and not folder.is_symlink(), 'DECISION_DIRECTORY_MISSING')
    report_files = sorted(folder.glob('operator_v2_trial_*.report.json'),
                          key=lambda p: (p.stat().st_mtime_ns, p.name), reverse=True)
    for path in report_files[:12]:
        trial = read_json(path)
        if (trial.get('season') != 2026 or trial.get('week') not in range(1, 19)
                or trial.get('commissioning_trial') is not True
                or trial.get('transaction_authority') != 'NONE'
                or trial.get('espn_writes') is not False
                or trial.get('completed_phases') != ['CALENDAR','SYNC','CAPTURE','MC','REVIEW']):
            continue
        prefix = path.name[:-len('.report.json')]
        phase = read_json(folder / (prefix + '.mc.done.json'))
        facts = phase.get('facts') or {}
        sha = facts.get('receipt_sha256')
        need(isinstance(sha, str) and len(sha) == 64 and all(x in '0123456789abcdef' for x in sha),
             'NATIVE_RECEIPT_HASH_NOT_VALID')
        matched = [x for x in folder.glob('weekly_decision_receipt_*.json')
                   if x.is_file() and not x.is_symlink() and digest(x) == sha]
        need(len(matched) == 1, 'NATIVE_RECEIPT_NOT_UNIQUE_OR_MISSING')
        native = read_json(matched[0])
        need(native.get('week') == trial['week'] and native.get('season') == 2026,
             'NATIVE_RECEIPT_WEEK_MISMATCH')
        need((native.get('operational_health') or {}).get('status') == 'PASS',
             'NATIVE_OPERATIONAL_HEALTH_NOT_PASS')
        rows = native.get('channels') or []
        need(isinstance(rows, list) and len(rows) == 9 and
             {r.get('key') for r in rows if isinstance(r, dict)} == set(CHANNEL_ORDER),
             'NATIVE_NINE_CHANNEL_MATRIX_INVALID')
        return trial, native, sha
    raise DecisionViewBlocked('NO_VALID_COMPLETED_SUPERVISED_TRIAL')


def _frozen_trade_certification(runtime: Path, snapshot: dict, native: dict,
                                trial: dict) -> dict:
    """Reuse existing provenance-bound Slice A; no provider, MC, or writes.

    If the runtime's latest snapshot is not this receipt's frozen epoch, block
    instead of silently treating current roster state as historical authority.
    """
    import importlib
    import sys
    from ..weekly_trade_portfolio_gate import assemble

    need(snapshot.get('snapshot_utc') == (native.get('provenance') or {}).get('snapshot_utc'),
         'FROZEN_WEDNESDAY_SNAPSHOT_NOT_CURRENT_LATEST')
    need((snapshot.get('espn') or {}).get('week') == native.get('week'),
         'FROZEN_SNAPSHOT_WEEK_MISMATCH')
    base = runtime / 'data/season_predictions/closure'
    captures = []
    for path in sorted(base.glob(f"pregame_2026_w{native['week']:02d}_*.json")):
        if path.is_file() and not path.is_symlink():
            value = read_json(path)
            if value.get('snapshot_utc') == snapshot['snapshot_utc']:
                captures.append(value)
    need(len(captures) == 1, 'FROZEN_CAPTURE_EPOCH_NOT_UNIQUE')
    operations = runtime.parent / 'tools/operations'
    expected = {
        'action_certification.py': '4780d467874920333141f55ddf65ed20fb02ba61',
    }
    for file, oid in expected.items():
        path = operations / file
        need(path.is_file() and not path.is_symlink(), 'CERTIFICATION_SOURCE_MISSING')
        raw = path.read_bytes().removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
        need(blob == oid, 'CERTIFICATION_SOURCE_UNVERIFIED')
    loc = str(operations.resolve())
    if loc not in sys.path:
        sys.path.insert(0, loc)
    module = importlib.import_module('action_certification')
    need(Path(module.__file__).resolve() == (operations / 'action_certification.py').resolve(),
         'CERTIFICATION_IMPORT_ORIGIN_INVALID')
    cert = module.certify_receipt(snapshot, captures[0], native)
    return assemble(cert, native, trial)


def collect(runtime: Path) -> dict:
    """A private local presentation, never an ESPN transaction certificate."""
    need((runtime / 'VERSION').is_file() and
         (runtime / 'VERSION').read_text(encoding='utf-8-sig').strip() == '0.36',
         'COMMISSIONED_VERSION_REQUIRED')
    trial, native, sha = _parse_trial(runtime)
    root = runtime.parent
    snapshot = read_json(runtime / 'data/season_snapshots/latest.json')
    league = read_json(runtime / 'config/league.json')
    official = _bye_map(root / 'tools/operations/weekly_operator_calendar_evidence.py')
    rows = {r['key']: r for r in native['channels']}
    result = {
        'week': native['week'], 'receipt_hash_short': sha[:16],
        'slot': _clean_text(trial.get('slot'), 10),
        'observed_utc': _clean_text(trial.get('created_utc'), 45),
        'native_overall': _clean_text(native.get('overall_state'), 80),
        'trial_state': _clean_text(trial.get('operator_state'), 80),
        'health': 'PASS', 'action_authority': 'NONE',
        'review_blocker': _clean_text(trial.get('blocker'), 100),
        'channels': [], 'lineup': [], 'candidates': [], 'alternatives': [],
        'alternatives_available': False,
    }
    for key in CHANNEL_ORDER:
        r = rows[key]
        status = _clean_text(r.get('status'), 90)
        evidence = r.get('evidence') or {}
        if not isinstance(evidence, dict):
            evidence = {}
        count = None
        if key == 'player_waiver_free_agent':
            count = evidence.get('candidate_pool_evaluated')
        elif key in TRADE_KEYS:
            count = evidence.get('evaluated_reported')
        channel = {'name': key, 'status': status, 'evaluated': count,
                   'gap': _clean_text(r.get('gap')) if r.get('gap') else ''}
        result['channels'].append(channel)
        action = r.get('action') or {}
        native_offers = action.get('offers') if isinstance(action, dict) else None
        if not isinstance(native_offers, list):
            native_offers = []
        alt = evidence.get('evaluated_alternatives')
        if isinstance(alt, dict) and alt.get('authority') == 'OBSERVATION_ONLY':
            result['alternatives_available'] = True
            if key == 'player_waiver_free_agent':
                groups = alt.get('groups') or []
                entries = [(g.get('acquisition_state'), x)
                           for g in groups if isinstance(g, dict)
                           for x in (g.get('alternatives') or []) if isinstance(x, dict)]
            elif key in TRADE_KEYS:
                entries = [(key, x) for x in (alt.get('alternatives') or []) if isinstance(x, dict)]
            else:
                entries = []
            for label, row in entries[:24]:
                if key == 'player_waiver_free_agent':
                    desc = ('ADD ' + _clean_text(row.get('add'), 100) +
                            ' / DROP ' + _clean_text(row.get('drop'), 100))
                    score = _finite_number(row.get('expected_delta_utility'))
                    p = _finite_number(row.get('p_acquire'))
                else:
                    identities = _resolve_trade_assets(key, row, native_offers)
                    desc = (' -> '.join(identities) if identities else
                            'Trade assets not uniquely retained — do not act')
                    score = _finite_number(row.get('expected_offer_value'))
                    p = _finite_number(row.get('p_accept'))
                result['alternatives'].append({
                    'family': _clean_text(label, 70),
                    'description': desc,
                    'classification': _clean_text(row.get('classification'), 80),
                    'score': score, 'probability': p,
                    'stage': _clean_text(row.get('mc_stage'), 30) if key == 'player_waiver_free_agent' else '',
                    'futility_stop': row.get('futility_stop') is True,
                    'interval_p16': _finite_number(row.get('paired_mean_interval_p16')),
                    'interval_p84': _finite_number(row.get('paired_mean_interval_p84')),
                    'our_ppg': _finite_number(row.get('our_delta_season_ppg')),
                    'partner_ppg': _finite_number(row.get('partner_delta_season_ppg')),
                    'certified': False,
                })
        action = r.get('action') or {}
        if isinstance(action, dict):
            if key == 'player_waiver_free_agent':
                proposed = action.get('candidates') or []
            elif key in TRADE_KEYS:
                proposed = action.get('offers') or []
            else:
                proposed = action.get('authorized_actions') or []
            if isinstance(proposed, list):
                for p in proposed[:25]:
                    if not isinstance(p, dict):
                        continue
                    if key in TRADE_KEYS:
                        identities = _resolve_trade_assets(key, p, native_offers)
                        desc = (' -> '.join(identities) if identities else
                                'Trade assets not uniquely retained — do not act')
                        score = _finite_number(p.get('expected_offer_value'))
                        clas = _clean_text(p.get('classification'), 75)
                    elif key == 'player_waiver_free_agent':
                        desc = ('ADD ' + _clean_text(p.get('add_name'), 80) +
                                ' / DROP ' + _clean_text(p.get('drop_name'), 80))
                        score = _finite_number(p.get('expected_delta_utility'))
                        clas = _clean_text(p.get('combined_action_classification'), 75)
                    else:
                        desc = _clean_text(str(p.get('policy') or 'Specialist candidate'))
                        score, clas = None, 'CHANNEL_SPECIFIC'
                    result['candidates'].append({'family': key, 'description': desc,
                                                  'classification': clas, 'score': score,
                                                  'certified': False})
    result['candidates'].sort(key=lambda a: a['score'] if a['score'] is not None else float('-inf'),
                              reverse=True)
    queue = trial.get('queue') or []
    for q in queue:
        if not isinstance(q, dict) or q.get('family') != 'LINEUP':
            continue
        result['lineup_state'] = _clean_text(q.get('state'))
        for p in q.get('proposals') or []:
            if not isinstance(p, dict) or not isinstance(p.get('player'), dict):
                continue
            athlete = p['player']
            reason = _clean_text(p.get('state'))
            verified_bye = (p.get('direction') == 'BENCH'
                            and p.get('kickoff_utc') is None
                            and athlete.get('lineup_locked') is False
                            and _verified_bye(athlete.get('name'), week=native['week'],
                                              native=native, snapshot=snapshot, league=league,
                                              official=official))
            if verified_bye:
                reason = 'OFFICIAL_FROZEN_VERIFIED_BYE (native reviewer still blocked)'
            result['lineup'].append({'direction': _clean_text(p.get('direction'), 12),
                                     'name': _clean_text(athlete.get('name'), 90),
                                     'position': _clean_text(athlete.get('position'), 10),
                                     'state': reason})
    try:
        result['portfolio_gate'] = _frozen_trade_certification(runtime, snapshot, native, trial)
        result['portfolio_gate_blocker'] = None
    except (DecisionViewBlocked, ValueError, OSError, KeyError, TypeError, ImportError):
        result['portfolio_gate'] = None
        result['portfolio_gate_blocker'] = 'FROZEN_CERTIFICATION_INPUT_OR_SOURCE_NOT_VERIFIED'
    result['review'] = [
        {'family': _clean_text(q.get('family')), 'state': _clean_text(q.get('state'), 120)}
        for q in queue if isinstance(q, dict) and q.get('family') not in ('LINEUP',)
    ]
    return result


def render_panel(runtime: Path) -> None:
    """Invoked inside the existing NiceGUI page; renders on page load and refresh."""
    from nicegui import ui
    with ui.card().classes('w-full p-4'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Weekly MC evidence / action gating').classes('text-lg font-semibold')
            refresh = ui.button('Refresh saved decisions', icon='refresh')
        ui.label('Existing frozen native MC and read-only review only. Refresh never runs ESPN, capture, or MC.').classes('text-sm')
        area = ui.column().classes('w-full gap-3')

        def redraw() -> None:
            area.clear()
            with area:
                try:
                    data = collect(runtime)
                except (DecisionViewBlocked, ValueError, OSError, KeyError, TypeError):
                    ui.label('No validated native weekly receipt available. No action authority.').classes('text-amber-400')
                    return
                ui.label(f"Week {data['week']} · {data['slot']} saved report {data['observed_utc']} · native {data['native_overall']} · health {data['health']}").classes('font-semibold')
                ui.label(f"Source {data['receipt_hash_short']}… · trial {data['trial_state']} · ESPN authority NONE").classes('text-sm')
                ui.label('The native model selects football actions. Live legality and approval are independent.').classes('text-sm')
                with ui.card().classes('w-full p-3'):
                    ui.label('Lineup — native proposals / live constraints').classes('font-semibold')
                    if not data['lineup']:
                        ui.label('No saved lineup proposal.')
                    for p in data['lineup']:
                        ui.label(f"{p['direction']} {p['name']} ({p['position']}): {p['state']}")
                with ui.card().classes('w-full p-3'):
                    ui.label('Acquisitions and trades — native decisions').classes('font-semibold')
                    if data['candidates']:
                        for p in data['candidates']:
                            delta = f" · native value {p['score']:+.4f}" if p['score'] is not None else ''
                            ui.label(f"{p['family']}: {p['description']} · {p['classification']}{delta} · UNCERTIFIED")
                    else:
                        ui.label('No native ACTIONABLE waiver or trade offer in this evaluated frontier. This is not evidence that every legal transaction was fully simulated.')
                with ui.card().classes('w-full p-3'):
                    ui.label('Evaluated waiver / trade alternatives — original MC classifications').classes('font-semibold')
                    if not data['alternatives_available']:
                        ui.label('This native receipt predates alternative retention. Evaluated rejected and close candidates were not saved; no historical recovery or new MC was attempted.')
                    elif not data['alternatives']:
                        ui.label('No evaluated candidate rows were retained for this native receipt. See screen and predictive frontier counts.')
                    else:
                        for p in data['alternatives']:
                            delta = f" · native value {p['score']:+.4f}" if p['score'] is not None else ' · value unavailable'
                            prob = f" · behavior P {p['probability']:.1%}" if p['probability'] is not None else ''
                            stage = f" · {p['stage']}" if p['stage'] and p['stage'] != 'Unavailable' else ''
                            parked = ' · stopped for futility at reported MC stage' if p['futility_stop'] else ''
                            interval = (f" · conditional paired mean interval [{p['interval_p16']:+.4f}, {p['interval_p84']:+.4f}]"
                                        if p['interval_p16'] is not None and p['interval_p84'] is not None else '')
                            ppg = (f" · our/partner ΔPPG {p['our_ppg']:+.2f}/{p['partner_ppg']:+.2f}"
                                   if p['our_ppg'] is not None and p['partner_ppg'] is not None else '')
                            ui.label(f"{p['family']}: {p['description']} · {p['classification']}{delta}{interval}{ppg}{prob}{stage}{parked} · UNCERTIFIED")
                    ui.label('Expected waiver value includes acquisition uncertainty; the paired interval is conditional on acquisition. Trade response probabilities are uncalibrated behavior estimates.').classes('text-sm')
                with ui.card().classes('w-full p-3'):
                    ui.label('Joint trade safety / certification — BLOCKED until verified').classes('font-semibold')
                    portfolio = data.get('portfolio_gate')
                    if not portfolio:
                        ui.label('Frozen certification cannot be verified for this receipt. No trade may be promoted to approval.')
                    else:
                        ui.label(f"{portfolio['candidate_count']} trade candidates; {portfolio['conflict_count']} potentially incompatible pairs; 0 approval-ready actions.")
                        for p in portfolio['candidates']:
                            reasons = ', '.join(p['blockers'][:5])
                            drops = ' + '.join(p['mandatory_user_drops']) or 'none in native model'
                            qbs = ' + '.join(p['remaining_qbs']) or 'none'
                            ui.label(f"#{p['ordinal']} {p['give_label']} -> {p['receive_label']}: BLOCKED | native drops {drops} | retained QBs {qbs} | {reasons}")
                        for pair in portfolio['conflicts']:
                            ui.label(f"Candidates #{pair['first_ordinal']} and #{pair['second_ordinal']}: {pair['kind']} — joint execution unverified")
                        ui.label('No-action and alternate-drop paired comparisons, trade effective timing, future fills, injury contingencies and current ESPN legality remain independent mandatory gates. No offer is approved.')
                with ui.card().classes('w-full p-3'):
                    ui.label('Nine-channel completion and evaluation scope').classes('font-semibold')
                    for c in data['channels']:
                        n = f" · evaluated {c['evaluated']}" if c['evaluated'] is not None else ''
                        ui.label(f"{c['name']}: {c['status']}{n}" + (f" · GAP {c['gap']}" if c['gap'] else ''))
                with ui.card().classes('w-full p-3'):
                    ui.label('Live reconciliation / unresolved certification').classes('font-semibold')
                    for q in data['review']:
                        ui.label(f"{q['family']}: {q['state']}")
                    ui.label('No ESPN transactions are submitted by this page.')
        refresh.on_click(redraw)
        redraw()
