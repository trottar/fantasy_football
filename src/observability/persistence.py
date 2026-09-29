from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import re
import threading

from .events import StructuredEvent
from .redaction import RedactionPolicy
from .sinks import RedactingJsonlSink


DEFAULT_ROTATE_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 256 * 1024 * 1024
_SEGMENT_RE = re.compile(
    r"^events-(?P<stamp>[0-9]{8}T[0-9]{6}Z)-p(?P<pid>[0-9]+)-s(?P<seq>[0-9]{4})\.jsonl$"
)


def default_persistence_root() -> Path:
    """Return the fixed local-only runtime observability directory."""
    return Path(__file__).resolve().parents[2] / "logs" / "observability"


@dataclass(frozen=True)
class PersistencePolicy:
    """Disabled-by-default local persistence limits.

    No retention deletion is performed. When the total storage ceiling is
    reached, new persistence stops while existing evidence remains untouched.
    """

    enabled: bool = False
    rotate_bytes: int = DEFAULT_ROTATE_BYTES
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a bool")
        for name, value in (
            ("rotate_bytes", self.rotate_bytes),
            ("max_total_bytes", self.max_total_bytes),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 1:
                raise ValueError(f"{name} must be >= 1")


@dataclass(frozen=True)
class PersistenceState:
    enabled: bool
    failed: bool
    failures: int
    disabled_reason: str | None
    active_path: str | None
    active_bytes: int
    total_bytes: int
    segments: int


class PersistenceController:
    """Fail-open redacting JSONL persistence owned by observability.

    The controller is independent of football/application business logic. It
    never deletes evidence. Disk/redaction/path failures disable future writes
    for this controller instance and are reported only as observer failures.
    """

    def __init__(
        self,
        root: str | Path,
        *,
        policy: PersistencePolicy | None = None,
        redaction_policy: RedactionPolicy | None = None,
    ) -> None:
        self.root = Path(root)
        self.policy = PersistencePolicy() if policy is None else policy
        if not isinstance(self.policy, PersistencePolicy):
            raise TypeError("policy must be a PersistencePolicy or None")
        self.redaction_policy = (
            RedactionPolicy() if redaction_policy is None else redaction_policy
        )
        if not isinstance(self.redaction_policy, RedactionPolicy):
            raise TypeError("redaction_policy must be a RedactionPolicy or None")
        self._lock = threading.Lock()
        self._enabled = bool(self.policy.enabled)
        self._failed = False
        self._failures = 0
        self._disabled_reason: str | None = None
        self._active_path: Path | None = None
        self._active_day: date | None = None
        self._active_bytes = 0
        self._total_bytes: int | None = None
        self._segments: int | None = None
        self._sequence = 0
        self._active_is_new = False

    def _owned_segments(self) -> tuple[Path, ...]:
        if not self.root.exists():
            return ()
        out: list[Path] = []
        for path in self.root.iterdir():
            if path.is_file() and _SEGMENT_RE.fullmatch(path.name):
                out.append(path)
        return tuple(sorted(out, key=lambda item: item.name))

    def _inventory(self) -> None:
        segments = self._owned_segments()
        self._segments = len(segments)
        self._total_bytes = sum(path.stat().st_size for path in segments)

    def _disable(self, reason: str, *, failed: bool) -> None:
        self._enabled = False
        self._disabled_reason = reason
        if failed:
            self._failed = True
            self._failures += 1

    def _new_segment(self, event: StructuredEvent) -> None:
        stamp = event.timestamp.strftime("%Y%m%dT%H%M%SZ")
        event_day = event.timestamp.date()
        self.root.mkdir(parents=True, exist_ok=True)
        while True:
            self._sequence += 1
            name = (
                f"events-{stamp}-p{os.getpid()}-s{self._sequence:04d}.jsonl"
            )
            if not _SEGMENT_RE.fullmatch(name):
                raise RuntimeError("generated unsafe persistence segment name")
            path = self.root / name
            if not path.exists():
                break
        self._active_path = path
        self._active_day = event_day
        self._active_bytes = 0
        self._active_is_new = True
        if self._segments is None:
            self._inventory()

    def _ensure_segment(self, event: StructuredEvent) -> None:
        rotate = (
            self._active_path is None
            or self._active_day != event.timestamp.date()
            or self._active_bytes >= self.policy.rotate_bytes
        )
        if rotate:
            self._new_segment(event)

    def state(self) -> PersistenceState:
        with self._lock:
            if self._total_bytes is None or self._segments is None:
                try:
                    self._inventory()
                except OSError:
                    total = 0
                    segments = 0
                else:
                    total = int(self._total_bytes or 0)
                    segments = int(self._segments or 0)
            else:
                total = self._total_bytes
                segments = self._segments
            return PersistenceState(
                enabled=self._enabled,
                failed=self._failed,
                failures=self._failures,
                disabled_reason=self._disabled_reason,
                active_path=None if self._active_path is None else str(self._active_path),
                active_bytes=self._active_bytes,
                total_bytes=total,
                segments=segments,
            )

    def emit(self, event: StructuredEvent) -> bool | None:
        """Persist one event.

        Returns True after a successful write, False for the event that disables
        persistence because of a storage/disk failure, and None while disabled.
        No persistence exception escapes this method.
        """
        if not isinstance(event, StructuredEvent):
            raise TypeError("event must be a StructuredEvent")

        with self._lock:
            if not self._enabled:
                return None
            try:
                if self._total_bytes is None or self._segments is None:
                    self._inventory()
                assert self._total_bytes is not None
                if self._total_bytes >= self.policy.max_total_bytes:
                    self._disable("storage_limit", failed=False)
                    return False

                self._ensure_segment(event)
                assert self._active_path is not None
                before = self._active_path.stat().st_size if self._active_path.exists() else 0
                RedactingJsonlSink(
                    self._active_path,
                    policy=self.redaction_policy,
                    create_parents=True,
                    flush=True,
                ).emit(event)
                after = self._active_path.stat().st_size
                delta = max(0, after - before)
                self._active_bytes = after
                self._total_bytes += delta
                if self._active_is_new:
                    assert self._segments is not None
                    self._segments += 1
                    self._active_is_new = False

                if self._total_bytes >= self.policy.max_total_bytes:
                    self._disable("storage_limit", failed=False)
                return True
            except Exception as exc:
                self._disable(f"disk_error:{type(exc).__name__}", failed=True)
                return False


_GLOBAL_LOCK = threading.Lock()
_GLOBAL_CONTROLLER = PersistenceController(
    default_persistence_root(),
    policy=PersistencePolicy(enabled=False),
)


def configure_shadow_persistence(
    policy: PersistencePolicy,
    *,
    redaction_policy: RedactionPolicy | None = None,
) -> PersistenceState:
    """Install a process-level controller at the fixed runtime-local path.

    Source import alone never activates persistence. Production activation must
    call this function explicitly with ``PersistencePolicy(enabled=True)``.
    """
    global _GLOBAL_CONTROLLER
    if not isinstance(policy, PersistencePolicy):
        raise TypeError("policy must be a PersistencePolicy")
    controller = PersistenceController(
        default_persistence_root(),
        policy=policy,
        redaction_policy=redaction_policy,
    )
    with _GLOBAL_LOCK:
        _GLOBAL_CONTROLLER = controller
    return controller.state()


def disable_shadow_persistence(reason: str = "disabled") -> PersistenceState:
    global _GLOBAL_CONTROLLER
    if not isinstance(reason, str) or not reason:
        raise ValueError("reason must be a non-empty string")
    controller = PersistenceController(
        default_persistence_root(),
        policy=PersistencePolicy(enabled=False),
    )
    controller._disabled_reason = reason
    with _GLOBAL_LOCK:
        _GLOBAL_CONTROLLER = controller
    return controller.state()


def shadow_persistence_state() -> PersistenceState:
    with _GLOBAL_LOCK:
        controller = _GLOBAL_CONTROLLER
    return controller.state()


def persist_shadow_event(event: StructuredEvent) -> bool | None:
    with _GLOBAL_LOCK:
        controller = _GLOBAL_CONTROLLER
    return controller.emit(event)
