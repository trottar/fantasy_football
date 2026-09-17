from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import math
from typing import Any
from zoneinfo import ZoneInfo

from .weekly_manager import HARD_UNAVAILABLE_STATUSES, active_probability, availability_status, status_observations

EASTERN = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


@dataclass(frozen=True)
class AvailabilityEvidenceItem:
    source: str
    kind: str
    value: str
    normalized: str | None = None
    active_likelihood_ratio: float = 1.0
    full_likelihood_ratio: float = 1.0
    used: bool = False
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "kind": self.kind,
            "value": self.value,
            "normalized": self.normalized,
            "active_likelihood_ratio": self.active_likelihood_ratio,
            "full_likelihood_ratio": self.full_likelihood_ratio,
            "used": self.used,
            "note": self.note,
        }


@dataclass(frozen=True)
class AvailabilityStateModel:
    status: str
    status_source: str
    p_active: float
    p_full_given_active: float
    p_out: float
    p_limited: float
    p_full: float
    limited_workload_fraction: float
    base_p_active: float = 1.0
    base_p_full_given_active: float = 1.0
    evidence_level: str = "STATUS_ONLY"
    posterior_method: str = "STATUS_PRIOR"
    calibration_status: str = "UNCALIBRATED"
    practice_source: str | None = None
    practice_sequence: tuple[str, ...] = ()
    hours_to_kickoff: float | None = None
    evidence: tuple[AvailabilityEvidenceItem, ...] = ()

    @property
    def expected_workload_given_active(self) -> float:
        return (
            self.p_full_given_active
            + (1.0 - self.p_full_given_active) * self.limited_workload_fraction
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "status_source": self.status_source,
            "p_active": self.p_active,
            "p_full_given_active": self.p_full_given_active,
            "p_out": self.p_out,
            "p_limited": self.p_limited,
            "p_full": self.p_full,
            "limited_workload_fraction": self.limited_workload_fraction,
            "expected_workload_given_active": self.expected_workload_given_active,
            "base_p_active": self.base_p_active,
            "base_p_full_given_active": self.base_p_full_given_active,
            "evidence_level": self.evidence_level,
            "posterior_method": self.posterior_method,
            "calibration_status": self.calibration_status,
            "practice_source": self.practice_source,
            "practice_sequence": list(self.practice_sequence),
            "hours_to_kickoff": self.hours_to_kickoff,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class LockTiming:
    kickoff: datetime | None
    reveal_time: datetime | None
    lock_group: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kickoff_utc": self.kickoff.astimezone(UTC).isoformat() if self.kickoff else None,
            "kickoff_et": self.kickoff.astimezone(EASTERN).isoformat() if self.kickoff else None,
            "reveal_utc": self.reveal_time.astimezone(UTC).isoformat() if self.reveal_time else None,
            "reveal_et": self.reveal_time.astimezone(EASTERN).isoformat() if self.reveal_time else None,
            "lock_group": self.lock_group,
            "source": self.source,
        }


def _bounded(value: Any, default: float) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = float(default)
    return min(max(x, 0.0), 1.0)


