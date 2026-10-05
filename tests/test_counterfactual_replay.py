from __future__ import annotations

from dataclasses import FrozenInstanceError
import json

import pytest

from src.counterfactual_replay import (
    CAUSAL_FROZEN_REPLAY,
    PROVENANCE_FROZEN,
    PROVENANCE_RECONSTRUCTED,
    RECONSTRUCTED_RETROSPECTIVE_REPLAY,
    DependencyProvenance,
    OutcomeAccessError,
    ReplayContractError,
    ReplayOutcomeFirewall,
    classify_replay_mode,
    freeze_phase_a_receipt,
    load_phase_a_receipt,
    save_phase_a_receipt,
)


FROZEN_UTC = "2026-10-05T18:00:00+00:00"


def _dep(key: str, channel: str, status: str) -> DependencyProvenance:
    return DependencyProvenance(
        key=key,
        channel=channel,
        status=status,
        artifact=f"frozen/{key}.json",
        sha256="a" * 64,
        captured_utc="2026-09-24T15:51:01+00:00",
    )


def _week3_dependencies():
    return [
        _dep("rostered_player_predictions", "player_roster_trade", PROVENANCE_FROZEN),
        _dep("specialist_actionable_frontier", "specialist", PROVENANCE_FROZEN),
        _dep(
            "player_values_for_available_market",
            "player_waiver_free_agent",
            PROVENANCE_RECONSTRUCTED,
        ),
    ]


def _receipt():
    return freeze_phase_a_receipt(
        frozen_utc=FROZEN_UTC,
        season=2026,
        week=3,
        dependencies=_week3_dependencies(),
        engine_identities={
            "replay_engine": "counterfactual_replay.py:test",
            "source_checkpoint": "f9023a9d165d1079a91d0dbcf060ee1709b1a16b",
        },
        candidates=[
            {
                "candidate_id": "hold",
                "action_family": "lineup",
                "rank": 1,
                "prediction": {"delta_utility": 0.0, "current_week_points": 100.0},
                "uncertainty": {"p_better": 0.5},
            },
            {
                "candidate_id": "swap-1",
                "action_family": "lineup",
                "rank": 2,
                "prediction": {"delta_utility": -0.01, "current_week_points": 99.0},
                "uncertainty": {"p_better": 0.4},
            },
        ],
        model_action={"decision": "HOLD", "candidate_id": "hold"},
        metadata={"outcome_firewall": "CLOSED", "oracle_available": False},
    )


def test_week3_mixed_provenance_is_reconstructed_retrospective():
    result = classify_replay_mode(_week3_dependencies())
    assert result.replay_mode == RECONSTRUCTED_RETROSPECTIVE_REPLAY
    assert result.reconstructed == (
        "player_waiver_free_agent:player_values_for_available_market",
    )
    assert result.missing == ()


def test_all_material_dependencies_frozen_is_causal():
    result = classify_replay_mode(
        [
            _dep("roster", "player", PROVENANCE_FROZEN),
            _dep("specialists", "specialist", PROVENANCE_FROZEN),
        ]
    )
    assert result.replay_mode == CAUSAL_FROZEN_REPLAY
    assert result.reconstructed == ()
    assert result.missing == ()


@pytest.mark.parametrize(
    "field",
    ["observed_points", "actual_score", "realized_points", "outcomes", "oracle_score"],
)
def test_phase_a_rejects_observed_outcome_fields(field):
    with pytest.raises(ReplayContractError, match="forbidden in Phase A"):
        freeze_phase_a_receipt(
            frozen_utc=FROZEN_UTC,
            season=2026,
            week=3,
            dependencies=_week3_dependencies(),
            engine_identities={"engine": "test"},
            candidates=[
                {
                    "candidate_id": "x",
                    "action_family": "lineup",
                    "rank": 1,
                    "prediction": {"nested": {field: 123}},
                    "uncertainty": {},
                }
            ],
            model_action={"candidate_id": "x"},
        )


