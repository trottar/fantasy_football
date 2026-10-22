"""Read-only, fail-closed trade-action certification scaffold (Week 8 Slice A).

Do not mistake a native ACTIONABLE_OFFER for a fully certified ESPN action.
This first slice proves input provenance and records explicit blockers. It does
not evaluate alternative drop distributions, future fills, or current ESPN
legality, and NEVER authorizes any transaction. Commissioned MC is unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

TRADE_CHANNELS = (
    "trade_one_for_one_player",
    "trade_multi_player_unequal",
    "trade_specialist_inclusive",
)
CONTRACT = "WEEKLY_ACTION_CERTIFICATION_READONLY_SCAFFOLD_V1"


class CertificationBlocked(ValueError):
    pass


def canonical_sha256(value: Any) -> str:
    def normalize(item: Any) -> Any:
        if isinstance(item, float) and not math.isfinite(item):
            return {"__nonfinite_float__": "NaN" if math.isnan(item) else ("+Inf" if item > 0 else "-Inf")}
        if isinstance(item, dict):
            return {str(k): normalize(v) for k, v in item.items()}
        if isinstance(item, (tuple, list)):
            return [normalize(v) for v in item]
        return item
    data = json.dumps(normalize(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False, default=str).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise CertificationBlocked(reason)


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None and not isinstance(value, bool) else None
    except (ValueError, TypeError, OverflowError):
        return None


def _teams(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    espn = snapshot.get("espn") or {}
    return [x for x in espn.get("teams") or [] if isinstance(x, dict)]


def _team(snapshot: Mapping[str, Any], team_id: int) -> dict[str, Any]:
    rows = [x for x in _teams(snapshot) if _safe_int(x.get("team_id")) == team_id]
    _require(len(rows) == 1, "EXACT_USER_TEAM_MISSING_OR_DUPLICATE")
    return rows[0]


def _lookup(roster: list[Any]) -> dict[int, dict[str, Any]]:
    return {int(p["espn_id"]): p for p in roster if isinstance(p, dict) and _safe_int(p.get("espn_id")) is not None}


def _offer_ids(offer: Mapping[str, Any], key: str) -> list[int]:
    value = offer.get(key)
    return [int(i) for i in value] if isinstance(value, list) and all(_safe_int(i) is not None for i in value) else []


def verify_frozen_inputs(snapshot: Mapping[str, Any], capture: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    _require(isinstance(snapshot, dict) and isinstance(capture, dict) and isinstance(receipt, dict),
             "INVALID_INPUT_TYPES")
    s_utc = snapshot.get("snapshot_utc")
    _require(isinstance(s_utc, str) and bool(s_utc), "SNAPSHOT_UTC_MISSING")
    _require(capture.get("snapshot_utc") == s_utc and
             (receipt.get("provenance") or {}).get("snapshot_utc") == s_utc,
             "SNAPSHOT_CAPTURE_MC_PROVENANCE_MISMATCH")
    _require((capture.get("behavioral_observation_state") or {}).get("snapshot_sha256") ==
             canonical_sha256(snapshot), "CAPTURE_SNAPSHOT_BINDING_INVALID")
    _require((capture.get("integrity") or {}).get("canonical_payload_sha256") ==
             canonical_sha256({k: v for k, v in capture.items() if k != "integrity"}),
             "PROSPECTIVE_CAPTURE_INTEGRITY_INVALID")
    _require((receipt.get("provenance") or {}).get("capture_integrity_ok") is True,
             "NATIVE_CAPTURE_VALIDATION_NOT_CONFIRMED")
    _require((snapshot.get("espn") or {}).get("week") == capture.get("week") == receipt.get("week"),
             "WEEK_MISMATCH")
    _require((snapshot.get("espn") or {}).get("season") == capture.get("season") == receipt.get("season"),
             "SEASON_MISMATCH")
    _require(_safe_int(receipt.get("team_id")) is not None, "RECEIPT_TEAM_ID_MISSING")
    _team(snapshot, int(receipt["team_id"]))


def _certify_offer(offer: Mapping[str, Any], channel: str, owned: dict[int, dict[str, Any]],
                   snapshot: Mapping[str, Any], review_hours: int | None) -> dict[str, Any]:
    blockers = [
        "NO_FRESH_ESPN_ACTION_SCREEN_OR_POST_MC_RECONCILIATION",
        "EXACT_ESPN_TRANSACTION_LEGALITY_UNVERIFIED",
        "ALT_ROSTER_DROP_AND_JOINT_PORTFOLIO_PAIRED_MC_NOT_CERTIFIED",
        "PARTNER_ACCEPTANCE_NOT_CONFIRMED",
    ]
    reasons: list[str] = []
    give = offer.get("give_names") or []
    receive = offer.get("receive_names") or []
    _require(isinstance(give, list) and isinstance(receive, list), "OFFER_ASSET_NAMES_INVALID")
    our_drop_ids = _offer_ids(offer, "user_auto_drop_ids")
    our_add_ids = _offer_ids(offer, "user_auto_add_ids")
    partner_add_ids = _offer_ids(offer, "partner_auto_add_ids")
    direct_give = _offer_ids(offer, "give_ids")
    receiving_positions = offer.get("receive_positions") or []
    _require(isinstance(receiving_positions, list), "RECEIVE_POSITIONS_INVALID")

    if our_drop_ids:
        blockers.append("AUTO_DROPS_REQUIRE_EXPLICIT_POST_TRADE_MC_COMPARISON")
    if our_add_ids or partner_add_ids:
        blockers.append("CURRENT_FREEAGENT_IS_NOT_GUARANTEED_AT_FUTURE_TRADE_EFFECTIVE_DATE")
    if review_hours is None:
        blockers.append("TRADE_REVIEW_WINDOW_UNVERIFIED")
    elif review_hours > 0:
        reasons.append("POSITIVE_TRADE_REVIEW_DEFERS_MODEL_TO_NEXT_WEEK")
    if str(offer.get("classification")) != "ACTIONABLE_OFFER":
        blockers.append("NATIVE_OFFER_NOT_ACTIONABLE")

    # Audit all QB ownership effects without comparing P versus DST/K production.
    roster_qbs = [pid for pid, p in owned.items() if str(p.get("position") or "").upper() == "QB"]
    outgoing_qbs = [pid for pid in direct_give if pid in roster_qbs]
    forced_drop_qbs = [pid for pid in our_drop_ids if pid in roster_qbs]
    retained_qbs = [pid for pid in roster_qbs if pid not in set(outgoing_qbs + forced_drop_qbs)]
    incoming_qbs = sum(1 for p in receiving_positions if str(p).upper() == "QB")
    remain = len(retained_qbs) + incoming_qbs
    if remain <= 1:
        blockers.append("POST_TRADE_QB_SINGLETON_CONTINGENCY_UNEVALUATED")
    if remain == 0:
        blockers.append("POST_TRADE_QB_NONE")
    if any(str(owned[i].get("injury_status") or "").upper() != "ACTIVE" for i in retained_qbs):
        blockers.append("POST_TRADE_QB_AVAILABILITY_UNCERTAINTY_NOT_PROPAGATED")
    unknown_drops = [pid for pid in our_drop_ids if pid not in owned]
    if unknown_drops:
        blockers.append("AUTO_DROP_ID_NOT_ON_FROZEN_OWNED_ROSTER")
    if not direct_give:
        blockers.append("GIVE_IDS_MISSING_FOR_EXACT_ROSTER_PROOF")
    return {
        "channel": channel,
        "give": [str(x) for x in give],
        "receive": [str(x) for x in receive],
        "native_classification": str(offer.get("classification") or "UNKNOWN"),
        "final_decision": "BLOCKED",
        "mandatory_user_drops": [str(owned[i].get("name") or "UNKNOWN") for i in our_drop_ids if i in owned],
        "required_user_auto_adds_total": len(our_add_ids),
        "required_partner_auto_adds_total": len(partner_add_ids),
        "post_trade_qbs_count_if_native_drops_executed": remain,
        "remaining_qbs": [str(owned[i].get("name") or "UNKNOWN") for i in retained_qbs],
        "modeled_earliest_effective_week": (int((snapshot.get("espn") or {}).get("week")) + 1)
            if review_hours is not None and review_hours > 0 else None,
        "non_authoritative_notes": reasons,
        "blockers": sorted(set(blockers)),
        "espn_action_authority": "NONE",
    }


def certify_receipt(snapshot: dict[str, Any], capture: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    verify_frozen_inputs(snapshot, capture, receipt)
    settings = (snapshot.get("espn") or {}).get("transaction_settings") or {}
    review_hours = _safe_int(settings.get("trade_review_hours"))
    if review_hours is not None and review_hours < 0:
        review_hours = None
    owned = _lookup(list(_team(snapshot, int(receipt["team_id"])).get("roster") or []))
    channels = receipt.get("channels") or []
    _require(isinstance(channels, list), "NATIVE_CHANNEL_RECEIPT_INVALID")
    bykey = {str(x.get("key")): x for x in channels if isinstance(x, dict)}
    offers: list[dict[str, Any]] = []
    missing: list[str] = []
    for key in TRADE_CHANNELS:
        c = bykey.get(key)
        if not isinstance(c, dict):
            missing.append(key)
            continue
        action = c.get("action") or {}
        if not isinstance(action, dict):
            raise CertificationBlocked("NATIVE_TRADE_ACTION_SHAPE_INVALID")
        candidates = action.get("offers") or []
        if not isinstance(candidates, list):
            raise CertificationBlocked("NATIVE_TRADE_OFFERS_NOT_LIST")
        for raw in candidates:
            _require(isinstance(raw, dict), "NATIVE_TRADE_OFFER_NOT_OBJECT")
            offers.append(_certify_offer(raw, key, owned, snapshot, review_hours))
    return {
        "contract": CONTRACT,
        "season": receipt.get("season"), "week": receipt.get("week"),
        "native_overall_at_frozen_state": receipt.get("overall_state"),
        "frozen_input_integrity": "PASS",
        "trade_channel_receipts_missing": missing,
        "candidates": offers,
        "candidate_count": len(offers),
        "certified_action_count": 0,
        "final_state": "BLOCKED_CERTIFICATION_NOT_COMMISSIONED",
        "espn_action_authority": "NONE",
        "notes": "Slice A observational scaffold; no fresh ESPN read, portfolio MC, app legality or trade submission",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--capture", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--out", type=Path, help="Private local report path; never commit")
    args = ap.parse_args(argv)
    print("WEEK8 ACTION CERTIFICATION SCAFFOLD READONLY", flush=True)
    try:
        documents = [json.loads(p.read_text(encoding="utf-8-sig")) for p in
                     (args.snapshot, args.capture, args.receipt)]
        report = certify_receipt(*documents)
        if args.out is not None:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("x", encoding="utf-8") as out:
                json.dump(report, out, indent=2, ensure_ascii=True, sort_keys=True)
                out.write("\n")
        print("FROZEN_INTEGRITY=PASS;CERTIFIED_ACTIONS=0;NATIVE_TRADE_OFFERS=" + str(report["candidate_count"]))
        for row in report["candidates"]:
            print("FROZEN_TRADE_CANDIDATE=" + json.dumps(row, ensure_ascii=True, sort_keys=True))
        print("FINAL_STATE=BLOCKED_CERTIFICATION_NOT_COMMISSIONED;ESPN_WRITES=NONE;ACTION_AUTHORITY=NONE")
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        code = str(exc) if isinstance(exc, CertificationBlocked) else type(exc).__name__
        print("CERTIFICATION_BLOCKED=" + code + ";ACTION_AUTHORITY=NONE")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