def _positive(value: Any, default: float = 1.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = float(default)
    if not math.isfinite(x) or x <= 0:
        return float(default)
    return x


def _posterior_from_likelihood_ratios(prior: float, ratios: list[float]) -> float:
    """Bayesian odds update using explicit, auditable likelihood-ratio knobs.

    v0.27's likelihood ratios are deliberately tagged as uncalibrated priors.  The
    architecture is Bayesian/provenance-aware now; empirical calibration is learned
    from observed weekly outcomes later rather than silently pretending these ratios
    are historical estimates.
    """
    p = min(max(float(prior), 1e-6), 1.0 - 1e-6)
    odds = p / (1.0 - p)
    for ratio in ratios:
        odds *= _positive(ratio, 1.0)
    posterior = odds / (1.0 + odds)
    return min(max(float(posterior), 0.001), 0.999)


def _practice_key(value: Any) -> str | None:
    text = " ".join(str(value or "").strip().upper().replace("-", " ").split())
    if not text or text in {"N/A", "NA", "NONE", "NULL", "-", "NOT LISTED"}:
        return None
    compact = text.replace(" ", "")
    if compact in {"DNP", "DIDNOTPARTICIPATE", "DIDNOTPRACTICE", "NOPARTICIPATION"}:
        return "DNP"
    if compact in {"LP", "LIMITED", "LIMITEDPARTICIPATION", "LIMITEDPRACTICE"}:
        return "LIMITED"
    if compact in {"FP", "FULL", "FULLPARTICIPATION", "FULLPRACTICE"}:
        return "FULL"
    # REST/veteran-rest and other administrative labels are context, not injury evidence.
    return None


def _official_practice_sequence(player: dict[str, Any]) -> tuple[str, ...]:
    practice = player.get("official_practice")
    if not isinstance(practice, dict) or not practice:
        return ()
    day_order = {"wed": 0, "thu": 1, "fri": 2, "sat": 3, "sun": 4, "mon": 5}
    rows: list[tuple[int, str, str]] = []
    for raw_key, raw_value in practice.items():
        key = str(raw_key).casefold()
        order = next((rank for day, rank in day_order.items() if day in key), 99)
        normalized = _practice_key(raw_value)
        if normalized:
            rows.append((order, str(raw_key), normalized))
    rows.sort(key=lambda item: (item[0], item[1]))
    return tuple(item[2] for item in rows)


def _practice_sequence(player: dict[str, Any]) -> tuple[str | None, tuple[str, ...]]:
    official = _official_practice_sequence(player)
    if official:
        return "NFL_OFFICIAL", official
    sleeper = _practice_key(player.get("sleeper_practice_participation"))
    if sleeper:
        return "SLEEPER", (sleeper,)
    return None, ()


def _practice_trend(sequence: tuple[str, ...]) -> str | None:
    if len(sequence) < 2:
        return None
    score = {"DNP": 0, "LIMITED": 1, "FULL": 2}
    vals = [score[x] for x in sequence if x in score]
    if len(vals) < 2:
        return None
    if vals[-1] > vals[0]:
        return "IMPROVING"
    if vals[-1] < vals[0]:
        return "WORSENING"
    if all(v == 0 for v in vals):
        return "STABLE_DNP"
    if all(v == 1 for v in vals):
        return "STABLE_LIMITED"
    if all(v == 2 for v in vals):
        return "STABLE_FULL"
    return "MIXED"


def _lr_pair(mapping: Any, key: str) -> tuple[float, float]:
    row = mapping.get(key, {}) if isinstance(mapping, dict) else {}
    if not isinstance(row, dict):
        row = {}
    return _positive(row.get("active", 1.0)), _positive(row.get("full", 1.0))


def _availability_evidence(
    player: dict[str, Any],
    model: dict[str, Any],
    *,
    status: str,
    status_source: str,
    hours_to_kickoff: float | None,
) -> tuple[str, str | None, tuple[str, ...], tuple[AvailabilityEvidenceItem, ...], list[float], list[float]]:
    cfg = model.get("weekly_manager", {})
    lr_cfg = cfg.get("availability_evidence_likelihood_ratios", {})
    practice_cfg = lr_cfg.get("practice", {}) if isinstance(lr_cfg, dict) else {}
    trend_cfg = lr_cfg.get("practice_trend", {}) if isinstance(lr_cfg, dict) else {}

    evidence: list[AvailabilityEvidenceItem] = []
    active_lrs: list[float] = []
    full_lrs: list[float] = []

    # Preserve the reconciled source observations even when no quantitative update is
    # made. This exposes conflicts rather than merging away provenance.
    observations = status_observations(player)
    if observations:
        for source, value in observations.items():
            evidence.append(AvailabilityEvidenceItem(
                source=source,
                kind="GAME_STATUS",
                value=str(value),
                normalized=str(value),
                used=False,
                note="resolved into the status prior; not multiplied again",
            ))
    else:
        evidence.append(AvailabilityEvidenceItem(
            source="DEFAULT",
            kind="GAME_STATUS",
            value=status,
            normalized=status,
            used=False,
            note="no recognized external weekly designation; default status prior",
        ))

    practice_source, sequence = _practice_sequence(player)
    if practice_source and sequence:
        source_cfg = practice_cfg.get(practice_source, {}) if isinstance(practice_cfg, dict) else {}
        latest = sequence[-1]
        a_lr, f_lr = _lr_pair(source_cfg, latest)
        active_lrs.append(a_lr)
        full_lrs.append(f_lr)
        evidence.append(AvailabilityEvidenceItem(
            source=practice_source,
            kind="PRACTICE_LATEST",
            value=latest,
            normalized=latest,
            active_likelihood_ratio=a_lr,
            full_likelihood_ratio=f_lr,
            used=True,
            note="latest practice state; official practice supersedes Sleeper practice",
        ))
        trend = _practice_trend(sequence)
        if trend:
            a_lr, f_lr = _lr_pair(trend_cfg, trend)
            active_lrs.append(a_lr)
            full_lrs.append(f_lr)
            evidence.append(AvailabilityEvidenceItem(
                source=practice_source,
                kind="PRACTICE_TREND",
                value="→".join(sequence),
                normalized=trend,
                active_likelihood_ratio=a_lr,
                full_likelihood_ratio=f_lr,
                used=(abs(a_lr - 1.0) > 1e-12 or abs(f_lr - 1.0) > 1e-12),
                note="single trajectory update avoids treating correlated daily practices as independent evidence",
            ))
        evidence_level = "OFFICIAL_PRACTICE" if practice_source == "NFL_OFFICIAL" else "SLEEPER_PRACTICE"
    elif status_source == "DEFAULT":
        evidence_level = "DEFAULT_PRIOR"
    else:
        evidence_level = "STATUS_ONLY"

    if player.get("official_injury"):
        evidence.append(AvailabilityEvidenceItem(
            source="NFL_OFFICIAL",
            kind="INJURY_CONTEXT",
            value=str(player.get("official_injury")),
            used=False,
            note="retained for audit/calibration; no injury-type likelihood ratio in v0.27",
        ))
    injury_start = player.get("sleeper_injury_start_date")
    if injury_start:
        evidence.append(AvailabilityEvidenceItem(
            source="SLEEPER",
            kind="INJURY_START_DATE",
            value=str(injury_start),
            used=False,
            note="retained for future calibration; does not alter v0.27 posterior",
        ))
    if hours_to_kickoff is not None:
        evidence.append(AvailabilityEvidenceItem(
            source="NFLVERSE_SCHEDULE",
            kind="HOURS_TO_KICKOFF",
            value=f"{float(hours_to_kickoff):.1f}",
            used=False,
            note="recorded at decision time for calibration; no uncalibrated timing multiplier applied",
        ))

    return evidence_level, practice_source, sequence, tuple(evidence), active_lrs, full_lrs


def availability_state_model(
    player: dict[str, Any],
    model: dict[str, Any],
    *,
    p_active_override: float | None = None,
    hours_to_kickoff: float | None = None,
) -> AvailabilityStateModel:
    """Return an evidence-conditioned OUT / ACTIVE_LIMITED / ACTIVE_FULL model.

    v0.27 preserves the commissioned v0.26 state decomposition while replacing the
    generic status-only probability with a provenance-aware posterior.  The status
    designation supplies the prior.  When present, the *latest* practice state plus
    one trajectory summary update the prior in Bayesian odds space.  NFL.com practice
    supersedes Sleeper practice to avoid correlated double counting.

    The likelihood-ratio knobs are explicitly marked UNCALIBRATED. They are intended
    as transparent priors until historical/weekly closure provides empirical values.
    """
    status, source = availability_status(player)
    cfg = model.get("weekly_manager", {})

    # Status priors remain a stable, auditable fallback. p_active_override is used by
    # future-week season simulation; current-week UtilityContext calls this model
    # without overriding the evidence-conditioned posterior.
    if status in HARD_UNAVAILABLE_STATUSES or bool(player.get("is_bye_week")):
        base_p_active = 0.0
    elif p_active_override is None:
        base_p_active = active_probability(player, model)
    else:
        base_p_active = _bounded(p_active_override, 1.0)

    full_cfg = cfg.get("status_full_given_active", {})
    default_full = {
        "ACTIVE": 0.97,
        "NORMAL": 0.97,
        "PROBABLE": 0.90,
        "QUESTIONABLE": 0.65,
        "DOUBTFUL": 0.40,
    }
    if base_p_active <= 0.0:
        base_p_full = 0.0
    else:
        base_p_full = _bounded(
            full_cfg.get(status, default_full.get(status, 0.90)),
            default_full.get(status, 0.90),
        )

    evidence_level, practice_source, practice_sequence, evidence, active_lrs, full_lrs = _availability_evidence(
        player,
        model,
        status=status,
        status_source=source,
        hours_to_kickoff=hours_to_kickoff,
    )

    if base_p_active <= 0.0:
        p_active = 0.0
        p_full_given_active = 0.0
        evidence_level = "HARD_UNAVAILABLE"
        posterior_method = "HARD_CONSTRAINT"
    elif p_active_override is not None:
        # Future-week simulations or explicit scenario overrides intentionally bypass
        # current-week injury evidence. Preserve the state decomposition but surface
        # that the active probability came from the caller.
        p_active = base_p_active
        p_full_given_active = base_p_full
        posterior_method = "OVERRIDE_STATUS_WORKLOAD_PRIOR"
    elif active_lrs or full_lrs:
        p_active = _posterior_from_likelihood_ratios(base_p_active, active_lrs)
        p_full_given_active = _posterior_from_likelihood_ratios(base_p_full, full_lrs)
        posterior_method = "PROVISIONAL_BAYES_ODDS_V027"
    else:
        p_active = base_p_active
        p_full_given_active = base_p_full
        posterior_method = "STATUS_PRIOR_FALLBACK"

    pos = str(player.get("position") or "").upper()
    limited_cfg = cfg.get("limited_workload_fraction", {})
    default_limited = {
        "QB": 0.80,
        "RB": 0.65,
        "WR": 0.65,
        "TE": 0.65,
        "K": 0.90,
        "DST": 0.90,
    }
    if isinstance(limited_cfg, dict):
        limited_fraction = _bounded(
            limited_cfg.get(pos, limited_cfg.get("DEFAULT", default_limited.get(pos, 0.65))),
            default_limited.get(pos, 0.65),
        )
    else:
        limited_fraction = _bounded(limited_cfg, default_limited.get(pos, 0.65))

    p_out = 1.0 - p_active
    p_full = p_active * p_full_given_active
    p_limited = p_active * (1.0 - p_full_given_active)
    return AvailabilityStateModel(
        status=status,
        status_source=source,
        p_active=float(p_active),
        p_full_given_active=float(p_full_given_active),
        p_out=float(p_out),
        p_limited=float(p_limited),
        p_full=float(p_full),
        limited_workload_fraction=float(limited_fraction),
        base_p_active=float(base_p_active),
        base_p_full_given_active=float(base_p_full),
        evidence_level=evidence_level,
        posterior_method=posterior_method,
        calibration_status="UNCALIBRATED_LIKELIHOOD_PRIORS",
        practice_source=practice_source,
        practice_sequence=practice_sequence,
        hours_to_kickoff=float(hours_to_kickoff) if hours_to_kickoff is not None else None,
        evidence=evidence,
    )


def sample_availability_state(
    state: AvailabilityStateModel,
    active_uniform: float,
    workload_uniform: float,
) -> str:
    if active_uniform >= state.p_active:
        return "OUT"
    if workload_uniform < state.p_full_given_active:
        return "ACTIVE_FULL"
    return "ACTIVE_LIMITED"


def _parse_kickoff(gameday: Any, gametime: Any) -> datetime | None:
    day = str(gameday or "").strip()
    time = str(gametime or "").strip()
    if not day:
        return None
    if not time or time.upper() in {"TBD", "NA", "N/A", "NONE"}:
        return None
    # nflverse schedules use YYYY-MM-DD and an Eastern clock time.
    candidates = [f"{day} {time}"]
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %I:%M%p",
        "%Y-%m-%d %I:%M %p",
    ]
    for text in candidates:
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt).replace(tzinfo=EASTERN)
            except ValueError:
                continue
    return None


