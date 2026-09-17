from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
import re
from types import MappingProxyType
from typing import Iterable, Mapping

from .correlation import BoundaryKind
from .registry import CORE_SUBSYSTEMS


_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


class IntegrationSurface(str, Enum):
    CLI = "cli"
    SERVICE = "service"
    BACKGROUND_TASK = "background_task"
    GUI = "gui"
    SUBSYSTEM = "subsystem"


class IntegrationMode(str, Enum):
    SHADOW = "shadow"


def _clean_source_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("source_path must be a non-empty relative path")
    path = PurePosixPath(value.strip().replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("source_path must be repository-relative without '..'")
    if path.suffix != ".py":
        raise ValueError("source_path must point to a Python source file")
    return path.as_posix()


def _clean_symbol(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("symbol must be a non-empty descriptive target")
    value = value.strip()
    if len(value) > 160:
        raise ValueError("symbol exceeds 160 characters")
    return value


@dataclass(frozen=True)
class IntegrationPoint:
    name: str
    surface: IntegrationSurface
    subsystem: str
    source_path: str
    symbol: str
    boundary_kind: BoundaryKind
    mode: IntegrationMode = IntegrationMode.SHADOW
    automatic_emit: bool = False
    persistent: bool = False
    redaction_required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _NAME_RE.fullmatch(self.name):
            raise ValueError("integration point name must be dotted lowercase identifiers")
        if not isinstance(self.surface, IntegrationSurface):
            raise TypeError("surface must be an IntegrationSurface")
        if self.subsystem not in CORE_SUBSYSTEMS:
            raise ValueError(f"unsupported subsystem: {self.subsystem!r}")
        object.__setattr__(self, "source_path", _clean_source_path(self.source_path))
        object.__setattr__(self, "symbol", _clean_symbol(self.symbol))
        if not isinstance(self.boundary_kind, BoundaryKind):
            raise TypeError("boundary_kind must be a BoundaryKind")
        if not isinstance(self.mode, IntegrationMode):
            raise TypeError("mode must be an IntegrationMode")
        if not isinstance(self.automatic_emit, bool):
            raise TypeError("automatic_emit must be bool")
        if not isinstance(self.persistent, bool):
            raise TypeError("persistent must be bool")
        if not isinstance(self.redaction_required, bool):
            raise TypeError("redaction_required must be bool")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "surface": self.surface.value,
            "subsystem": self.subsystem,
            "source_path": self.source_path,
            "symbol": self.symbol,
            "boundary_kind": self.boundary_kind.value,
            "mode": self.mode.value,
            "automatic_emit": self.automatic_emit,
            "persistent": self.persistent,
            "redaction_required": self.redaction_required,
        }


class IntegrationPlan:
    """Immutable proposed integration map; it performs no instrumentation."""

    def __init__(
        self,
        points: Iterable[IntegrationPoint],
        *,
        observer_only: bool = True,
    ) -> None:
        rows: dict[str, IntegrationPoint] = {}
        for point in points:
            if not isinstance(point, IntegrationPoint):
                raise TypeError("plan points must be IntegrationPoint values")
            if point.name in rows:
                raise ValueError(f"duplicate integration point: {point.name}")
            rows[point.name] = point
        if not rows:
            raise ValueError("integration plan requires at least one point")
        if not isinstance(observer_only, bool):
            raise TypeError("observer_only must be bool")
        if observer_only:
            unsafe = [
                point.name
                for point in rows.values()
                if point.automatic_emit or point.persistent
            ]
            if unsafe:
                raise ValueError(
                    "observer-only integration plan cannot auto-emit or persist: "
                    + ", ".join(unsafe)
                )
        self._points: Mapping[str, IntegrationPoint] = MappingProxyType(rows)
        self.observer_only = observer_only

    def __len__(self) -> int:
        return len(self._points)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._points)

    @property
    def source_paths(self) -> tuple[str, ...]:
        return tuple(sorted({point.source_path for point in self._points.values()}))

    def require(self, name: str) -> IntegrationPoint:
        try:
            return self._points[name]
        except KeyError as exc:
            raise KeyError(f"integration point is not registered: {name}") from exc

    def to_dict(self) -> dict[str, object]:
        return {
            "observer_only": self.observer_only,
            "points": [point.to_dict() for point in self._points.values()],
        }


