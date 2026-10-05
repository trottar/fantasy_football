from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
PHASE_A_CONTRACT = "HISTORICAL_COUNTERFACTUAL_REPLAY_PHASE_A_V001"

CAUSAL_FROZEN_REPLAY = "CAUSAL_FROZEN_REPLAY"
RECONSTRUCTED_RETROSPECTIVE_REPLAY = "RECONSTRUCTED_RETROSPECTIVE_REPLAY"

PROVENANCE_FROZEN = "FROZEN"
PROVENANCE_RECONSTRUCTED = "RECONSTRUCTED"
PROVENANCE_MISSING = "MISSING"
PROVENANCE_NOT_APPLICABLE = "NOT_APPLICABLE"

_ALLOWED_PROVENANCE = {
    PROVENANCE_FROZEN,
    PROVENANCE_RECONSTRUCTED,
    PROVENANCE_MISSING,
    PROVENANCE_NOT_APPLICABLE,
}

_FORBIDDEN_PHASE_A_KEYS = {
    "actual",
    "actual_points",
    "actual_score",
    "final_points",
    "final_score",
    "game_result",
    "matchup_result",
    "observed",
    "observed_outcomes",
    "observed_points",
    "oracle_score",
    "outcome",
    "outcomes",
    "realized_points",
    "realized_score",
}


class ReplayContractError(ValueError):
    """Replay receipt violates the decision-science contract."""


