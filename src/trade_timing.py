from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

import numpy as np

from .season_utility import week_weights


class TradeTimingCoverageError(RuntimeError):
    """Raised when decision-time evidence cannot authorize a trade timing state."""


@dataclass(frozen=True)
class TradeTiming:
    current_week: int
    effective_week: int
    current_week_effective: bool
    trade_review_hours: int
    lineup_locktime_type: str
    roster_locktime_type: str
    reasons: tuple[str, ...]
    lock_evidence: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _snapshot_utc(snapshot: Mapping[str, Any]) -> datetime:
    raw = snapshot.get("snapshot_utc")
    if not raw:
        raise TradeTimingCoverageError("snapshot_utc missing for trade timing")
    try:
        value = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise TradeTimingCoverageError("snapshot_utc invalid for trade timing") from exc
    if value.tzinfo is None:
        raise TradeTimingCoverageError("snapshot_utc must be timezone-aware")
    return value.astimezone(timezone.utc)


def require_trade_settings(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    espn = snapshot.get("espn", snapshot)
    if not isinstance(espn, Mapping):
        raise TradeTimingCoverageError("ESPN snapshot block missing")
    settings = espn.get("transaction_settings")
    if not isinstance(settings, Mapping):
        raise TradeTimingCoverageError(
            "normalized ESPN transaction_settings missing; fresh snapshot required"
        )

    raw_review = settings.get("trade_review_hours")
    if isinstance(raw_review, bool):
        raise TradeTimingCoverageError("trade_review_hours is invalid")
    try:
        review_hours = int(raw_review)
    except (TypeError, ValueError) as exc:
        raise TradeTimingCoverageError("trade_review_hours missing or invalid") from exc
    if review_hours < 0:
        raise TradeTimingCoverageError("trade_review_hours cannot be negative")

    lineup_lock = str(settings.get("lineup_locktime_type") or "").strip()
    roster_lock = str(settings.get("roster_locktime_type") or "").strip()
    if not lineup_lock or not roster_lock:
        raise TradeTimingCoverageError(
            "normalized ESPN lineup/roster lock-time settings are incomplete"
        )

    return {
        **dict(settings),
        "trade_review_hours": review_hours,
        "lineup_locktime_type": lineup_lock,
        "roster_locktime_type": roster_lock,
    }


def _pid(player: Mapping[str, Any]) -> int | None:
    try:
        value = player.get("espn_id")
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def resolve_trade_timing(
    snapshot: Mapping[str, Any],
    current_week: int,
    affected_assets: Iterable[tuple[str, Mapping[str, Any], Any]],
) -> TradeTiming:
    """Resolve the earliest week in which a proposed ownership change may exist.

    v0.X is deliberately conservative. Any positive configured ESPN trade-review
    window defers modeled ownership until the next scoring week; commissioner early
    processing is never assumed. With zero review hours, every affected asset must
    have complete decision-time lock evidence. A locked asset defers the package to
    the next week; unresolved timing fails closed.
    """
    settings = require_trade_settings(snapshot)
    week = int(current_week)
    if week < 1 or week > 17:
        raise TradeTimingCoverageError(f"current trade week out of range: {week}")

    review_hours = int(settings["trade_review_hours"])
    next_week = min(18, week + 1)
    if review_hours > 0:
        return TradeTiming(
            current_week=week,
            effective_week=next_week,
            current_week_effective=False,
            trade_review_hours=review_hours,
            lineup_locktime_type=str(settings["lineup_locktime_type"]),
            roster_locktime_type=str(settings["roster_locktime_type"]),
            reasons=(f"ESPN_TRADE_REVIEW_WINDOW_HOURS={review_hours}",),
            lock_evidence=(),
        )

    decision_time = _snapshot_utc(snapshot)
    evidence: list[dict[str, Any]] = []
    any_locked = False
    for role, player_raw, ctx in affected_assets:
        player = dict(player_raw)
        pid = _pid(player)
        state = "UNKNOWN"
        source = "UNKNOWN"
        kickoff_utc: str | None = None

        if bool(player.get("lineup_locked")):
            state = "LOCKED"
            source = "ESPN_LINEUP_LOCKED"
        else:
            try:
                timing = ctx.lock_timing(player, week)
            except Exception as exc:
                raise TradeTimingCoverageError(
                    f"trade lock timing failed for {role}:{pid}:{type(exc).__name__}"
                ) from exc
            kickoff = getattr(timing, "kickoff", None)
            source = str(getattr(timing, "source", None) or "UNKNOWN")
            if kickoff is None:
                raise TradeTimingCoverageError(
                    f"trade lock timing unresolved for {role}:{pid}:{source}"
                )
            if kickoff.tzinfo is None:
                raise TradeTimingCoverageError(
                    f"trade lock kickoff is naive for {role}:{pid}:{source}"
                )
            kickoff = kickoff.astimezone(timezone.utc)
            kickoff_utc = kickoff.isoformat()
            state = "LOCKED" if kickoff <= decision_time else "UNLOCKED"

        any_locked = any_locked or state == "LOCKED"
        evidence.append({
            "role": str(role),
            "espn_id": pid,
            "name": player.get("name"),
            "position": player.get("position"),
            "state": state,
            "source": source,
            "kickoff_utc": kickoff_utc,
        })

    if not evidence:
        raise TradeTimingCoverageError("trade timing received no affected assets")

    effective_week = next_week if any_locked else week
    reasons = (
        ("AFFECTED_ASSET_ALREADY_LOCKED",)
        if any_locked
        else ("ZERO_REVIEW_ALL_AFFECTED_ASSETS_UNLOCKED",)
    )
    return TradeTiming(
        current_week=week,
        effective_week=effective_week,
        current_week_effective=effective_week == week,
        trade_review_hours=review_hours,
        lineup_locktime_type=str(settings["lineup_locktime_type"]),
        roster_locktime_type=str(settings["roster_locktime_type"]),
        reasons=reasons,
        lock_evidence=tuple(evidence),
    )


def splice_effective_week(
    baseline: np.ndarray,
    after: np.ndarray,
    effective_week: int,
) -> np.ndarray:
    base = np.asarray(baseline, dtype=float)
    post = np.asarray(after, dtype=float)
    if base.shape != post.shape:
        raise ValueError(
            f"trade temporal splice shape mismatch baseline={base.shape} after={post.shape}"
        )
    if base.ndim != 2:
        raise ValueError("trade temporal splice requires scenarios x weeks arrays")
    week = int(effective_week)
    if week < 1:
        raise ValueError("trade effective week must be positive")
    out = np.array(base, copy=True)
    cut = min(max(week - 1, 0), out.shape[1])
    if cut < out.shape[1]:
        out[:, cut:] = post[:, cut:]
    return out


def season_ppg_from_weekly(
    weekly: np.ndarray,
    league: Mapping[str, Any],
    current_week: int,
) -> np.ndarray:
    arr = np.asarray(weekly, dtype=float)
    if arr.ndim != 2:
        raise ValueError("trade season PPG requires scenarios x weeks array")
    weeks, weights = week_weights(dict(league))
    weights = np.asarray(weights, dtype=float)
    weights[weeks < int(current_week)] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= int(current_week)] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    return np.sum(arr * weights[None, :], axis=1) / norm
