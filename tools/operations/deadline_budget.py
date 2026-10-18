"""Read-only deadline budgeting for protected Wednesday/Saturday fantasy MC runs.

This module is not a substitute for ESPN lock/legality checks or MC authority.
It does not fetch schedules or change any state. A verified applicable lock must
be provided; the strict timing check is a preflight, not a transaction approval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from typing import Sequence

DEFAULT_MC_MINUTES = 40
DEFAULT_VERIFICATION_MINUTES = 15
DEFAULT_ACTION_MINUTES = 15
DEFAULT_SAFETY_MINUTES = 10


def aware_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("TIMESTAMP_MISSING")
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        timestamp = datetime.fromisoformat(s)
    except ValueError:
        raise ValueError("TIMESTAMP_INVALID_ISO8601") from None
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return timestamp.astimezone(timezone.utc)


def budget_deadline(
    now: datetime,
    deadline: datetime,
    *,
    mc_minutes: int = DEFAULT_MC_MINUTES,
    verification_minutes: int = DEFAULT_VERIFICATION_MINUTES,
    action_minutes: int = DEFAULT_ACTION_MINUTES,
    safety_minutes: int = DEFAULT_SAFETY_MINUTES,
) -> dict[str, object]:
    for label, value in (
        ("MC", mc_minutes),
        ("VERIFICATION", verification_minutes),
        ("ACTION", action_minutes),
        ("SAFETY", safety_minutes),
    ):
        if type(value) is not int or value < 0 or (label != "SAFETY" and value == 0):
            raise ValueError("INVALID_" + label + "_MINUTES")
    if now.tzinfo is None or now.utcoffset() is None or deadline.tzinfo is None or deadline.utcoffset() is None:
        raise ValueError("TIMEZONE_AWARE_TIMESTAMPS_REQUIRED")
    utc_now = now.astimezone(timezone.utc)
    utc_deadline = deadline.astimezone(timezone.utc)
    required = mc_minutes + verification_minutes + action_minutes + safety_minutes
    remaining = (utc_deadline - utc_now).total_seconds() / 60.0
    safe_end = utc_now + timedelta(minutes=required)
    # At equality a zero-second real-world delay causes the action to miss its
    # lock. Require positive remaining slack, not equality.
    if remaining <= 0:
        classification = "BLOCKED_LOCK_PASSED"
    elif safe_end >= utc_deadline:
        classification = "BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME"
    else:
        classification = "READY_TO_START_MC_NOT_ACTION_AUTHORITY"
    return {
        "classification": classification,
        "now_utc": utc_now.isoformat(),
        "deadline_utc": utc_deadline.isoformat(),
        "required_lead_minutes": required,
        "remaining_minutes": round(remaining, 3),
        "slack_minutes": round(remaining - required, 3),
    }


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--deadline-utc", required=True, help="Freshly verified earliest affected individual lock (timezone-aware ISO 8601)")
    ap.add_argument("--now-utc", help="Test/replay only; never backdate live football decision authority")
    ap.add_argument("--mc-minutes", type=int, default=DEFAULT_MC_MINUTES)
    ap.add_argument("--verification-minutes", type=int, default=DEFAULT_VERIFICATION_MINUTES)
    ap.add_argument("--action-minutes", type=int, default=DEFAULT_ACTION_MINUTES)
    ap.add_argument("--safety-minutes", type=int, default=DEFAULT_SAFETY_MINUTES)
    args = ap.parse_args(argv)
    print("PROTECTED WEEKLY MC DEADLINE PREFLIGHT", flush=True)
    try:
        deadline = aware_utc(args.deadline_utc)
        now = aware_utc(args.now_utc) if args.now_utc is not None else datetime.now(timezone.utc)
        result = budget_deadline(
            now, deadline,
            mc_minutes=args.mc_minutes,
            verification_minutes=args.verification_minutes,
            action_minutes=args.action_minutes,
            safety_minutes=args.safety_minutes,
        )
    except ValueError as exc:
        print("PREFLIGHT=BLOCKED_INVALID_DEADLINE_OR_BUDGET;REASON=" + str(exc), flush=True)
        print("MC_NOT_STARTED=TRUE;ESPN_ACTION_AUTHORITY=NONE", flush=True)
        return 2
    print("NOW_UTC=" + str(result["now_utc"]), flush=True)
    print("EARLIEST_AFFECTED_LOCK_UTC=" + str(result["deadline_utc"]), flush=True)
    print("REQUIRED_LEAD_MINUTES=" + str(result["required_lead_minutes"]), flush=True)
    print("REMAINING_MINUTES=" + str(result["remaining_minutes"]), flush=True)
    print("SLACK_MINUTES=" + str(result["slack_minutes"]), flush=True)
    print("PREFLIGHT=" + str(result["classification"]), flush=True)
    print("CALENDAR_ONLY=TRUE;LIVE_ESPN_CHECK=REQUIRED;MC_NOT_STARTED=TRUE;ESPN_ACTION_AUTHORITY=NONE", flush=True)
    return 0 if str(result["classification"]).startswith("READY_") else 3


if __name__ == "__main__":
    raise SystemExit(main())
