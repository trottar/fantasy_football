from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


REQUIRED_PROVIDER_KEYS = (
    "espn",
    "sleeper",
    "nflverse_rosters",
    "nflverse_matchups",
    "nfl_official_rosters",
    "nfl_official",
)

PASS = "PASS"
BLOCKED = "BLOCKED_HEALTH"


@dataclass(frozen=True)
class HealthItem:
    key: str
    status: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperationalHealthReceipt:
    schema_version: int
    generated_utc: str
    status: str
    items: tuple[HealthItem, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "generated_utc": self.generated_utc,
            "status": self.status,
            "items": [item.to_dict() for item in self.items],
            "blockers": list(self.blockers),
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truthy_source_status(key: str, item: Any, *, snapshot_present: bool) -> tuple[bool, str]:
    if item is None:
        if key == "espn" and snapshot_present:
            return True, "snapshot present"
        return False, "status missing"
    if not isinstance(item, Mapping):
        return False, "malformed status"
    if key == "nfl_official_rosters" and item.get("complete") is not None:
        ok = bool(item.get("complete"))
    else:
        ok = bool(item.get("ok", item.get("complete", False)))
    detail = str(item.get("error") or item.get("detail") or ("OK" if ok else "not healthy"))
    return ok, detail


def capture_integrity_state(capture: Mapping[str, Any] | None) -> tuple[bool, list[str]]:
    """Return whether the prospective capture is usable without importing outcome data.

    Integrity verification is delegated to the commissioned prospective-measurement
    implementation.  Gate A additionally requires the explicit pre-data firewall
    fields that protect the v0.X information boundary.
    """
    if not capture:
        return False, ["prospective capture missing"]
    try:
        from .prospective_measurement_v034 import verify_capture_integrity

        integrity_ok = bool(verify_capture_integrity(dict(capture)))
    except Exception as exc:  # fail closed; the caller records type only
        return False, [f"capture integrity verifier failed:{type(exc).__name__}"]
    reasons: list[str] = []
    if not integrity_ok:
        reasons.append("capture integrity failed")
    firewall = capture.get("pre_data_firewall")
    if not isinstance(firewall, Mapping):
        reasons.append("pre-data firewall missing")
    else:
        expected_false = (
            "2026_game_outcomes_used_for_tuning",
            "automatic_refit",
            "automatic_calibration",
        )
        for key in expected_false:
            if firewall.get(key) is not False:
                reasons.append(f"pre-data firewall {key} must be false")
    return not reasons, reasons


def build_operational_health_receipt(
    *,
    snapshot: Mapping[str, Any],
    capture: Mapping[str, Any] | None,
    commissioning_identity: Mapping[str, Any] | None,
    observed_dependencies: Mapping[str, str],
    observed_runtime_version: str | None,
    memory_health: Mapping[str, Any] | None,
    persistence_state: Any,
    unresolved_diagnostics: Sequence[str] = (),
    receipt_inventory: Sequence[str] = (),
    required_receipts: Sequence[str] = (),
) -> OperationalHealthReceipt:
    """Build the weekly operational-health gate from explicit evidence.

    The function deliberately does not infer repository/runtime commissioning from
    the current working directory.  That identity must be supplied by the
    commissioned runtime/operator boundary.  This keeps control-root Git metadata,
    installed runtime state, and remote repository state distinct.
    """
    items: list[HealthItem] = []
    blockers: list[str] = []

    identity = dict(commissioning_identity or {})
    source_checkpoint = str(identity.get("source_checkpoint") or "").strip()
    expected_runtime = str(identity.get("runtime_version") or "").strip()
    commissioned = identity.get("commissioned") is True
    expected_dependencies = identity.get("dependencies")
    if not isinstance(expected_dependencies, Mapping):
        expected_dependencies = {}

    identity_reasons: list[str] = []
    if not commissioned:
        identity_reasons.append("commissioned runtime identity missing or not commissioned")
    if not source_checkpoint:
        identity_reasons.append("source checkpoint missing")
    if not expected_runtime:
        identity_reasons.append("runtime version missing")
    if not observed_runtime_version:
        identity_reasons.append("observed runtime VERSION missing")
    elif expected_runtime and str(observed_runtime_version).strip() != expected_runtime:
        identity_reasons.append(
            f"runtime version mismatch expected={expected_runtime} observed={observed_runtime_version}"
        )
    if not expected_dependencies:
        identity_reasons.append("commissioned dependency identities missing")
    else:
        for key, expected in expected_dependencies.items():
            observed = observed_dependencies.get(str(key))
            if not observed:
                identity_reasons.append(f"dependency identity missing:{key}")
            elif str(observed) != str(expected):
                identity_reasons.append(f"dependency identity mismatch:{key}")
    identity_ok = not identity_reasons
    if not identity_ok:
        blockers.extend(f"runtime_identity:{reason}" for reason in identity_reasons)
    items.append(
        HealthItem(
            "runtime_identity",
            PASS if identity_ok else BLOCKED,
            {
                "source_checkpoint": source_checkpoint or None,
                "expected_runtime_version": expected_runtime or None,
                "observed_runtime_version": observed_runtime_version,
                "expected_dependencies": dict(expected_dependencies),
                "observed_dependencies": dict(observed_dependencies),
                "reasons": identity_reasons,
            },
        )
    )

    statuses = snapshot.get("source_status") if isinstance(snapshot, Mapping) else None
    statuses = statuses if isinstance(statuses, Mapping) else {}
    provider_rows: dict[str, Any] = {}
    provider_ok = True
    for key in REQUIRED_PROVIDER_KEYS:
        ok, detail = _truthy_source_status(key, statuses.get(key), snapshot_present=bool(snapshot))
        provider_rows[key] = {"ok": ok, "detail": detail}
        if not ok:
            provider_ok = False
            blockers.append(f"provider:{key}:{detail}")
    items.append(HealthItem("provider_health", PASS if provider_ok else BLOCKED, provider_rows))

    capture_ok, capture_reasons = capture_integrity_state(capture)
    if not capture_ok:
        blockers.extend(f"capture:{reason}" for reason in capture_reasons)
    items.append(
        HealthItem(
            "capture_integrity_predata_firewall",
            PASS if capture_ok else BLOCKED,
            {
                "capture_present": bool(capture),
                "capture_integrity": bool(capture_ok),
                "reasons": capture_reasons,
            },
        )
    )

    pstate = persistence_state
    failed = bool(getattr(pstate, "failed", False))
    enabled = bool(getattr(pstate, "enabled", False))
    failures = int(getattr(pstate, "failures", 0) or 0)
    disabled_reason = getattr(pstate, "disabled_reason", None)
    persistence_ok = not failed
    if not persistence_ok:
        blockers.append("persistence:observer persistence reports failure")
    items.append(
        HealthItem(
            "persistence_non_interference",
            PASS if persistence_ok else BLOCKED,
            {
                "enabled": enabled,
                "failed": failed,
                "failures": failures,
                "disabled_reason": disabled_reason,
            },
        )
    )

    mem = dict(memory_health or {})
    mem_status = str(mem.get("status") or "").strip().upper()
    mem_checkpoint = str(mem.get("source_checkpoint") or "").strip()
    memory_ok = mem_status in {"PASS", "HEALTHY"}
    memory_reasons: list[str] = []
    if not memory_ok:
        memory_reasons.append("strict durable-memory health missing or failed")
    if source_checkpoint and mem_checkpoint != source_checkpoint:
        memory_ok = False
        memory_reasons.append(
            f"memory-health checkpoint mismatch expected={source_checkpoint} observed={mem_checkpoint or '-'}"
        )
    if not memory_ok:
        blockers.extend(f"memory_health:{reason}" for reason in memory_reasons)
    items.append(
        HealthItem(
            "durable_memory_health",
            PASS if memory_ok else BLOCKED,
            {**mem, "reasons": memory_reasons},
        )
    )

    unresolved = [str(x) for x in unresolved_diagnostics if str(x).strip()]
    diagnostics_ok = not unresolved
    if unresolved:
        blockers.extend(f"diagnostic:{x}" for x in unresolved)
    items.append(
        HealthItem(
            "unresolved_diagnostics",
            PASS if diagnostics_ok else BLOCKED,
            {"blockers": unresolved},
        )
    )

    present = {str(x) for x in receipt_inventory}
    required = {str(x) for x in required_receipts}
    missing = sorted(required - present)
    inventory_ok = not missing
    if missing:
        blockers.extend(f"receipt_inventory:missing:{x}" for x in missing)
    items.append(
        HealthItem(
            "decision_receipt_inventory",
            PASS if inventory_ok else BLOCKED,
            {"required": sorted(required), "present": sorted(present), "missing": missing},
        )
    )

    return OperationalHealthReceipt(
        schema_version=1,
        generated_utc=utc_now(),
        status=PASS if not blockers else BLOCKED,
        items=tuple(items),
        blockers=tuple(blockers),
    )