@dataclass(frozen=True)
class PlanSourceCheck:
    ok: bool
    missing_paths: tuple[str, ...]
    checked_paths: tuple[str, ...]

    def require_ok(self) -> None:
        if not self.ok:
            raise ValueError(
                "integration plan source paths missing: " + ", ".join(self.missing_paths)
            )


def validate_plan_sources(
    plan: IntegrationPlan,
    repository_root: str | Path,
) -> PlanSourceCheck:
    if not isinstance(plan, IntegrationPlan):
        raise TypeError("plan must be an IntegrationPlan")
    root = Path(repository_root)
    checked = plan.source_paths
    missing = tuple(path for path in checked if not (root / path).is_file())
    return PlanSourceCheck(
        ok=not missing,
        missing_paths=missing,
        checked_paths=checked,
    )


def _point(
    name: str,
    surface: IntegrationSurface,
    subsystem: str,
    source_path: str,
    symbol: str,
    boundary_kind: BoundaryKind,
) -> IntegrationPoint:
    return IntegrationPoint(
        name=name,
        surface=surface,
        subsystem=subsystem,
        source_path=source_path,
        symbol=symbol,
        boundary_kind=boundary_kind,
        mode=IntegrationMode.SHADOW,
        automatic_emit=False,
        persistent=False,
        redaction_required=True,
    )


DEFAULT_INTEGRATION_PLAN = IntegrationPlan(
    (
        _point(
            "cli.command.dispatch",
            IntegrationSurface.CLI,
            "observability",
            "fantasy.py",
            "cmd_* command boundary",
            BoundaryKind.CLI,
        ),
        _point(
            "service.season_gui",
            IntegrationSurface.SERVICE,
            "gui",
            "src/gui/season_service.py",
            "SeasonGuiService public service methods",
            BoundaryKind.SERVICE,
        ),
        _point(
            "task.season_gui.background",
            IntegrationSurface.BACKGROUND_TASK,
            "gui",
            "src/gui/season_app.py",
            "GUI recompute/background task lifecycle",
            BoundaryKind.BACKGROUND_TASK,
        ),
        _point(
            "subsystem.player.predictive",
            IntegrationSurface.SUBSYSTEM,
            "player",
            "src/transaction_manager.py",
            "evaluate_roster_predictive",
            BoundaryKind.SUBSYSTEM,
        ),
        _point(
            "subsystem.dst.channel",
            IntegrationSurface.SUBSYSTEM,
            "dst",
            "src/specialist_policy_v032.py",
            "evaluate_defense_channel",
            BoundaryKind.SUBSYSTEM,
        ),
        _point(
            "subsystem.k.channel",
            IntegrationSurface.SUBSYSTEM,
            "k",
            "src/specialist_policy_v032.py",
            "evaluate_kicker_channel",
            BoundaryKind.SUBSYSTEM,
        ),
        _point(
            "subsystem.trade.search",
            IntegrationSurface.SUBSYSTEM,
            "trade",
            "src/market_manager.py",
            "search_trades",
            BoundaryKind.SUBSYSTEM,
        ),
        _point(
            "subsystem.closure.capture",
            IntegrationSurface.SUBSYSTEM,
            "closure",
            "src/closure.py",
            "build_pregame_capture_from_context",
            BoundaryKind.SUBSYSTEM,
        ),
        _point(
            "subsystem.data_source.season_sync",
            IntegrationSurface.SUBSYSTEM,
            "data_source",
            "src/season_snapshot.py",
            "sync_season_snapshot",
            BoundaryKind.SUBSYSTEM,
        ),
    ),
    observer_only=True,
)
