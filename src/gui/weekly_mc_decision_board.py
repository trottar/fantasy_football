"""Human-first, read-only board from already-saved native weekly MC.

This is a *presentation*, not a football model, live ESPN action certificate,
transaction planner, prospective capture, scheduler, or MC executor.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import math
from typing import Any

FIRST_WEEK_MONDAY = date(2026, 9, 7)
DST_END_UTC = datetime(2026, 11, 1, 6, tzinfo=timezone.utc)
FAMILY_RANK = {'LINEUP': 0, 'IR': 1, 'PLAYER': 2, 'DST': 3,
               'K': 4, 'TRADE_PLAYER': 5, 'TRADE_SPECIALIST': 6}
FAMILY_LABEL = {'LINEUP': 'Lineup', 'IR': 'Injury / IR / roster capacity',
                'PLAYER': 'QB/RB/WR/TE acquisitions', 'DST': 'D/ST',
                'K': 'Kicker', 'TRADE_PLAYER': 'Player trades',
                'TRADE_SPECIALIST': 'Specialist-inclusive trades'}


def _number(v: Any) -> float | None:
    if v is None or isinstance(v, bool):
        return None
    try:
        n = float(v)
    except (TypeError, ValueError, OverflowError):
        return None
    return n if math.isfinite(n) else None


def _text(v: Any, limit: int = 230) -> str:
    if not isinstance(v, str) or not v or len(v) > limit or not v.isprintable():
        return 'Unavailable'
    return v if all(c not in v for c in '\r\n\x00') else 'Unavailable'


def week_at(now: datetime) -> int:
    """Match the existing v2 operator's 2026 Monday/Eastern week convention."""
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError('AWARE_CLOCK_REQUIRED')
    utc = now.astimezone(timezone.utc)
    offset = -5 if utc >= DST_END_UTC else -4
    local = utc.astimezone(timezone(timedelta(hours=offset))).date()
    return (local - FIRST_WEEK_MONDAY).days // 7 + 1


def _family(label: Any) -> str | None:
    name = str(label or '').upper()
    if name in ('WAIVERS', 'FREEAGENT', 'FREE_AGENT', 'PLAYER_ACQUISITION'):
        return 'PLAYER'
    if 'PLAYER_WAIVER' in name:
        return 'PLAYER'
    if 'TRADE_SPECIALIST' in name:
        return 'TRADE_SPECIALIST'
    if 'TRADE_' in name or name == 'TRADES':
        return 'TRADE_PLAYER'
    if 'DST' in name or name == 'DEFENSE':
        return 'DST'
    if name in ('K', 'KICKER') or 'KICKER' in name:
        return 'K'
    if name.startswith('IR') or 'INJURY_REPLACEMENT' in name:
        return 'IR'
    if 'LINEUP' in name:
        return 'LINEUP'
    return None


def _qualifies_candidate(row: dict) -> bool:
    s = str(row.get('classification') or '').upper()
    return 'ACTION' in s or 'OFFER' in s or 'ADD' in s


def _score_line(row: dict) -> str:
    n = _number(row.get('score'))
    fmt = f'MC model score {n:+.4f}' if n is not None else 'MC score not retained'
    low = _number(row.get('interval_p16'))
    high = _number(row.get('interval_p84'))
    if low is not None and high is not None and low <= high:
        fmt += f' | conditional paired-mean interval [{low:+.4f}, {high:+.4f}]'
    p = _number(row.get('probability'))
    if p is not None and 0 <= p <= 1:
        fmt += f' | behavior probability {p:.0%} (not calibrated action guarantee)'
    return fmt


def _item(family: str, description: str, source: str, state: str,
          score: float | None = None, detail: str = '', classification: str = '') -> dict:
    return {'family': family, 'family_label': FAMILY_LABEL[family],
            'description': _text(description), 'source': source, 'state': state,
            'score': score, 'detail': _text(detail, 300) if detail else '',
            'classification': _text(classification, 90) if classification else ''}


