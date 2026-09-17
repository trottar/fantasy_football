from __future__ import annotations

from dataclasses import dataclass
import random
from statistics import median
import time
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class OverheadBudget:
    """Engineering gate for shadow instrumentation overhead.

    For operations below ``relative_floor_ns`` the absolute incremental budget
    is authoritative because relative percentages are unstable for tiny calls.
    At or above the floor, both absolute and relative budgets must pass.
    """

    max_incremental_ns: int = 1_000_000
    max_relative_fraction: float = 0.02
    relative_floor_ns: int = 1_000_000
    trials: int = 30
    warmups: int = 3

    def __post_init__(self) -> None:
        for field_name in ("max_incremental_ns", "relative_floor_ns", "trials"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{field_name} must be a positive integer")
        if isinstance(self.warmups, bool) or not isinstance(self.warmups, int) or self.warmups < 0:
            raise ValueError("warmups must be a non-negative integer")
        if not isinstance(self.max_relative_fraction, (int, float)) or self.max_relative_fraction < 0:
            raise ValueError("max_relative_fraction must be non-negative")


@dataclass(frozen=True)
class StateProbe:
    name: str
    capture: Callable[[], Any]
    restore: Callable[[Any], None]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("probe name must be non-empty")
        if not callable(self.capture) or not callable(self.restore):
            raise TypeError("probe capture/restore must be callable")


def python_random_probe() -> StateProbe:
    return StateProbe(
        name="python_random",
        capture=random.getstate,
        restore=random.setstate,
    )


@dataclass(frozen=True)
class OverheadEvaluation:
    baseline_ns: int
    observed_ns: int
    incremental_ns: int
    relative_fraction: float
    absolute_ok: bool
    relative_ok: bool

    @property
    def passed(self) -> bool:
        return self.absolute_ok and self.relative_ok

    def to_dict(self) -> dict[str, object]:
        return {
            "baseline_ns": self.baseline_ns,
            "observed_ns": self.observed_ns,
            "incremental_ns": self.incremental_ns,
            "relative_fraction": self.relative_fraction,
            "absolute_ok": self.absolute_ok,
            "relative_ok": self.relative_ok,
            "passed": self.passed,
        }


def evaluate_overhead(
    baseline_ns: int,
    observed_ns: int,
    budget: OverheadBudget,
) -> OverheadEvaluation:
    if not isinstance(budget, OverheadBudget):
        raise TypeError("budget must be an OverheadBudget")
    for field_name, value in (("baseline_ns", baseline_ns), ("observed_ns", observed_ns)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field_name} must be a non-negative integer")
    incremental = max(0, observed_ns - baseline_ns)
    relative = incremental / max(1, baseline_ns)
    absolute_ok = incremental <= budget.max_incremental_ns
    relative_ok = (
        True
        if baseline_ns < budget.relative_floor_ns
        else relative <= budget.max_relative_fraction
    )
    return OverheadEvaluation(
        baseline_ns=baseline_ns,
        observed_ns=observed_ns,
        incremental_ns=incremental,
        relative_fraction=relative,
        absolute_ok=absolute_ok,
        relative_ok=relative_ok,
    )


@dataclass(frozen=True)
class _Outcome:
    ok: bool
    value: Any = None
    error_type: str | None = None


def _invoke(fn: Callable[[], Any]) -> _Outcome:
    try:
        return _Outcome(True, value=fn())
    except Exception as exc:
        return _Outcome(False, error_type=type(exc).__name__)


def _outcomes_equal(
    left: _Outcome,
    right: _Outcome,
    equality: Callable[[Any, Any], bool],
) -> bool:
    if left.ok != right.ok:
        return False
    if not left.ok:
        return left.error_type == right.error_type
    return bool(equality(left.value, right.value))


@dataclass(frozen=True)
class BenchmarkGateResult:
    trials: int
    outputs_equal: bool
    exception_behavior_equal: bool
    states_equal: bool
    baseline_median_ns: int
    observed_median_ns: int
    overhead: OverheadEvaluation
    probe_names: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return (
            self.outputs_equal
            and self.exception_behavior_equal
            and self.states_equal
            and self.overhead.passed
        )

    def require_pass(self) -> None:
        if not self.passed:
            raise ValueError("observability non-interference/overhead gate failed")

    def to_dict(self) -> dict[str, object]:
        return {
            "trials": self.trials,
            "outputs_equal": self.outputs_equal,
            "exception_behavior_equal": self.exception_behavior_equal,
            "states_equal": self.states_equal,
            "baseline_median_ns": self.baseline_median_ns,
            "observed_median_ns": self.observed_median_ns,
            "overhead": self.overhead.to_dict(),
            "probe_names": list(self.probe_names),
            "passed": self.passed,
        }


def benchmark_pair(
    baseline: Callable[[], Any],
    observed: Callable[[], Any],
    *,
    budget: OverheadBudget | None = None,
    probes: Iterable[StateProbe] | None = None,
    equality: Callable[[Any, Any], bool] | None = None,
) -> BenchmarkGateResult:
    """Paired non-interference/overhead benchmark from identical probe state.

    Probe state is restored before the observed call and again after every pair,
    so the benchmark itself does not leave those state channels advanced.
    Exception messages and returned values are never stored in the gate result.
    """
    if not callable(baseline) or not callable(observed):
        raise TypeError("baseline and observed must be callable")
    active_budget = OverheadBudget() if budget is None else budget
    if not isinstance(active_budget, OverheadBudget):
        raise TypeError("budget must be an OverheadBudget or None")
    active_probes = tuple(probes) if probes is not None else (python_random_probe(),)
    if not active_probes:
        raise ValueError("at least one state probe is required")
    if any(not isinstance(probe, StateProbe) for probe in active_probes):
        raise TypeError("all probes must be StateProbe values")
    names = tuple(probe.name for probe in active_probes)
    if len(set(names)) != len(names):
        raise ValueError("probe names must be unique")
    compare = (lambda a, b: a == b) if equality is None else equality
    if not callable(compare):
        raise TypeError("equality must be callable")

    baseline_times: list[int] = []
    observed_times: list[int] = []
    outputs_equal = True
    exception_equal = True
    states_equal = True

    def one_pair(record: bool) -> None:
        nonlocal outputs_equal, exception_equal, states_equal
        initial = tuple(probe.capture() for probe in active_probes)
        try:
            start = time.perf_counter_ns()
            base = _invoke(baseline)
            base_ns = time.perf_counter_ns() - start
            base_end = tuple(probe.capture() for probe in active_probes)

            for probe, state in zip(active_probes, initial):
                probe.restore(state)

            start = time.perf_counter_ns()
            obs = _invoke(observed)
            obs_ns = time.perf_counter_ns() - start
            obs_end = tuple(probe.capture() for probe in active_probes)
        finally:
            for probe, state in zip(active_probes, initial):
                probe.restore(state)

        if record:
            baseline_times.append(base_ns)
            observed_times.append(obs_ns)
            same_outcome = _outcomes_equal(base, obs, compare)
            outputs_equal = outputs_equal and same_outcome
            exception_equal = exception_equal and (
                base.ok == obs.ok and (base.ok or base.error_type == obs.error_type)
            )
            states_equal = states_equal and base_end == obs_end

    for _ in range(active_budget.warmups):
        one_pair(False)
    for _ in range(active_budget.trials):
        one_pair(True)

    baseline_median = int(median(baseline_times))
    observed_median = int(median(observed_times))
    overhead = evaluate_overhead(
        baseline_median,
        observed_median,
        active_budget,
    )
    return BenchmarkGateResult(
        trials=active_budget.trials,
        outputs_equal=outputs_equal,
        exception_behavior_equal=exception_equal,
        states_equal=states_equal,
        baseline_median_ns=baseline_median,
        observed_median_ns=observed_median,
        overhead=overhead,
        probe_names=names,
    )
