"""Pure deadline preflight regression / safety boundary tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util
import subprocess
import sys

import pytest


MODULE = Path(__file__).resolve().parents[1] / "tools" / "operations" / "deadline_budget.py"
SPEC = importlib.util.spec_from_file_location("deadline_budget_under_test", MODULE)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def at(date: str) -> datetime:
    return mod.aware_utc(date)


def decision(start: str, end: str, **kwargs: int) -> dict[str, object]:
    return mod.budget_deadline(at(start), at(end), **kwargs)


def test_default_budget_is_80_minutes():
    x = decision("2026-10-21T19:00:00Z", "2026-10-22T00:00:00Z")
    assert x["required_lead_minutes"] == 80
    assert x["classification"] == "READY_TO_START_MC_NOT_ACTION_AUTHORITY"


def test_wednesday_thursday_short_window_blocked():
    x = decision("2026-10-22T22:45:00Z", "2026-10-23T00:00:00Z")
    assert x["remaining_minutes"] == 75
    assert x["classification"] == "BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME"


def test_saturday_to_sunday_typical_am_has_time():
    assert decision("2026-10-24T20:00:00Z", "2026-10-25T17:00:00Z")["classification"].startswith("READY_")


def test_sunday_start_15_minutes_before_lock_is_rejected():
    x = decision("2026-10-18T13:14:00Z", "2026-10-18T13:30:00Z")
    assert x["classification"] == "BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME"


def test_exact_budget_boundary_is_rejected():
    x = decision("2026-10-18T12:10:00Z", "2026-10-18T13:30:00Z")
    assert x["remaining_minutes"] == 80
    assert x["classification"] == "BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME"


def test_one_second_extra_passes_budget_only():
    x = decision("2026-10-18T12:09:59Z", "2026-10-18T13:30:00Z")
    assert x["classification"] == "READY_TO_START_MC_NOT_ACTION_AUTHORITY"


def test_past_and_exactly_at_lock_blocked():
    for now in ("2026-10-18T13:30:00Z", "2026-10-18T13:31:00Z"):
        assert decision(now, "2026-10-18T13:30:00Z")["classification"] == "BLOCKED_LOCK_PASSED"


def test_utc_offsets_respect_instant():
    assert at("2026-10-18T09:30:00-04:00") == at("2026-10-18T13:30:00Z")


@pytest.mark.parametrize("invalid", ["", "2026-10-18T13:30:00", "yesterday", "2026-13-99T00:00:00Z"])
def test_invalid_or_naive_time_blocked(invalid: str):
    with pytest.raises(ValueError):
        at(invalid)


@pytest.mark.parametrize("key,value", [("mc_minutes", 0), ("mc_minutes", -1), ("verification_minutes", 0), ("action_minutes", 0), ("safety_minutes", -1), ("mc_minutes", True)])
def test_invalid_budget_fails_closed(key: str, value: int):
    with pytest.raises(ValueError):
        decision("2026-10-21T18:00:00Z", "2026-10-22T00:00:00Z", **{key: value})


def test_cli_success_is_preflight_only():
    r = subprocess.run([sys.executable, str(MODULE), "--now-utc", "2026-10-18T12:00:00Z", "--deadline-utc", "2026-10-18T13:30:00Z"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "READY_TO_START_MC_NOT_ACTION_AUTHORITY" in r.stdout
    assert "ESPN_ACTION_AUTHORITY=NONE" in r.stdout


def test_cli_block_failure_is_nonzero_and_explicit():
    r = subprocess.run([sys.executable, str(MODULE), "--now-utc", "2026-10-18T13:14:00Z", "--deadline-utc", "2026-10-18T13:30:00Z"], capture_output=True, text=True)
    assert r.returncode == 3
    assert "BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME" in r.stdout


def test_cli_missing_required_lock_is_nonzero():
    r = subprocess.run([sys.executable, str(MODULE)], capture_output=True, text=True)
    assert r.returncode != 0


def test_cli_invalid_time_is_nonzero():
    r = subprocess.run([sys.executable, str(MODULE), "--deadline-utc", "2026-10-18T13:30:00"], capture_output=True, text=True)
    assert r.returncode == 2
    assert "BLOCKED_INVALID_DEADLINE_OR_BUDGET" in r.stdout