def test_phase_a_receipt_is_hash_addressed_and_deeply_immutable():
    receipt = _receipt()
    receipt.verify()
    assert len(receipt.receipt_sha256) == 64
    assert receipt.replay_mode == RECONSTRUCTED_RETROSPECTIVE_REPLAY

    with pytest.raises(TypeError):
        receipt.metadata["x"] = 1
    with pytest.raises(TypeError):
        receipt.candidates[0].prediction["delta_utility"] = 999
    with pytest.raises(FrozenInstanceError):
        receipt.week = 4


def test_phase_a_ranking_and_model_action_are_frozen():
    receipt = _receipt()
    assert [row.rank for row in receipt.candidates] == [1, 2]
    assert [row.candidate_id for row in receipt.candidates] == ["hold", "swap-1"]
    assert receipt.model_action["candidate_id"] == "hold"

    with pytest.raises(ReplayContractError, match="contiguous"):
        freeze_phase_a_receipt(
            frozen_utc=FROZEN_UTC,
            season=2026,
            week=3,
            dependencies=_week3_dependencies(),
            engine_identities={"engine": "test"},
            candidates=[
                {
                    "candidate_id": "x",
                    "action_family": "lineup",
                    "rank": 2,
                    "prediction": {},
                    "uncertainty": {},
                }
            ],
            model_action={"candidate_id": "x"},
        )


def test_phase_a_receipt_save_is_no_overwrite_and_round_trips(tmp_path):
    receipt = _receipt()
    path = tmp_path / "phase_a.json"
    save_phase_a_receipt(receipt, path)
    loaded = load_phase_a_receipt(path)
    assert loaded.to_dict() == receipt.to_dict()

    with pytest.raises(FileExistsError):
        save_phase_a_receipt(receipt, path)


def test_tampered_phase_a_receipt_is_rejected(tmp_path):
    receipt = _receipt()
    path = tmp_path / "phase_a.json"
    save_phase_a_receipt(receipt, path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["candidates"][0]["prediction"]["delta_utility"] = 999.0
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ReplayContractError, match="hash mismatch"):
        load_phase_a_receipt(path)


def test_outcome_firewall_blocks_access_and_attachment_before_phase_a_freeze():
    firewall = ReplayOutcomeFirewall()
    assert not firewall.phase_a_frozen
    assert not firewall.phase_b_attached

    with pytest.raises(OutcomeAccessError, match="unavailable"):
        _ = firewall.observed_outcomes

    with pytest.raises(OutcomeAccessError, match="before Phase A"):
        firewall.attach_phase_b(
            attached_utc="2026-10-05T19:00:00+00:00",
            outcomes={"matchup": {"score": 123.0}},
            source_identities={"outcomes": "source"},
        )


def test_outcomes_attach_only_after_verified_phase_a_and_link_by_receipt_hash():
    receipt = _receipt()
    firewall = ReplayOutcomeFirewall()
    firewall.freeze_phase_a(receipt)
    assert firewall.phase_a_frozen

    phase_b = firewall.attach_phase_b(
        attached_utc="2026-10-05T19:00:00+00:00",
        outcomes={"matchup": {"score": 123.0}},
        source_identities={"outcomes": "immutable-outcome-artifact"},
    )

    assert phase_b.phase_a_receipt_sha256 == receipt.receipt_sha256
    assert firewall.observed_outcomes["matchup"]["score"] == 123.0
    with pytest.raises(TypeError):
        firewall.observed_outcomes["matchup"]["score"] = 0.0
    with pytest.raises(ReplayContractError, match="already attached"):
        firewall.attach_phase_b(
            attached_utc="2026-10-05T20:00:00+00:00",
            outcomes={},
            source_identities={},
        )


def test_phase_a_cannot_be_frozen_twice():
    firewall = ReplayOutcomeFirewall()
    firewall.freeze_phase_a(_receipt())
    with pytest.raises(ReplayContractError, match="already frozen"):
        firewall.freeze_phase_a(_receipt())
