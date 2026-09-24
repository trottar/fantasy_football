from datetime import datetime, timezone
from pathlib import Path
import random

import pytest

from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    evaluate_overhead,
    python_random_probe,
)
from src.observability.context import RunContext
from src.observability.correlation import begin_cli_action
from src.observability.integration_plan import (
    DEFAULT_INTEGRATION_PLAN,
    IntegrationMode,
    IntegrationPlan,
    IntegrationPoint,
    IntegrationSurface,
    validate_plan_sources,
)
from src.observability.correlation import BoundaryKind

UTC = timezone.utc


def _context():
    return RunContext.create(
        subsystem="observability",
        run_id="run:gate",
        timestamp=datetime(2026, 9, 17, 19, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="116c99ebc3bab3db6b27cb8ddb5f7100cbd2b113",
    )


def test_default_plan_is_shadow_observer_only_and_names_real_surfaces():
    plan = DEFAULT_INTEGRATION_PLAN
    assert plan.observer_only
    assert len(plan) >= 8
    assert {
        "cli.command.dispatch",
        "service.season_gui",
        "task.season_gui.background",
        "subsystem.player.predictive",
        "subsystem.dst.channel",
        "subsystem.k.channel",
        "subsystem.behavior.trade_response_probabilities",
        "subsystem.closure.capture",
    }.issubset(set(plan.names))
    for name in plan.names:
        point = plan.require(name)
        assert point.mode is IntegrationMode.SHADOW
        assert point.automatic_emit is False
        assert point.persistent is False
        assert point.redaction_required is True


def test_default_plan_source_paths_exist_in_authoritative_repository():
    root = Path(__file__).resolve().parents[1]
    result = validate_plan_sources(DEFAULT_INTEGRATION_PLAN, root)
    assert result.ok, result.missing_paths


def test_observer_only_plan_rejects_automatic_emit_or_persistence():
    point = IntegrationPoint(
        name="cli.unsafe",
        surface=IntegrationSurface.CLI,
        subsystem="observability",
        source_path="fantasy.py",
        symbol="cmd_*",
        boundary_kind=BoundaryKind.CLI,
        automatic_emit=True,
    )
    with pytest.raises(ValueError, match="cannot auto-emit or persist"):
        IntegrationPlan((point,), observer_only=True)


def test_integration_point_rejects_parent_escape_source_path():
    with pytest.raises(ValueError, match="repository-relative"):
        IntegrationPoint(
            name="cli.bad_path",
            surface=IntegrationSurface.CLI,
            subsystem="observability",
            source_path="../fantasy.py",
            symbol="cmd_*",
            boundary_kind=BoundaryKind.CLI,
        )


def test_overhead_evaluation_uses_absolute_gate_for_tiny_calls():
    budget = OverheadBudget(
        max_incremental_ns=1_000_000,
        max_relative_fraction=0.02,
        relative_floor_ns=1_000_000,
        trials=1,
        warmups=0,
    )
    result = evaluate_overhead(10_000, 100_000, budget)
    assert result.passed
    assert result.relative_fraction > 1.0


def test_overhead_evaluation_requires_relative_budget_above_floor():
    budget = OverheadBudget(
        max_incremental_ns=1_000_000,
        max_relative_fraction=0.02,
        relative_floor_ns=1_000_000,
        trials=1,
        warmups=0,
    )
    assert evaluate_overhead(10_000_000, 10_100_000, budget).passed
    assert not evaluate_overhead(10_000_000, 10_500_000, budget).passed


def test_benchmark_pair_passes_for_observational_boundary_and_restores_rng():
    context = _context()
    random.seed(123456)
    before = random.getstate()

    def baseline():
        return {"value": 7, "channel": "player"}

    def observed():
        boundary = begin_cli_action(
            context,
            "benchmark",
            action_id="action:benchmark",
            attributes={"mode": "shadow"},
        )
        assert boundary.start_event.event_name == "action.start"
        return {"value": 7, "channel": "player"}

    result = benchmark_pair(
        baseline,
        observed,
        budget=OverheadBudget(
            max_incremental_ns=20_000_000,
            max_relative_fraction=1000.0,
            relative_floor_ns=1,
            trials=5,
            warmups=1,
        ),
    )
    assert result.passed
    assert random.getstate() == before
    assert result.probe_names == ("python_random",)


def test_benchmark_pair_detects_output_change_without_storing_outputs():
    result = benchmark_pair(
        lambda: 1,
        lambda: 2,
        budget=OverheadBudget(
            max_incremental_ns=20_000_000,
            max_relative_fraction=1000.0,
            relative_floor_ns=1,
            trials=2,
            warmups=0,
        ),
    )
    assert not result.outputs_equal
    assert not result.passed
    row = result.to_dict()
    assert "value" not in row
    assert "output" not in row


def test_benchmark_pair_detects_rng_interference_and_restores_caller_state():
    random.seed(991)
    before = random.getstate()

    def baseline():
        return "same"

    def observed():
        random.random()
        return "same"

    result = benchmark_pair(
        baseline,
        observed,
        budget=OverheadBudget(
            max_incremental_ns=20_000_000,
            max_relative_fraction=1000.0,
            relative_floor_ns=1,
            trials=2,
            warmups=0,
        ),
    )
    assert not result.states_equal
    assert not result.passed
    assert random.getstate() == before


def test_benchmark_pair_compares_exception_type_without_message_leakage():
    def first():
        raise ValueError("secret-one")

    def second():
        raise ValueError("secret-two")

    result = benchmark_pair(
        first,
        second,
        budget=OverheadBudget(
            max_incremental_ns=20_000_000,
            max_relative_fraction=1000.0,
            relative_floor_ns=1,
            trials=2,
            warmups=0,
        ),
    )
    assert result.outputs_equal
    assert result.exception_behavior_equal
    text = str(result.to_dict())
    assert "secret-one" not in text
    assert "secret-two" not in text


def test_custom_state_probe_detects_state_change_and_is_restored():
    state = {"counter": 0}

    def capture():
        return state["counter"]

    def restore(value):
        state["counter"] = value

    probe = StateProbe("counter", capture, restore)

    def baseline():
        return 1

    def observed():
        state["counter"] += 1
        return 1

    result = benchmark_pair(
        baseline,
        observed,
        probes=(probe,),
        budget=OverheadBudget(
            max_incremental_ns=20_000_000,
            max_relative_fraction=1000.0,
            relative_floor_ns=1,
            trials=2,
            warmups=0,
        ),
    )
    assert not result.states_equal
    assert state["counter"] == 0


def test_duplicate_probe_names_rejected():
    probe = python_random_probe()
    with pytest.raises(ValueError, match="unique"):
        benchmark_pair(
            lambda: 1,
            lambda: 1,
            probes=(probe, probe),
            budget=OverheadBudget(trials=1, warmups=0),
        )