def _lock_group(kickoff: datetime | None) -> str:
    if kickoff is None:
        return "UNKNOWN"
    local = kickoff.astimezone(EASTERN)
    weekday = local.weekday()  # Mon=0 ... Sun=6
    hour = local.hour + local.minute / 60.0
    if weekday == 3:
        return "THU"
    if weekday == 5:
        return "SAT"
    if weekday == 6:
        if hour < 15.5:
            return "SUN_EARLY"
        if hour < 19.0:
            return "SUN_LATE"
        return "SNF"
    if weekday == 0:
        return "MNF"
    return local.strftime("%a").upper()


def player_lock_timing(
    player: dict[str, Any],
    *,
    week: int,
    matchup_context: dict[str, Any] | None,
    model: dict[str, Any],
) -> LockTiming:
    team = str(player.get("nfl_team") or "").strip().upper()
    game = None
    if matchup_context and team:
        game = ((matchup_context.get("team_week") or {}).get(team) or {}).get(str(int(week)))
    if not game:
        return LockTiming(None, None, "UNKNOWN", "NO_SCHEDULE")
    kickoff = _parse_kickoff(game.get("gameday"), game.get("gametime"))
    if kickoff is None:
        return LockTiming(None, None, "UNKNOWN", "NFLVERSE_SCHEDULE_UNPARSED")
    lead = model.get("weekly_manager", {}).get("inactive_reveal_lead_minutes", 90)
    try:
        lead_minutes = max(float(lead), 0.0)
    except (TypeError, ValueError):
        lead_minutes = 90.0
    reveal = kickoff - timedelta(minutes=lead_minutes)
    return LockTiming(kickoff, reveal, _lock_group(kickoff), "NFLVERSE_SCHEDULE")
