from dataclasses import FrozenInstanceError
from types import SimpleNamespace
import json
import random

import pytest

from src.observability.invariants import (
    CORE_INVARIANT_REGISTRY,
    InvariantDefinition,
    InvariantRegistry,
    InvariantSeverity,
    InvariantStatus,
)


def test_core_registry_contains_scientific_and_gui_contracts():
    expected = {
        "physics.channel_separation",
        "authority.screen_not_authority",
        "causality.prediction_frozen_before_outcome",
        "causality.information_not_after_decision",
        "randomness.crn_required_pairing",
        "league.dropped_players_retained",
        "separation.football_vs_behavior",
        "data.raw_vs_derived_separation",
        "gui.no_mutation_after_unmount",
        "gui.task_owned_and_cancelled",
        "gui.no_stale_service_write",
        "gui.refresh_render_correlated",
        "gui.exception_correlation_preserved",
    }
    assert expected.issubset(set(CORE_INVARIANT_REGISTRY.names))


def test_result_is_immutable_json_stable_and_context_correlated():
    context = SimpleNamespace(
        subsystem="gui",
        run_id="run:test",
        correlation_id="action:refresh",
    )
    source = {"items": [{"count": 2}]}
    result = CORE_INVARIANT_REGISTRY.result(
        "gui.no_stale_service_write",
        passed=False,
        context=context,
        message="stale target",
        details=source,
    )
    source["items"][0]["count"] = 99

    assert result.status is InvariantStatus.FAIL
    assert result.failed
    assert result.run_id == "run:test"
    assert result.correlation_id == "action:refresh"
    assert result.to_dict()["details"] == {"items": [{"count": 2}]}
    assert json.loads(result.to_json()) == result.to_dict()

    with pytest.raises(FrozenInstanceError):
        result.message = "mutate"
    with pytest.raises(TypeError):
        result.details["x"] = 1


def test_registry_enforces_gui_subsystem_and_duplicate_names():
    with pytest.raises(ValueError, match="does not allow subsystem"):
        CORE_INVARIANT_REGISTRY.result(
            "gui.no_mutation_after_unmount",
            passed=True,
            subsystem="player",
        )

    definition = InvariantDefinition(
        name="test.contract",
        description="test",
        severity=InvariantSeverity.DIAGNOSTIC,
    )
    with pytest.raises(ValueError, match="duplicate"):
        InvariantRegistry([definition, definition])


def test_pass_fail_skip_and_explicit_error_statuses():
    passed = CORE_INVARIANT_REGISTRY.result(
        "authority.screen_not_authority",
        passed=True,
    )
    failed = CORE_INVARIANT_REGISTRY.result(
        "authority.screen_not_authority",
        passed=False,
    )
    skipped = CORE_INVARIANT_REGISTRY.result(
        "authority.screen_not_authority",
    )
    errored = CORE_INVARIANT_REGISTRY.result(
        "authority.screen_not_authority",
        status=InvariantStatus.ERROR,
    )
    assert passed.passed
    assert failed.failed
    assert skipped.status is InvariantStatus.SKIP
    assert errored.failed


def test_error_result_records_exception_type_but_not_message():
    secret = "espn_s2=TOPSECRET"
    error = RuntimeError(secret)
    result = CORE_INVARIANT_REGISTRY.error_result(
        "data.raw_vs_derived_separation",
        error,
        safe_message="invariant evaluator failed",
    )
    text = result.to_json()
    assert result.status is InvariantStatus.ERROR
    assert result.to_dict()["details"]["error_type"] == "RuntimeError"
    assert secret not in text
    assert "TOPSECRET" not in text


def test_result_rejects_non_finite_details():
    with pytest.raises(ValueError, match="non-finite"):
        CORE_INVARIANT_REGISTRY.result(
            "physics.channel_separation",
            passed=True,
            details={"value": float("nan")},
        )


def test_invariant_contract_does_not_advance_random_state():
    random.seed(20260917)
    before = random.getstate()
    CORE_INVARIANT_REGISTRY.result(
        "randomness.crn_required_pairing",
        passed=True,
        details={"paired": True},
    )
    assert random.getstate() == before