class OutcomeAccessError(RuntimeError):
    """Observed outcomes were requested before the Phase-A freeze boundary."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return value


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _thaw(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _forbid_phase_a_outcome_keys(value: Any, *, path: str = "phase_a") -> None:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            key = str(raw_key).strip().lower()
            current = f"{path}.{raw_key}"
            if key in _FORBIDDEN_PHASE_A_KEYS:
                raise ReplayContractError(
                    f"observed-outcome field is forbidden in Phase A: {current}"
                )
            _forbid_phase_a_outcome_keys(nested, path=current)
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _forbid_phase_a_outcome_keys(nested, path=f"{path}[{index}]")


@dataclass(frozen=True)
class DependencyProvenance:
    key: str
    channel: str
    status: str
    material: bool = True
    artifact: str | None = None
    sha256: str | None = None
    captured_utc: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ReplayContractError("dependency key must be non-empty")
        if not self.channel.strip():
            raise ReplayContractError("dependency channel must be non-empty")
        if self.status not in _ALLOWED_PROVENANCE:
            raise ReplayContractError(f"unsupported provenance status: {self.status}")
        if self.sha256 is not None:
            digest = self.sha256.strip().lower()
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ReplayContractError(
                    f"dependency sha256 must be a 64-character hex digest: {self.key}"
                )
            object.__setattr__(self, "sha256", digest)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "channel": self.channel,
            "status": self.status,
            "material": bool(self.material),
            "artifact": self.artifact,
            "sha256": self.sha256,
            "captured_utc": self.captured_utc,
            "note": self.note,
        }


@dataclass(frozen=True)
class ProvenanceClassification:
    replay_mode: str
    reconstructed: tuple[str, ...]
    missing: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_mode": self.replay_mode,
            "reconstructed": list(self.reconstructed),
            "missing": list(self.missing),
        }


def classify_replay_mode(
    dependencies: Sequence[DependencyProvenance],
) -> ProvenanceClassification:
    material = [row for row in dependencies if row.material]
    if not material:
        raise ReplayContractError("at least one material dependency is required")

    seen: set[tuple[str, str]] = set()
    reconstructed: list[str] = []
    missing: list[str] = []
    for row in material:
        identity = (row.channel, row.key)
        if identity in seen:
            raise ReplayContractError(
                f"duplicate material dependency: {row.channel}:{row.key}"
            )
        seen.add(identity)
        label = f"{row.channel}:{row.key}"
        if row.status == PROVENANCE_RECONSTRUCTED:
            reconstructed.append(label)
        elif row.status == PROVENANCE_MISSING:
            missing.append(label)

    mode = (
        CAUSAL_FROZEN_REPLAY
        if not reconstructed and not missing
        else RECONSTRUCTED_RETROSPECTIVE_REPLAY
    )
    return ProvenanceClassification(
        replay_mode=mode,
        reconstructed=tuple(sorted(reconstructed)),
        missing=tuple(sorted(missing)),
    )


@dataclass(frozen=True)
class PhaseACandidate:
    candidate_id: str
    action_family: str
    rank: int
    prediction: Mapping[str, Any]
    uncertainty: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ReplayContractError("candidate_id must be non-empty")
        if not self.action_family.strip():
            raise ReplayContractError("action_family must be non-empty")
        if int(self.rank) < 1:
            raise ReplayContractError("candidate rank must be >= 1")
        _forbid_phase_a_outcome_keys(self.prediction, path="candidate.prediction")
        _forbid_phase_a_outcome_keys(self.uncertainty, path="candidate.uncertainty")
        object.__setattr__(self, "prediction", _freeze(self.prediction))
        object.__setattr__(self, "uncertainty", _freeze(self.uncertainty))

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "action_family": self.action_family,
            "rank": int(self.rank),
            "prediction": _thaw(self.prediction),
            "uncertainty": _thaw(self.uncertainty),
        }


@dataclass(frozen=True)
class PhaseAReceipt:
    schema_version: int
    contract: str
    frozen_utc: str
    season: int
    week: int
    replay_mode: str
    dependencies: tuple[DependencyProvenance, ...]
    reconstructed_dependencies: tuple[str, ...]
    missing_dependencies: tuple[str, ...]
    engine_identities: Mapping[str, Any]
    candidates: tuple[PhaseACandidate, ...]
    model_action: Mapping[str, Any]
    metadata: Mapping[str, Any]
    receipt_sha256: str

    def core_dict(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "contract": self.contract,
            "frozen_utc": self.frozen_utc,
            "season": int(self.season),
            "week": int(self.week),
            "replay_mode": self.replay_mode,
            "dependencies": [row.to_dict() for row in self.dependencies],
            "reconstructed_dependencies": list(self.reconstructed_dependencies),
            "missing_dependencies": list(self.missing_dependencies),
            "engine_identities": _thaw(self.engine_identities),
            "candidates": [row.to_dict() for row in self.candidates],
            "model_action": _thaw(self.model_action),
            "metadata": _thaw(self.metadata),
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.core_dict()
        out["receipt_sha256"] = self.receipt_sha256
        return out

    def verify(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ReplayContractError("unsupported Phase-A schema version")
        if self.contract != PHASE_A_CONTRACT:
            raise ReplayContractError("unsupported Phase-A contract")
        observed = canonical_sha256(self.core_dict())
        if observed != self.receipt_sha256:
            raise ReplayContractError(
                f"Phase-A receipt hash mismatch expected={self.receipt_sha256} "
                f"observed={observed}"
            )


def _dependency_from_mapping(row: Mapping[str, Any]) -> DependencyProvenance:
    return DependencyProvenance(
        key=str(row.get("key") or ""),
        channel=str(row.get("channel") or ""),
        status=str(row.get("status") or ""),
        material=bool(row.get("material", True)),
        artifact=row.get("artifact"),
        sha256=row.get("sha256"),
        captured_utc=row.get("captured_utc"),
        note=row.get("note"),
    )


def _candidate_from_mapping(row: Mapping[str, Any]) -> PhaseACandidate:
    prediction = row.get("prediction") or {}
    uncertainty = row.get("uncertainty") or {}
    if not isinstance(prediction, Mapping) or not isinstance(uncertainty, Mapping):
        raise ReplayContractError("candidate prediction/uncertainty must be mappings")
    return PhaseACandidate(
        candidate_id=str(row.get("candidate_id") or ""),
        action_family=str(row.get("action_family") or ""),
        rank=int(row.get("rank") or 0),
        prediction=prediction,
        uncertainty=uncertainty,
    )


def freeze_phase_a_receipt(
    *,
    frozen_utc: str,
    season: int,
    week: int,
    dependencies: Sequence[DependencyProvenance | Mapping[str, Any]],
    engine_identities: Mapping[str, Any],
    candidates: Sequence[PhaseACandidate | Mapping[str, Any]],
    model_action: Mapping[str, Any],
    metadata: Mapping[str, Any] | None = None,
) -> PhaseAReceipt:
    dependency_rows = tuple(
        row if isinstance(row, DependencyProvenance) else _dependency_from_mapping(row)
        for row in dependencies
    )
    classification = classify_replay_mode(dependency_rows)

    candidate_rows = tuple(
        row if isinstance(row, PhaseACandidate) else _candidate_from_mapping(row)
        for row in candidates
    )
    candidate_rows = tuple(sorted(candidate_rows, key=lambda row: row.rank))
    ranks = [row.rank for row in candidate_rows]
    if ranks != list(range(1, len(candidate_rows) + 1)):
        raise ReplayContractError(
            "candidate ranks must be unique and contiguous starting at 1"
        )
    candidate_ids = [row.candidate_id for row in candidate_rows]
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ReplayContractError("candidate_id values must be unique")

    _forbid_phase_a_outcome_keys(engine_identities, path="engine_identities")
    _forbid_phase_a_outcome_keys(model_action, path="model_action")
    _forbid_phase_a_outcome_keys(metadata or {}, path="metadata")

    selected = model_action.get("candidate_id")
    if selected is not None and str(selected) not in set(candidate_ids):
        raise ReplayContractError(
            "model_action.candidate_id must refer to a frozen Phase-A candidate"
        )

    dependency_rows = tuple(
        sorted(dependency_rows, key=lambda row: (row.channel, row.key))
    )
    frozen_engine = _freeze(engine_identities)
    frozen_action = _freeze(model_action)
    frozen_metadata = _freeze(metadata or {})

    core = {
        "schema_version": SCHEMA_VERSION,
        "contract": PHASE_A_CONTRACT,
        "frozen_utc": str(frozen_utc),
        "season": int(season),
        "week": int(week),
        "replay_mode": classification.replay_mode,
        "dependencies": [row.to_dict() for row in dependency_rows],
        "reconstructed_dependencies": list(classification.reconstructed),
        "missing_dependencies": list(classification.missing),
        "engine_identities": _thaw(frozen_engine),
        "candidates": [row.to_dict() for row in candidate_rows],
        "model_action": _thaw(frozen_action),
        "metadata": _thaw(frozen_metadata),
    }
    digest = canonical_sha256(core)
    receipt = PhaseAReceipt(
        schema_version=SCHEMA_VERSION,
        contract=PHASE_A_CONTRACT,
        frozen_utc=str(frozen_utc),
        season=int(season),
        week=int(week),
        replay_mode=classification.replay_mode,
        dependencies=dependency_rows,
        reconstructed_dependencies=classification.reconstructed,
        missing_dependencies=classification.missing,
        engine_identities=frozen_engine,
        candidates=candidate_rows,
        model_action=frozen_action,
        metadata=frozen_metadata,
        receipt_sha256=digest,
    )
    receipt.verify()
    return receipt


def phase_a_receipt_from_dict(payload: Mapping[str, Any]) -> PhaseAReceipt:
    dependencies = payload.get("dependencies")
    candidates = payload.get("candidates")
    if not isinstance(dependencies, list) or not isinstance(candidates, list):
        raise ReplayContractError("Phase-A dependencies/candidates must be lists")
    engine = payload.get("engine_identities") or {}
    action = payload.get("model_action") or {}
    metadata = payload.get("metadata") or {}
    if not all(isinstance(x, Mapping) for x in (engine, action, metadata)):
        raise ReplayContractError(
            "Phase-A engine_identities/model_action/metadata must be mappings"
        )

    receipt = freeze_phase_a_receipt(
        frozen_utc=str(payload.get("frozen_utc") or ""),
        season=int(payload.get("season") or 0),
        week=int(payload.get("week") or 0),
        dependencies=[
            _dependency_from_mapping(row)
            for row in dependencies
            if isinstance(row, Mapping)
        ],
        engine_identities=engine,
        candidates=[
            _candidate_from_mapping(row)
            for row in candidates
            if isinstance(row, Mapping)
        ],
        model_action=action,
        metadata=metadata,
    )
    if int(payload.get("schema_version") or 0) != SCHEMA_VERSION:
        raise ReplayContractError("unsupported Phase-A schema version")
    if str(payload.get("contract") or "") != PHASE_A_CONTRACT:
        raise ReplayContractError("unsupported Phase-A contract")
    expected = str(payload.get("receipt_sha256") or "")
    if not expected:
        raise ReplayContractError("Phase-A receipt_sha256 is required")
    if expected != receipt.receipt_sha256:
        raise ReplayContractError(
            f"Phase-A receipt hash mismatch expected={expected} "
            f"observed={receipt.receipt_sha256}"
        )
    return receipt


def save_phase_a_receipt(
    receipt: PhaseAReceipt,
    path: str | Path,
) -> Path:
    receipt.verify()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(str(target), flags, 0o644)
    try:
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise
    return target


def load_phase_a_receipt(path: str | Path) -> PhaseAReceipt:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        raise ReplayContractError("Phase-A receipt root must be an object")
    return phase_a_receipt_from_dict(payload)


@dataclass(frozen=True)
class PhaseBEnvelope:
    phase_a_receipt_sha256: str
    attached_utc: str
    outcomes: Mapping[str, Any]
    source_identities: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_a_receipt_sha256": self.phase_a_receipt_sha256,
            "attached_utc": self.attached_utc,
            "outcomes": _thaw(self.outcomes),
            "source_identities": _thaw(self.source_identities),
        }


class ReplayOutcomeFirewall:
    """Enforces the Phase-A freeze before observed outcomes can be attached."""

    def __init__(self) -> None:
        self._phase_a: PhaseAReceipt | None = None
        self._phase_b: PhaseBEnvelope | None = None

    @property
    def phase_a_frozen(self) -> bool:
        return self._phase_a is not None

    @property
    def phase_b_attached(self) -> bool:
        return self._phase_b is not None

    @property
    def phase_a_receipt(self) -> PhaseAReceipt | None:
        return self._phase_a

    @property
    def observed_outcomes(self) -> Mapping[str, Any]:
        if self._phase_b is None:
            raise OutcomeAccessError(
                "observed outcomes are unavailable until Phase A is frozen "
                "and Phase B is explicitly attached"
            )
        return self._phase_b.outcomes

    def freeze_phase_a(self, receipt: PhaseAReceipt) -> None:
        if self._phase_a is not None:
            raise ReplayContractError("Phase A is already frozen")
        receipt.verify()
        self._phase_a = receipt

    def attach_phase_b(
        self,
        *,
        attached_utc: str,
        outcomes: Mapping[str, Any],
        source_identities: Mapping[str, Any],
    ) -> PhaseBEnvelope:
        if self._phase_a is None:
            raise OutcomeAccessError(
                "cannot attach observed outcomes before Phase A is frozen"
            )
        if self._phase_b is not None:
            raise ReplayContractError("Phase B outcomes are already attached")
        self._phase_a.verify()
        envelope = PhaseBEnvelope(
            phase_a_receipt_sha256=self._phase_a.receipt_sha256,
            attached_utc=str(attached_utc),
            outcomes=_freeze(outcomes),
            source_identities=_freeze(source_identities),
        )
        self._phase_b = envelope
        return envelope
