from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import re
from typing import Any
from uuid import uuid4


_SUBSYSTEM_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _utc(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _optional_text(value: str | None, field: str, max_length: int = 256) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string or None")
    value = value.strip()
    if not value:
        raise ValueError(f"{field} cannot be empty")
    if len(value) > max_length:
        raise ValueError(f"{field} exceeds {max_length} characters")
    return value


def _id(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ValueError(
            f"{field} must match {_ID_RE.pattern!r}; received {value!r}"
        )
    return value


def _hash(value: str | None, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _HASH_RE.fullmatch(value):
        raise ValueError(f"{field} must be a 64-character hexadecimal SHA-256")
    return value.lower()


def _subsystem(value: str) -> str:
    if not isinstance(value, str) or not _SUBSYSTEM_RE.fullmatch(value):
        raise ValueError(
            f"subsystem must match {_SUBSYSTEM_RE.pattern!r}; received {value!r}"
        )
    return value


def new_correlation_id(prefix: str) -> str:
    """Return a UUID-backed ID without touching Python's pseudo-random stream."""
    prefix = _subsystem(prefix.replace("-", "_"))
    return f"{prefix}:{uuid4().hex}"


@dataclass(frozen=True)
class RunContext:
    """Immutable provenance and correlation context for a run or nested action."""

    run_id: str
    timestamp: datetime
    subsystem: str
    release_version: str | None = None
    source_commit: str | None = None
    week: int | None = None
    decision_time: datetime | None = None
    data_as_of: datetime | None = None
    scenario_id: str | None = None
    random_seed: int | None = None
    crn_group_id: str | None = None
    config_hash: str | None = None
    input_snapshot_hash: str | None = None
    action_id: str | None = None
    parent_action_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", _id(self.run_id, "run_id"))
        object.__setattr__(self, "timestamp", _utc(self.timestamp, "timestamp"))
        object.__setattr__(self, "subsystem", _subsystem(self.subsystem))
        object.__setattr__(
            self,
            "release_version",
            _optional_text(self.release_version, "release_version", 128),
        )
        object.__setattr__(
            self,
            "source_commit",
            _optional_text(self.source_commit, "source_commit", 128),
        )

        if self.week is not None:
            if isinstance(self.week, bool) or not isinstance(self.week, int):
                raise TypeError("week must be an integer or None")
            if self.week < 1:
                raise ValueError("week must be >= 1")

        if self.decision_time is not None:
            object.__setattr__(
                self,
                "decision_time",
                _utc(self.decision_time, "decision_time"),
            )
        if self.data_as_of is not None:
            object.__setattr__(
                self,
                "data_as_of",
                _utc(self.data_as_of, "data_as_of"),
            )

        if self.scenario_id is not None:
            object.__setattr__(
                self,
                "scenario_id",
                _id(self.scenario_id, "scenario_id"),
            )
        if self.random_seed is not None:
            if isinstance(self.random_seed, bool) or not isinstance(
                self.random_seed, int
            ):
                raise TypeError("random_seed must be an integer or None")
        if self.crn_group_id is not None:
            object.__setattr__(
                self,
                "crn_group_id",
                _id(self.crn_group_id, "crn_group_id"),
            )

        object.__setattr__(
            self,
            "config_hash",
            _hash(self.config_hash, "config_hash"),
        )
        object.__setattr__(
            self,
            "input_snapshot_hash",
            _hash(self.input_snapshot_hash, "input_snapshot_hash"),
        )

        if self.action_id is not None:
            object.__setattr__(
                self,
                "action_id",
                _id(self.action_id, "action_id"),
            )
        if self.parent_action_id is not None:
            object.__setattr__(
                self,
                "parent_action_id",
                _id(self.parent_action_id, "parent_action_id"),
            )
        if self.action_id is None and self.parent_action_id is not None:
            raise ValueError(
                "parent_action_id requires an action_id on the current context"
            )

    @classmethod
    def create(
        cls,
        *,
        subsystem: str,
        timestamp: datetime | None = None,
        run_id: str | None = None,
        **kwargs: Any,
    ) -> "RunContext":
        return cls(
            run_id=run_id or new_correlation_id("run"),
            timestamp=timestamp or datetime.now(timezone.utc),
            subsystem=subsystem,
            **kwargs,
        )

    @property
    def correlation_id(self) -> str:
        return self.action_id or self.run_id

    def for_action(
        self,
        *,
        subsystem: str | None = None,
        action_id: str | None = None,
        scenario_id: str | None = None,
        random_seed: int | None = None,
        crn_group_id: str | None = None,
    ) -> "RunContext":
        """Return a child action context while preserving immutable run provenance."""
        return replace(
            self,
            subsystem=self.subsystem if subsystem is None else subsystem,
            action_id=action_id or new_correlation_id("action"),
            parent_action_id=self.action_id,
            scenario_id=self.scenario_id if scenario_id is None else scenario_id,
            random_seed=self.random_seed if random_seed is None else random_seed,
            crn_group_id=self.crn_group_id if crn_group_id is None else crn_group_id,
        )

    def provenance(self) -> dict[str, str | None]:
        return {
            "release_version": self.release_version,
            "source_commit": self.source_commit,
            "config_hash": self.config_hash,
            "input_snapshot_hash": self.input_snapshot_hash,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "timestamp": _iso(self.timestamp),
            "subsystem": self.subsystem,
            "release_version": self.release_version,
            "source_commit": self.source_commit,
            "week": self.week,
            "decision_time": _iso(self.decision_time),
            "data_as_of": _iso(self.data_as_of),
            "scenario_id": self.scenario_id,
            "random_seed": self.random_seed,
            "crn_group_id": self.crn_group_id,
            "config_hash": self.config_hash,
            "input_snapshot_hash": self.input_snapshot_hash,
            "action_id": self.action_id,
            "parent_action_id": self.parent_action_id,
        }
