"""Synthetic fail-closed Week 8 action certification scaffold tests."""
import copy
import importlib.util
from pathlib import Path
import sys

FILE = Path(__file__).resolve().parents[1] / 'tools/operations/action_certification.py'
spec = importlib.util.spec_from_file_location('action_certification_v2', FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def inputs():
    snapshot = {
        'snapshot_utc': '2026-10-21T15:24:38+00:00',
        'espn': {
            'season': 2026, 'week': 7,
            'transaction_settings': {'trade_review_hours': 48},
            'teams': [
                {'team_id': 1, 'name': 'Us', 'roster': [
                    {'espn_id': 11, 'name': 'Lamar Jackson', 'position': 'QB', 'injury_status': 'QUESTIONABLE'},
                    {'espn_id': 12, 'name': 'Baker Mayfield', 'position': 'QB', 'injury_status': 'QUESTIONABLE'},
                    {'espn_id': 13, 'name': 'Jacoby Brissett', 'position': 'QB', 'injury_status': 'ACTIVE'},
                    {'espn_id': 14, 'name': 'Other', 'position': 'WR', 'injury_status': 'ACTIVE'},
                ]},
                {'team_id': 2, 'name': 'Other Team', 'roster': [
                    {'espn_id': 100, 'name': 'CeeDee Lamb', 'position': 'WR'},
                    {'espn_id': 101, 'name': 'Ravens D/ST', 'position': 'DST'},
                ]},
            ],
        },
    }
    capture = {
        'snapshot_utc': snapshot['snapshot_utc'], 'week': 7, 'season': 2026,
        'behavioral_observation_state': {'snapshot_sha256': mod.canonical_sha256(snapshot)},
    }
    capture['integrity'] = {'canonical_payload_sha256': mod.canonical_sha256(capture)}
    action = {'classification': 'ACTIONABLE_OFFER', 'give_names': ['Lamar Jackson'],
              'receive_names': ['CeeDee Lamb', 'Ravens D/ST'], 'give_ids': [11],
              'receive_positions': ['WR', 'DST'], 'user_auto_drop_ids': [13],
              'user_auto_add_ids': [], 'partner_auto_add_ids': [1001],
             }
    receipt = {'season': 2026, 'week': 7, 'team_id': 1,
               'overall_state': 'COMPLETE / ACTION_REQUIRED',
               'provenance': {'snapshot_utc': snapshot['snapshot_utc'], 'capture_integrity_ok': True},
               'channels': [
                   {'key': 'trade_one_for_one_player', 'status': 'PASS / HOLD:ONE_FOR_ONE_PLAYER_TRADE'},
                   {'key': 'trade_multi_player_unequal', 'status': 'PASS / HOLD:MULTI_ASSET_PLAYER_TRADE'},
                   {'key': 'trade_specialist_inclusive', 'status': 'PASS / ACTION', 'action': {'offers': [action]}},
               ]}
    return snapshot, capture, receipt


def test_lamar_trade_exposes_forced_drop_and_qb_singleton():
    report = mod.certify_receipt(*inputs())
    assert report['candidate_count'] == 1
    offer = report['candidates'][0]
    assert offer['mandatory_user_drops'] == ['Jacoby Brissett']
    assert offer['remaining_qbs'] == ['Baker Mayfield']
    assert offer['post_trade_qbs_count_if_native_drops_executed'] == 1
    assert 'POST_TRADE_QB_SINGLETON_CONTINGENCY_UNEVALUATED' in offer['blockers']
    assert 'POST_TRADE_QB_AVAILABILITY_UNCERTAINTY_NOT_PROPAGATED' in offer['blockers']
    assert offer['modeled_earliest_effective_week'] == 8
    assert report['certified_action_count'] == 0
    assert report['espn_action_authority'] == 'NONE'


def test_future_partner_fill_is_not_guaranteed():
    report = mod.certify_receipt(*inputs())
    assert report['candidates'][0]['required_partner_auto_adds_total'] == 1
    assert 'CURRENT_FREEAGENT_IS_NOT_GUARANTEED_AT_FUTURE_TRADE_EFFECTIVE_DATE' in report['candidates'][0]['blockers']


def test_changed_capture_binding_rejected():
    s,c,r = inputs()
    s['espn']['teams'][0]['roster'][0]['injury_status']='ACTIVE'
    import pytest
    with pytest.raises(mod.CertificationBlocked, match='CAPTURE_SNAPSHOT_BINDING_INVALID'):
        mod.certify_receipt(s,c,r)


def test_changed_capture_hash_rejected():
    s,c,r = inputs()
    c['week']=8
    import pytest
    with pytest.raises(mod.CertificationBlocked, match='PROSPECTIVE_CAPTURE_INTEGRITY_INVALID'):
        mod.certify_receipt(s,c,r)


def test_receipt_provenance_mismatch_rejected():
    s,c,r = inputs()
    r['provenance']['snapshot_utc']='stale'
    import pytest
    with pytest.raises(mod.CertificationBlocked, match='SNAPSHOT_CAPTURE_MC_PROVENANCE_MISMATCH'):
        mod.certify_receipt(s,c,r)


def test_no_trade_channels_fails_closed_and_names_missing():
    s,c,r = inputs()
    r['channels']=[]
    report=mod.certify_receipt(s,c,r)
    assert report['trade_channel_receipts_missing'] == list(mod.TRADE_CHANNELS)
    assert report['candidate_count']==0
    assert report['final_state'].startswith('BLOCKED_')


def test_zero_review_not_claimed_week8():
    s,c,r = inputs()
    s['espn']['transaction_settings']['trade_review_hours']=0
    c['behavioral_observation_state']['snapshot_sha256']=mod.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=mod.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})
    report=mod.certify_receipt(s,c,r)
    assert report['candidates'][0]['modeled_earliest_effective_week'] is None


def test_even_no_implicit_drop_never_auto_approves():
    s,c,r = inputs()
    offer=r['channels'][2]['action']['offers'][0]
    offer['user_auto_drop_ids']=[]
    offer['partner_auto_add_ids']=[]
    report=mod.certify_receipt(s,c,r)
    assert report['certified_action_count']==0
    assert report['candidates'][0]['final_decision']=='BLOCKED'


def test_invalid_offer_shape_rejected():
    s,c,r = inputs()
    r['channels'][2]['action']['offers']='invalid'
    import pytest
    with pytest.raises(mod.CertificationBlocked, match='NATIVE_TRADE_OFFERS_NOT_LIST'):
        mod.certify_receipt(s,c,r)


def test_unknown_drop_is_explicit_blocker():
    s,c,r=inputs()
    r['channels'][2]['action']['offers'][0]['user_auto_drop_ids']=[9999]
    report=mod.certify_receipt(s,c,r)
    assert 'AUTO_DROP_ID_NOT_ON_FROZEN_OWNED_ROSTER' in report['candidates'][0]['blockers']


def test_source_text_has_no_network_or_transaction_post():
    raw=FILE.read_text('utf-8')
    for bad in ('requests.post(', 'urlopen(', 'subprocess.run(', 'create_trade(', 'os.system('):
        assert bad not in raw
