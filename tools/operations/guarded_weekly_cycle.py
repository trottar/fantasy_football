"""Protected Wed/Sat nine-channel MC launcher: verify timing *before* calling MC.

This is an opt-in orchestration control at the control root. It does NOT modify
commissioned v0.36, obtain live ESPN locks, authorize ESPN actions, or replace MC.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
import subprocess
import sys
from typing import Any

EXPECTED_RUNTIME = "fantasy_season_v0_36_repack1"
EXPECTED_VERSION = "0.36"
EXPECTED_SOURCE_CHECKPOINT = "68dfabed5088a6ddf90a5d3af4f5497bf25f334a"
EXPECTED_BLOBS = {
    "fantasy.py": "dd3a0a2b39ea1c6b424e71f6a11273f2503ccc64",
    "src/weekly_decision_cycle.py": "c4c7fafbdeabb9454b8eb0c82a5aa4a466f7d12a",
    "src/closure.py": "9e7602dde722a999c5077904cb5d485d9015f34e",
}
PROVIDERS = ("espn", "sleeper", "nflverse_rosters", "nflverse_matchups", "nfl_official_rosters", "nfl_official")
DEPENDENCIES = {"league_config": "config/league.json", "model_config": "config/model.json",
                "player_values": "data/processed/player_values_2026.csv"}


class Blocked(ValueError):
    pass


def require(value: bool, reason: str) -> None:
    if not value:
        raise Blocked(reason)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git_blob(raw: bytes) -> str:
    data = raw.removeprefix(b"\xef\xbb\xbf").replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _canon(value: Any) -> str:
    def clean(v: Any) -> Any:
        if isinstance(v, float) and not math.isfinite(v):
            return {"__nonfinite_float__": "NaN" if math.isnan(v) else ("+Inf" if v > 0 else "-Inf")}
        if isinstance(v, dict):
            return {str(k): clean(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [clean(x) for x in v]
        return v
    return _sha256(json.dumps(clean(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                              allow_nan=False, default=str).encode("utf-8"))


def _json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise Blocked("LOCAL_JSON_NOT_READABLE:" + path.name) from exc
    require(isinstance(result, dict), "LOCAL_JSON_NOT_OBJECT:" + path.name)
    return result


def _time(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return ts.astimezone(timezone.utc) if ts.tzinfo is not None and ts.utcoffset() is not None else None
    except (ValueError, OverflowError):
        return None


def safe_file(runtime: Path, relative: str, collection: str) -> Path:
    candidate = Path(relative)
    require(relative and not candidate.is_absolute() and ".." not in candidate.parts
            and ":" not in relative and "\\" not in relative, "INVALID_LOCAL_PATH")
    dest = (runtime / candidate).resolve()
    require(dest.is_relative_to((runtime / collection).resolve()), "LOCAL_PATH_OUTSIDE_COLLECTION")
    require(dest.is_file(), "REQUIRED_LOCAL_FILE_MISSING:" + candidate.name)
    return dest


def validate_root(root: Path) -> Path:
    require(root.name.casefold() == "fantasy_football" and
            (root / "tools/operations/deadline_budget.py").is_file(), "WRONG_PROJECT_ROOT")
    runtime = root / EXPECTED_RUNTIME
    require(runtime.is_dir() and (runtime / "VERSION").read_text(encoding="utf-8-sig").strip() == EXPECTED_VERSION,
            "COMMISSIONED_RUNTIME_UNVERIFIED")
    for rel, oid in EXPECTED_BLOBS.items():
        path = runtime / rel
        require(path.is_file() and _git_blob(path.read_bytes()) == oid, "SOURCE_BLOB_MISMATCH:" + rel)
    return runtime


def _lock_candidates(capture: dict[str, Any], now: datetime) -> dict[str, Any]:
    player_rows = (capture.get("league_player_predictions") or {}).get("records")
    specialist_rows = (capture.get("specialist_predictions") or {}).get("records")
    require(isinstance(player_rows, list) and player_rows and isinstance(specialist_rows, list) and specialist_rows,
            "CAPTURE_P_D_K_RECORDS_REQUIRED")
    user_team_id = capture.get("team_id")
    require(user_team_id is not None, "CAPTURE_USER_TEAM_UNRESOLVED")
    values = []
    owned = []
    unknown_all = 0
    expired = 0
    for item, is_player in [(p, True) for p in player_rows] + [(p, False) for p in specialist_rows]:
        require(isinstance(item, dict), "CAPTURE_RECORD_NOT_OBJECT")
        pid = item.get("espn_id")
        pos = str(item.get("position") or "").upper()
        is_user = item.get("side") == "US" if is_player else item.get("owner_team_id") == user_team_id
        if not pos:
            continue
        kickoff = _time(item.get("kickoff_utc"))
        if kickoff is None:
            unknown_all += 1
            if is_user:
                raise Blocked("UNKNOWN_OWNED_PLAYER_LOCK")
            continue
        if is_user:
            owned.append(kickoff)
        if kickoff > now:
            values.append(kickoff)
        else:
            expired += 1
    require(bool(owned), "CAPTURE_USER_ROSTER_LOCKS_MISSING")
    require(any(t > now for t in owned), "NO_UNLOCKED_OWNED_ASSETS")
    require(bool(values), "NO_FUTURE_VERIFIABLE_LOCKS")
    return {"deadline": min(values), "owned_records": len(owned), "unknown_all": unknown_all,
            "expired_records": expired, "known_future_records": len(values)}


def inspect(root: Path, runtime: Path, snapshot_rel: str, capture_rel: str,
            identity_rel: str, memory_rel: str, now: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
    snapshot_path = safe_file(runtime, snapshot_rel, "data/season_snapshots")
    capture_path = safe_file(runtime, capture_rel, "data/season_predictions/closure")
    identity_path = safe_file(runtime, identity_rel, "data/season_decisions")
    memory_path = safe_file(runtime, memory_rel, "data/season_decisions")
    snapshot, capture = _json(snapshot_path), _json(capture_path)
    ident, mem = _json(identity_path), _json(memory_path)
    require(ident.get("commissioned") is True and ident.get("source_checkpoint") == EXPECTED_SOURCE_CHECKPOINT
            and ident.get("runtime_version") == EXPECTED_VERSION, "COMMISSIONING_IDENTITY_INVALID")
    dependency_identity = ident.get("dependencies") or {}
    for key, rel in DEPENDENCIES.items():
        path = runtime / rel
        require(path.is_file() and dependency_identity.get(key) == _sha256(path.read_bytes()),
                "COMMISSIONED_DEPENDENCY_MISMATCH:" + key)
    require(mem.get("status") == "PASS" and mem.get("strict") is True, "MEMORY_HEALTH_EVIDENCE_INVALID")
    for label, document in (("IDENTITY", ident), ("MEMORY_HEALTH", mem)):
        checked = _time(document.get("verified_utc") if label == "IDENTITY" else document.get("checked_utc"))
        require(checked is not None and 0 <= (now - checked).total_seconds() < 7200,
                label + "_STALE_OR_FUTURE")
    espn = snapshot.get("espn") or {}
    require(espn.get("week") == capture.get("week") and espn.get("season") == capture.get("season"),
            "SNAPSHOT_CAPTURE_WEEK_MISMATCH")
    require(capture.get("model_version") == EXPECTED_VERSION, "CAPTURE_MODEL_VERSION_MISMATCH")
    require(capture.get("measurement_contract") == "A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034",
            "PROSPECTIVE_CONTRACT_INVALID")
    source = snapshot.get("source_status") or {}
    for p in PROVIDERS:
        entry = source.get(p)
        require(isinstance(entry, dict) and (entry.get("complete") if p == "nfl_official_rosters" and
                entry.get("complete") is not None else entry.get("ok")) is True,
                "PROVIDER_HEALTH_INCOMPLETE:" + p)
    captured = _time(capture.get("captured_utc"))
    snap_time = _time(snapshot.get("snapshot_utc"))
    require(captured is not None and snap_time is not None and snap_time <= captured <= now,
            "CAPTURE_CHRONOLOGY_INVALID")
    require((now - captured).total_seconds() <= 7200, "CAPTURE_TOO_OLD_FOR_PROTECTED_RUN")
    require(capture.get("snapshot_utc") == snapshot.get("snapshot_utc"), "CAPTURE_SNAPSHOT_TIME_MISMATCH")
    require((capture.get("behavioral_observation_state") or {}).get("snapshot_sha256") == _canon(snapshot),
            "SNAPSHOT_CAPTURE_BINDING_INVALID")
    require((capture.get("integrity") or {}).get("canonical_payload_sha256") ==
            _canon({k: v for k, v in capture.items() if k != "integrity"}), "CAPTURE_INTEGRITY_INVALID")
    firewall = capture.get("pre_data_firewall") or {}
    for k in ("2026_game_outcomes_used_for_tuning", "automatic_refit", "automatic_calibration"):
        require(firewall.get(k) is False, "PRE_DATA_FIREWALL_INVALID")
    return _lock_candidates(capture, now), {"snapshot": snapshot, "capture": capture,
            "capture_sha256": _sha256(capture_path.read_bytes()),
            "snapshot_sha256": _sha256(snapshot_path.read_bytes())}


def evaluate_timing(root: Path, now: datetime, earliest: datetime) -> dict[str, Any]:
    sys.path.insert(0, str(root / "tools/operations"))
    from deadline_budget import budget_deadline
    return budget_deadline(now, earliest)


def execute(root: Path, runtime: Path, paths: tuple[str, str, str, str], earliest: datetime,
            evidence: dict[str, Any], now_fn=None, child=None) -> dict[str, Any]:
    now_fn = now_fn or (lambda: datetime.now(timezone.utc))
    child = child or subprocess.run
    # Re-check budget immediately before entering native MC; do not allow preflight
    # validation/printing overhead to eat the action budget.
    timing = evaluate_timing(root, now_fn(), earliest)
    require(timing["classification"] == "READY_TO_START_MC_NOT_ACTION_AUTHORITY",
            "DEADLINE_EXPIRED_BEFORE_MC_LAUNCH")
    decision_dir = runtime / "data/season_decisions"
    before = {p.name for p in decision_dir.glob("weekly_decision_receipt_*.json")}
    command = [sys.executable, "fantasy.py", "weekly-cycle", "--snapshot", paths[0],
               "--capture", paths[1], "--commissioning-identity", paths[2],
               "--memory-health", paths[3]]
    done = child(command, cwd=str(runtime), capture_output=True, text=True, check=False)
    if done.returncode != 0:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        failure = decision_dir / ("guarded_mc_failure_" + stamp + ".log")
        with failure.open("x", encoding="utf-8") as fh:
            fh.write("EXIT=" + str(done.returncode) + "\nSTDOUT\n" + done.stdout + "\nSTDERR\n" + done.stderr)
        raise Blocked("NATIVE_MC_FAILED_EXIT_" + str(done.returncode) + ";PRIVATE_LOG=" + failure.name)
    new = [p for p in decision_dir.glob("weekly_decision_receipt_*.json") if p.name not in before]
    require(len(new) == 1, "NATIVE_MC_RECEIPT_NOT_UNIQUE")
    receipt = _json(new[0])
    require((receipt.get("provenance") or {}).get("snapshot_utc") == evidence["snapshot"]["snapshot_utc"],
            "NATIVE_MC_PROVENANCE_MISMATCH")
    require((runtime / paths[0]).is_file() and _sha256((runtime / paths[0]).read_bytes()) == evidence["snapshot_sha256"]
            and _sha256((runtime / paths[1]).read_bytes()) == evidence["capture_sha256"],
            "IMMUTABLE_EVIDENCE_CHANGED_DURING_MC")
    completed = now_fn()
    # MC has finished: budget ONLY live verification, user action, safety.
    remaining_after_mc = (earliest - completed).total_seconds() / 60.0
    remaining_budget = 15 + 15 + 10
    action_window = ("RECHECK_REQUIRED" if remaining_after_mc > remaining_budget else
                     "LOCK_PASSED_OR_INSUFFICIENT_ACTION_TIME")
    return {"receipt": new[0].relative_to(runtime).as_posix(), "receipt_sha256": _sha256(new[0].read_bytes()),
            "native_overall": receipt.get("overall_state"),
            "action_window": action_window,
            "finish_utc": completed.isoformat()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--snapshot", required=True, help="Runtime-relative immutable fresh six-provider snapshot")
    ap.add_argument("--capture", required=True, help="Runtime-relative bound immutable prospective capture")
    ap.add_argument("--commissioning-identity", required=True)
    ap.add_argument("--memory-health", required=True)
    ap.add_argument("--execute", action="store_true", help="Explicitly start the ~40 minute native MC after preflight")
    args = ap.parse_args(argv)
    print("PROTECTED WED/SAT NINE-CHANNEL MC LAUNCH GATE", flush=True)
    try:
        root = Path(args.project_root).resolve()
        runtime = validate_root(root)
        now = datetime.now(timezone.utc)
        p = (args.snapshot, args.capture, args.commissioning_identity, args.memory_health)
        locks, evidence = inspect(root, runtime, *p, now)
        timing = evaluate_timing(root, now, locks["deadline"])
        print("EARLIEST_CAPTURED_FUTURE_LOCK_UTC=" + locks["deadline"].isoformat(), flush=True)
        print("OWNED_LOCKS_VERIFIED=" + str(locks["owned_records"]), flush=True)
        print("UNKNOWN_CAPTURE_RECORD_LOCKS=" + str(locks["unknown_all"]), flush=True)
        print("ALREADY_LOCKED_CAPTURE_RECORDS=" + str(locks["expired_records"]), flush=True)
        print("REMAINING_MINUTES=" + str(timing["remaining_minutes"]), flush=True)
        print("REQUIRED_MINUTES=" + str(timing["required_lead_minutes"]), flush=True)
        print("PREFLIGHT=" + str(timing["classification"]), flush=True)
        print("TIME_BUDGET_ONLY;LIVE_ESPN_SLOT_AND_LOCK_RECHECK_REQUIRED;ACTION_AUTHORITY=NONE", flush=True)
        if not str(timing["classification"]).startswith("READY_"):
            print("MC_NOT_STARTED=TRUE", flush=True)
            return 3
        if not args.execute:
            print("MODE=CHECK_ONLY;MC_NOT_STARTED=TRUE", flush=True)
            return 0
        outcome = execute(root, runtime, p, locks["deadline"], evidence)
        print("MODE=EXECUTE;NATIVE_MC=COMPLETED", flush=True)
        print("RECEIPT=" + outcome["receipt"] + ";SHA256=" + outcome["receipt_sha256"], flush=True)
        print("NATIVE_OVERALL=" + str(outcome["native_overall"]), flush=True)
        print("ACTION_WINDOW=" + outcome["action_window"], flush=True)
        print("LIVE_ESPN_RECHECK_PENDING=TRUE;ESPN_ACTION_AUTHORITY=NONE;NO_ESPN_TRANSACTIONS=TRUE", flush=True)
        return 0
    except (Blocked, ValueError, OSError, TypeError, KeyError) as exc:
        print("GUARDED_MC_BLOCKED=" + str(exc), flush=True)
        print("MC_NOT_AUTHORIZED_TO_RUN;ESPN_ACTION_AUTHORITY=NONE", flush=True)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
