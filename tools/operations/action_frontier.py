"""Frozen trade alternatives and coupled-offer frontier, Week 8 Slice B1.

The output is a deterministic list of structural perturbations for *future*
paired MC, not evaluated fantasy utility, guaranteed ESPN legality, or advice.
Only frozen, provenance-verified snapshot/capture/receipt inputs are accepted.
The existing commissioned v0.36 trade evaluator is never patched or called.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Mapping

from action_certification import (
    CertificationBlocked,
    TRADE_CHANNELS,
    _lookup,
    _safe_int,
    _team,
    canonical_sha256,
    certify_receipt,
)

FRONTIER_CONTRACT = "WEEK8_FROZEN_TRADE_STRUCTURAL_FRONTIER_V1"
MAX_ALTERNATIVES = 64


def _need(ok: bool, reason: str) -> None:
    if not ok:
        raise CertificationBlocked(reason)


def _ids_strict(offer: Mapping[str, Any], key: str) -> tuple[int, ...]:
    raw = offer.get(key)
    _need(isinstance(raw, list), "NATIVE_OFFER_IDS_NOT_LIST:" + key)
    _need(all(type(v) is int and v != 0 for v in raw), "NATIVE_OFFER_IDS_INVALID:" + key)
    _need(len(set(raw)) == len(raw), "DUPLICATE_OFFER_IDS:" + key)
    return tuple(raw)


def _exact_roster(team: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    roster = team.get("roster")
    _need(isinstance(roster, list) and roster, "TEAM_ROSTER_UNAVAILABLE")
    _need(all(type(p.get("espn_id")) is int and p["espn_id"] != 0 and
              (p["espn_id"] > 0 or _position(p) == "DST") for p in roster),
          "ROSTER_ASSET_ID_SIGN_OR_POSITION_INVALID")
    out = _lookup(roster)
    _need(len(out) == len(roster), "DUPLICATE_OR_UNIDENTIFIED_ROSTER_ASSETS")
    return out


def _position(player: Mapping[str, Any]) -> str:
    pos = str(player.get("position") or "").upper()
    return pos if pos in {"QB", "RB", "WR", "TE", "DST", "K"} else "UNKNOWN"


def _roster_summary(players: Mapping[int, Mapping[str, Any]]) -> dict[str, Any]:
    positions = Counter(_position(p) for p in players.values())
    return {"total": len(players),
            "channels": {
                "P": {k: positions[k] for k in ("QB", "RB", "WR", "TE")},
                "D": {"DST": positions["DST"]},
                "K": {"K": positions["K"]},
                "UNKNOWN": positions["UNKNOWN"],
            },
            "qb_names": sorted(str(p.get("name") or "UNKNOWN") for p in players.values()
                               if _position(p) == "QB"),
            "unresolved_qb_availability": sorted(str(p.get("name") or "UNKNOWN") for p in players.values()
                               if _position(p) == "QB" and str(p.get("injury_status") or "").upper() != "ACTIVE")}


def _offer_id(channel: str, partner: int, give: tuple[int, ...], receive: tuple[int, ...]) -> str:
    state = {"channel": channel, "partner_team_id": partner, "give": sorted(give), "receive": sorted(receive)}
    return hashlib.sha256(json.dumps(state, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:24]


def _candidate(incoming: Mapping[int, Mapping[str, Any]],
               retained: dict[int, dict[str, Any]], dropped: tuple[int, ...],
               roster_target: int, *, native: bool) -> dict[str, Any]:
    after = {pid: p for pid, p in retained.items() if pid not in dropped}
    after.update(incoming)
    # A static roster representation is not enough to certify ESPN transactions.
    labels = []
    if len(after) != roster_target:
        labels.append("ROSTER_COUNT_MISMATCH_OR_FUTURE_FILL_NEEDED")
    if any(retained[pid].get("droppable") is not True for pid in dropped):
        labels.append("FROZEN_ESPN_DROPPABLE_NOT_TRUE")
    if any(retained[pid].get("lineup_locked") is not False for pid in dropped):
        labels.append("FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED")
    if not labels:
        labels.append("FROZEN_ONLY_ESPN_AND_FUTURE_WEEK_LEGALITY_UNVERIFIED")
    return {
        "drop_ids": list(dropped),
        "drop_names": [str(retained[pid].get("name") or "UNKNOWN") for pid in dropped],
        "native_selected_normalization": native,
        "post_trade_owned_ids_without_future_fills": sorted(after),
        "post_trade_static_state": _roster_summary(after),
        "static_target_roster_size": roster_target,
        "feasibility_evidence": sorted(set(labels)),
        "valuation_state": "PAIRED_MC_NOT_RUN",
        "espn_legality": "UNVERIFIED",
    }


def _native_position_rebalance_drop_count(
    channel: str, user: Mapping[int, Mapping[str, Any]],
    give: tuple[int, ...], incoming: Mapping[int, Mapping[str, Any]],
    user_drops: tuple[int, ...], user_adds: tuple[int, ...],
    snapshot: Mapping[str, Any], must_drop: int, must_fill: int,
) -> int | None:
    """Represent only evidenced equal-count specialist position repairs.

    The native specialist normalizer can perform a drop plus a conditional
    FREEAGENT fill even when trade headcount is balanced.  This is frozen
    structural evidence, not a guarantee of future acquisition or ESPN action.
    B2b2 remains authoritative for actual league min/max legality per branch.
    """
    extra = len(user_drops)
    if (channel != "trade_specialist_inclusive" or must_drop or must_fill or
            extra < 1 or extra > 2 or len(user_adds) != extra or
            tuple(sorted(user_drops)) != user_drops or
            not set(user_drops).issubset(set(user) - set(give))):
        return None
    original = Counter(_position(p) for p in user.values())
    direct = Counter(_position(p) for pid, p in user.items() if pid not in give)
    direct.update(_position(p) for p in incoming.values())
    espn = snapshot.get("espn", snapshot)
    pool = espn.get("available_players") if isinstance(espn, Mapping) else None
    if not isinstance(pool, list):
        return None
    matched = []
    for pid in user_adds:
        rows = [p for p in pool if isinstance(p, Mapping) and
                type(p.get("espn_id")) is int and p["espn_id"] == pid]
        if (len(rows) != 1 or
                str(rows[0].get("fantasy_status") or "").upper() != "FREEAGENT" or
                _position(rows[0]) not in ("DST", "K") or
                (pid < 0 and _position(rows[0]) != "DST")):
            return None
        matched.append(rows[0])
    fills = Counter(_position(p) for p in matched)
    # Exact specialist deficit relative to frozen original, not a headcount guess.
    if not any(direct[pos] < original[pos] and fills[pos] > 0
               for pos in ("DST", "K")):
        return None
    return extra


def _enumerate_offer(offer: Mapping[str, Any], channel: str,
                     user: Mapping[int, dict[str, Any]], snapshot: Mapping[str, Any],
                     *, limit: int = MAX_ALTERNATIVES) -> dict[str, Any]:
    _need(1 <= limit <= 256, "INVALID_ALTERNATIVE_LIMIT")
    give = _ids_strict(offer, "give_ids")
    receive = _ids_strict(offer, "receive_ids")
    user_drops = _ids_strict(offer, "user_auto_drop_ids")
    user_adds = _ids_strict(offer, "user_auto_add_ids")
    partner_drops = _ids_strict(offer, "partner_auto_drop_ids")
    partner_adds = _ids_strict(offer, "partner_auto_add_ids")
    _need(give and receive, "EMPTY_NATIVE_TRADE_PACKAGE")
    _need(not (set(give) & set(receive)), "SAME_ASSET_BOTH_SIDES")
    _need(not (set(receive) & set(user)), "RECEIVED_ASSET_ALREADY_ON_USER_ROSTER")
    partner_id = _safe_int(offer.get("partner_team_id"))
    _need(partner_id is not None, "PARTNER_TEAM_ID_UNVERIFIED")
    partner_team = _team(snapshot, partner_id)
    partner = _exact_roster(partner_team)
    # Need exact native player ownership; a missing asset makes the candidate
    # structurally invalid, never a candidate with guessed names/positions.
    _need(set(give) <= set(user), "FROZEN_GIVE_NOT_OWNED")
    _need(set(receive) <= set(partner), "FROZEN_RECEIVE_NOT_PARTNER_OWNED")
    _need(not (set(user_drops) & set(give)), "NATIVE_AUTO_DROP_IS_GIVEN_ASSET")
    _need(set(user_drops) <= set(user), "NATIVE_AUTO_DROP_NOT_OWNED")
    _need(not (set(user_adds) & (set(user) | set(receive))), "NATIVE_AUTO_ADD_ALREADY_OWNED_OR_RECEIVED")
    _need(not (set(partner_adds) & (set(partner) | set(give))), "PARTNER_AUTO_ADD_ALREADY_OWNED_OR_RECEIVED")

    incoming = {i: dict(partner[i]) for i in receive}
    retained = {i: p for i, p in user.items() if i not in give}
    count_without_fills = len(retained) + len(incoming)
    must_drop = max(0, count_without_fills - len(user))
    must_fill = max(0, len(user) - count_without_fills)
    repair_drops = _native_position_rebalance_drop_count(
        channel, user, give, incoming, user_drops, user_adds, snapshot,
        must_drop, must_fill)
    enumerate_drop_count = repair_drops if repair_drops is not None else must_drop
    normalize = []
    if len(user_drops) != must_drop or len(user_adds) != must_fill:
        normalize.append("NATIVE_POSITION_REBALANCE_CONDITIONAL_FROZEN_FILL"
                         if repair_drops is not None else
                         "NATIVE_NORMALIZATION_COUNT_INCONSISTENT_WITH_FROZEN_ROSTER")
    if partner_adds or user_adds:
        normalize.append("FUTURE_FREEAGENT_FILL_UNPROVEN")

    # Candidate drops are *structural possibilities*, not legally certified.
    # Use exact frozen ESPN booleans; unknowns are excluded from the safe-frontier
    # but the native choice is always shown with explicit evidence warnings.
    structurally_droppable = sorted(i for i, p in retained.items()
                                    if p.get("droppable") is True and p.get("lineup_locked") is False)
    combos = itertools.combinations(structurally_droppable, enumerate_drop_count)
    inspected = []
    for combo in itertools.islice(combos, limit + 1):
        inspected.append(combo)
    truncated = len(inspected) > limit
    inspect_pairs = inspected[:limit]
    # Include native selected drop even when its frozen ESPN legality is unknown.
    native_tuple = tuple(sorted(user_drops))
    alt = []
    if len(user_drops) == enumerate_drop_count:
        alt.append(_candidate(incoming, retained, native_tuple, len(user), native=True))
    for combo in inspect_pairs:
        if combo != native_tuple:
            alt.append(_candidate(incoming, retained, combo, len(user), native=False))

    identity = _offer_id(channel, partner_id, give, receive)
    original = _roster_summary(user)
    warnings = ["STATIC_FRONTIER_ONLY_NO_NATIVE_PAIRED_MC_OR_ESPN_ACTION_AUTHORITY"] + normalize
    if truncated:
        warnings.append("STRUCTURAL_ALTERNATIVES_TRUNCATED")
    if enumerate_drop_count and not inspect_pairs:
        warnings.append("NO_FROZEN_PROVEN_UNLOCKED_DROPPABLE_ALTERNATIVES")
    return {
        "offer_id": identity,
        "channel": channel,
        "partner_team_id": partner_id,
        "partner_name": str(partner_team.get("name") or "UNKNOWN"),
        "give": [str(user[i].get("name") or "UNKNOWN") for i in give],
        "receive": [str(partner[i].get("name") or "UNKNOWN") for i in receive],
        "give_ids": list(give), "receive_ids": list(receive),
        "modeled_native_auto_drop_ids": list(user_drops),
        "modeled_native_auto_add_ids": list(user_adds),
        "modeled_partner_auto_drop_ids": list(partner_drops),
        "modeled_partner_auto_add_ids": list(partner_adds),
        "required_user_drops_by_count": must_drop,
        "required_user_fills_by_count": must_fill,
        "baseline_owned_state": original,
        "structural_options": alt,
        "structural_options_truncated": truncated,
        "structural_options_total_enumerated": len(alt),
        "next_compute": "NATIVE_PAIRED_COMPLETE_ROSTER_MC_ALL_FEASIBLE_NORMALIZATIONS_REQUIRED",
        "blocking_evidence": sorted(set(warnings)),
        "decision": "BLOCKED_PENDING_PREDICTIVE_CERTIFICATION",
    }


def _couplings(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for a, b in itertools.combinations(offers, 2):
        # All requested options are currently individual choices. Shared direct
        # assets make the two simultaneous offers impossible in one roster state.
        shared_give = sorted(set(a["give_ids"]) & set(b["give_ids"]))
        shared_receive = sorted(set(a["receive_ids"]) & set(b["receive_ids"]))
        if shared_give or shared_receive or a["partner_team_id"] == b["partner_team_id"]:
            out.append({"offer_ids": sorted((a["offer_id"], b["offer_id"])),
                        "shared_given_ids": shared_give,
                        "shared_receiving_ids": shared_receive,
                        "same_partner": a["partner_team_id"] == b["partner_team_id"],
                        "direct_asset_conflict": bool(shared_give or shared_receive),
                        "combined_strategy_evaluated": False})
    return out


def build_frontier(snapshot: dict[str, Any], capture: dict[str, Any],
                   receipt: dict[str, Any], *, limit: int = MAX_ALTERNATIVES) -> dict[str, Any]:
    base = certify_receipt(snapshot, capture, receipt)  # all Slice A binding checks
    _need(not base["trade_channel_receipts_missing"], "REQUIRED_TRADE_CHANNEL_RECEIPT_MISSING")
    user = _exact_roster(_team(snapshot, int(receipt["team_id"])))
    found = []
    byid = set()
    for channel in receipt["channels"]:
        if channel.get("key") not in TRADE_CHANNELS:
            continue
        for raw in (channel.get("action") or {}).get("offers") or []:
            _need(isinstance(raw, dict), "NATIVE_OFFER_NOT_DICT")
            offer = _enumerate_offer(raw, channel["key"], user, snapshot, limit=limit)
            _need(offer["offer_id"] not in byid, "DUPLICATE_NATIVE_OFFER_ID")
            byid.add(offer["offer_id"])
            found.append(offer)
    _need(len(found) == base["candidate_count"], "SLICE_A_NATIVE_OFFER_COUNT_MISMATCH")
    return {
        "contract": FRONTIER_CONTRACT,
        "source_contract": base["contract"],
        "snapshot_identity": canonical_sha256(snapshot),
        "capture_identity": canonical_sha256(capture),
        "receipt_identity": canonical_sha256(receipt),
        "week": receipt["week"],
        "offers": found,
        "offer_count": len(found),
        "couplings": _couplings(found),
        "eligible_for_approval_count": 0,
        "state": "BLOCKED_FROZEN_STRUCTURAL_FRONTIER_ONLY",
        "espn_action_authority": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--capture", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--out", type=Path, help="private local report; never commit")
    args = ap.parse_args(argv)
    print("WEEK8 SLICE B1 FROZEN STRUCTURAL TRADE FRONTIER", flush=True)
    try:
        docs = [json.loads(p.read_text(encoding="utf-8-sig")) for p in
                (args.snapshot, args.capture, args.receipt)]
        result = build_frontier(*docs)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("x", encoding="utf-8") as fh:
                json.dump(result, fh, sort_keys=True, indent=2)
                fh.write("\n")
        print("FROZEN_INPUTS=PASS;NATIVE_OFFERS=" + str(result["offer_count"]) +
              ";OFFER_COUPLINGS=" + str(len(result["couplings"])), flush=True)
        for row in result["offers"]:
            print("STRUCTURAL_TRADE_FRONTIER=" + json.dumps({
                "offer_id": row["offer_id"], "give": row["give"], "receive": row["receive"],
                "structural_options": row["structural_options_total_enumerated"],
                "native_auto_drops": row["modeled_native_auto_drop_ids"],
                "future_fills": row["modeled_native_auto_add_ids"],
                "blockers": row["blocking_evidence"], "decision": row["decision"]}, sort_keys=True), flush=True)
        print("CERTIFIED_ACTIONS=0;NO_MC_REEVALUATION=TRUE;ESPN_WRITES=NONE;ACTION_AUTHORITY=NONE")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("B1_BLOCKED=" + (str(exc) if isinstance(exc, CertificationBlocked) else type(exc).__name__) +
              ";ACTION_AUTHORITY=NONE")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