def build_board(data: dict, *, now: datetime | None = None) -> dict:
    """Prioritize observations without asserting cross-channel score comparability.

    Lineup/IR safety is shown first, then players, D/ST, K, and trades. Numeric
    model scores order entries only *inside* the same group. Existing MC labels
    remain source labels; no candidate becomes an ESPN authorization.
    """
    now = now or datetime.now(timezone.utc)
    week = week_at(now)
    saved = data.get('week')
    current = type(saved) is int and saved == week
    channels = data.get('channels') if isinstance(data.get('channels'), list) else []
    unique = {r.get('name'): str(r.get('status') or '') for r in channels
              if isinstance(r, dict) and isinstance(r.get('name'), str)}
    healthy_matrix = (len(channels) == 9 and len(unique) == 9 and
                      all(v.startswith('PASS') for v in unique.values()))
    gaps = [r['name'] for r in channels if isinstance(r, dict) and
            not str(r.get('status') or '').startswith('PASS') and 'name' in r]
    # Do not treat an absent or incomplete 9-channel matrix as a roster-wide HOLD.
    if len(unique) != 9:
        gaps.append('NINE_CHANNEL_MATRIX_MISSING_OR_DUPLICATE')
    items = []
    seen = set()
    offer_by_key = {}
    for r in data.get('lineup') or []:
        if not isinstance(r, dict):
            continue
        direction, name = _text(r.get('direction')), _text(r.get('name'))
        state = _text(r.get('state'))
        if direction not in ('START', 'BENCH'):
            continue
        key = ('LINEUP', direction, name)
        if key in seen:
            continue
        seen.add(key)
        items.append(_item('LINEUP', f'{direction} {name} ({_text(r.get("position"))})',
                           'FROZEN_NATIVE_LINEUP', 'VERIFY_LOCK_AND_ESPN_SLOT',
                           detail=state))
    reviews = data.get('review') if isinstance(data.get('review'), list) else []
    for q in reviews:
        if not isinstance(q, dict):
            continue
        family = _family(q.get('family'))
        state = _text(q.get('state'), 120)
        if family == 'IR' and ('HOLD' not in state or 'INCOMPLETE' in state):
            key = ('IR', state)
            if key not in seen:
                seen.add(key)
                items.append(_item('IR', 'Check injury / IR / open-slot state',
                                   'NATIVE_REVIEW', 'REVIEW_CAPACITY_AND_ELIGIBILITY',
                                   detail=state))
    candidates = data.get('candidates') if isinstance(data.get('candidates'), list) else []
    alternatives = data.get('alternatives') if isinstance(data.get('alternatives'), list) else []
    # The saved ACTION and alternative rows may describe the same transaction.
    # Deduplicate by grounded description *within family* and retain ACTION first.
    for source, source_rows in [('NATIVE_ACTION', candidates), ('NATIVE_EVALUATED_ALTERNATIVE', alternatives)]:
        for row in source_rows:
            if not isinstance(row, dict):
                continue
            family = _family(row.get('family'))
            if family not in FAMILY_RANK or family in ('LINEUP', 'IR'):
                continue
            desc = _text(row.get('description'))
            if desc == 'Unavailable' or 'Unavailable' in desc or 'not uniquely retained' in desc.lower():
                continue
            classification = _text(row.get('classification'), 90)
            key = (family, desc)
            if key in seen:
                # A native ACTION and its retained MC alternative may carry
                # complementary evidence. Preserve the ACTION identity, but
                # attach its alternative's uncertainty/behavior interval.
                if source == 'NATIVE_EVALUATED_ALTERNATIVE' and key in offer_by_key:
                    prior = offer_by_key[key]
                    if prior['source'] == 'NATIVE_ACTION':
                        prior['detail'] = _score_line(row)
                        if prior['score'] is None:
                            prior['score'] = _number(row.get('score'))
                continue
            seen.add(key)
            score = _number(row.get('score'))
            actionable = source == 'NATIVE_ACTION' or _qualifies_candidate(row)
            state = ('MODEL_OPPORTUNITY_ESPN_UNVERIFIED' if actionable else
                     'MODEL_ALTERNATIVE_NOT_RECOMMENDED')
            if family.startswith('TRADE'):
                state = 'TRADE_RISK_AND_ESPN_UNVERIFIED'
            if 'Specialist candidate' in desc:
                state = 'POLICY_RETAINED_BUT_ASSET_IDENTITY_UNAVAILABLE'
            if row.get('futility_stop') is True:
                state = 'EVALUATION_STOPPED_FOR_FUTILITY'
            added = _item(family, desc, source, state, score=score,
                          detail=_score_line(row), classification=classification)
            items.append(added)
            offer_by_key[key] = added
    # A missing concrete candidate cannot be fabricated from aggregate screen counts.
    for r in channels:
        if not isinstance(r, dict):
            continue
        fam = _family(r.get('name'))
        if fam in ('DST', 'K', 'PLAYER', 'IR') and not any(x['family'] == fam for x in items):
            status = _text(r.get('status'))
            if status.startswith('INCOMPLETE') or status.startswith('BLOCKED'):
                items.append(_item(fam, f'{FAMILY_LABEL[fam]}: no supported candidate detail',
                                   'NATIVE_CHANNEL_STATUS', 'COVERAGE_GAP', detail=status))
    items.sort(key=lambda r: (FAMILY_RANK[r['family']],
                              0 if r['source'] in ('FROZEN_NATIVE_LINEUP', 'NATIVE_REVIEW', 'NATIVE_ACTION') else 1,
                              -(r['score'] if r['score'] is not None else -1e30),
                              r['description']))
    for ordinal, item in enumerate(items, 1):
        item['ordinal'] = ordinal
        item['state'] = ('HISTORICAL_DO_NOT_ACT' if not current else item['state'])
    if not current:
        state = 'SAVED_WEEK_NOT_CURRENT_DO_NOT_ACT'
    elif not healthy_matrix:
        state = 'CURRENT_MC_INCOMPLETE_REVIEW_ONLY'
    elif not items:
        state = 'CURRENT_MC_NO_RETAINED_CANDIDATES_NOT_ROSTER_WIDE_HOLD'
    else:
        state = 'CURRENT_MC_LEADS_ESPN_UNVERIFIED'
    return {'week_now': week, 'week_saved': saved, 'current_week': current,
            'state': state, 'items': items, 'total_candidates': len(items),
            'channel_gaps': sorted(set(gaps)), 'channel_statuses': unique,
            'native_overall': _text(data.get('native_overall')),
            'trial_state': _text(data.get('trial_state')),
            'review_blocker': _text(data.get('review_blocker')),
            'action_authority': 'NONE', 'espn_writes': False,
            'ranking_method': 'SAFETY_FIRST_THEN_WITHIN_CHANNEL_MODEL_SCORE',
            'explanation': ('Fixed family-priority order for readiness; numeric scores compared '
                            'only within the same channel. Native MC evidence, not verified '
                            'ESPN execution. No automatic submissions.')}


def format_board(board: dict, *, limit: int = 15) -> str:
    """Readable local console report; never fetches data or mutates state."""
    header = [f"WEEKLY MC DECISION BOARD | week now {board['week_now']} | saved week {board['week_saved']}",
              f"STATE={board['state']} | ESPN_ACTION_AUTHORITY=NONE",
              board['explanation']]
    for row in board['items'][:max(0, min(limit, 40))]:
        header.append(f"#{row['ordinal']} [{row['family_label']}] {row['description']} | {row['state']}")
        if row['detail']:
            header.append('    '+row['detail'])
    for gap in board['channel_gaps']:
        header.append('MISSING_COVERAGE='+gap)
    if len(board['items']) > limit:
        header.append(f"OTHER_RETAINED_ROWS={len(board['items'])-limit}")
    return '\n'.join(header)
