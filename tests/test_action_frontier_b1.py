"""Slice B1: exact native-search schema and frozen-state perturbation tests."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

import pytest
from test_action_certification_v2 import inputs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/operations'))
FILE = ROOT / 'tools/operations/action_frontier.py'
spec = importlib.util.spec_from_file_location('action_frontier_b1', FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def setup():
    s, c, r = inputs()
    our = s['espn']['teams'][0]['roster']
    for p in our:
        p['droppable'] = True
        p['lineup_locked'] = False
    trade = r['channels'][2]['action']['offers'][0]
    trade.update({'partner_team_id': 2, 'receive_ids': [100, 101],
                  'user_auto_add_ids': [], 'partner_auto_drop_ids': [],
                  'partner_auto_add_ids': [1001], 'give_ids': [11],
                  'user_auto_drop_ids': [13]})
    # Frozen binding changes when we add legitimate ESPN normalized fields.
    c['behavioral_observation_state']['snapshot_sha256'] = m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256'] = m.canonical_sha256({k: v for k, v in c.items() if k != 'integrity'})
    return s,c,r


def test_native_lamar_frontier_contains_brissett_and_alternatives():
    s,c,r=setup()
    x=m.build_frontier(s,c,r)
    assert x['offer_count']==1
    offer=x['offers'][0]
    assert offer['give']==['Lamar Jackson']
    assert offer['receive']==['CeeDee Lamb','Ravens D/ST']
    assert offer['required_user_drops_by_count']==1
    assert offer['modeled_native_auto_drop_ids']==[13]
    drops={tuple(row['drop_ids']):row for row in offer['structural_options']}
    assert set(drops)=={(12,),(13,),(14,)}
    assert drops[(13,)]['native_selected_normalization']
    assert drops[(13,)]['post_trade_static_state']['channels']['P']['QB']==1
    assert drops[(13,)]['post_trade_static_state']['unresolved_qb_availability']==['Baker Mayfield']
    assert drops[(12,)]['post_trade_static_state']['qb_names']==['Jacoby Brissett']
    assert drops[(14,)]['post_trade_static_state']['channels']['P']['QB']==2
    assert drops[(14,)]['post_trade_static_state']['channels']['D']['DST']==1
    assert x['eligible_for_approval_count']==0
    assert x['espn_action_authority']=='NONE'


def test_native_choice_not_proven_droppable_or_unlocked():
    s,c,r=setup()
    our=s['espn']['teams'][0]['roster']
    our[2]['droppable']=False
    our[2]['lineup_locked']=True
    c['behavioral_observation_state']['snapshot_sha256']=m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=m.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})
    options=m.build_frontier(s,c,r)['offers'][0]['structural_options']
    native=next(x for x in options if x['native_selected_normalization'])
    assert 'FROZEN_ESPN_DROPPABLE_NOT_TRUE' in native['feasibility_evidence']
    assert 'FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED' in native['feasibility_evidence']
    assert not any(row['drop_ids']==[13] for row in options if not row['native_selected_normalization'])


def test_future_fill_is_not_assumed_to_be_owned():
    s,c,r=setup()
    a=r['channels'][2]['action']['offers'][0]
    a.update({'give_ids':[11,13],'give_names':['Lamar Jackson','Jacoby Brissett'],
              'receive_ids':[100],'receive_names':['CeeDee Lamb'],'receive_positions':['WR'],
              'user_auto_drop_ids':[], 'user_auto_add_ids':[900], 'partner_auto_add_ids':[]})
    x=m.build_frontier(s,c,r)['offers'][0]
    assert x['required_user_drops_by_count']==0
    assert x['required_user_fills_by_count']==1
    assert 'FUTURE_FREEAGENT_FILL_UNPROVEN' in x['blocking_evidence']
    assert x['structural_options'][0]['post_trade_static_state']['total']==3
    assert x['structural_options'][0]['valuation_state']=='PAIRED_MC_NOT_RUN'


def test_future_fill_native_count_mismatch_blocks_output():
    s,c,r=setup()
    r['channels'][2]['action']['offers'][0]['user_auto_add_ids']=[900]
    x=m.build_frontier(s,c,r)['offers'][0]
    assert 'NATIVE_NORMALIZATION_COUNT_INCONSISTENT_WITH_FROZEN_ROSTER' in x['blocking_evidence']


def test_missing_partner_asset_refuses_structural_claim():
    s,c,r=setup()
    r['channels'][2]['action']['offers'][0]['receive_ids']=[888]
    with pytest.raises(m.CertificationBlocked,match='FROZEN_RECEIVE_NOT_PARTNER_OWNED'):
        m.build_frontier(s,c,r)


def test_duplicate_user_roster_refs_refused():
    s,c,r=setup()
    s['espn']['teams'][0]['roster'].append(copy.deepcopy(s['espn']['teams'][0]['roster'][0]))
    c['behavioral_observation_state']['snapshot_sha256']=m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=m.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})
    with pytest.raises(m.CertificationBlocked,match='DUPLICATE_OR_UNIDENTIFIED_ROSTER_ASSETS'):
        m.build_frontier(s,c,r)


def test_missing_trade_channel_refused():
    s,c,r=setup(); r['channels']=r['channels'][1:]
    with pytest.raises(m.CertificationBlocked,match='REQUIRED_TRADE_CHANNEL_RECEIPT_MISSING'):
        m.build_frontier(s,c,r)


def test_invalid_offer_fields_refused_not_silently_empty():
    s,c,r=setup(); r['channels'][2]['action']['offers'][0].pop('receive_ids')
    with pytest.raises(m.CertificationBlocked,match='NATIVE_OFFER_IDS_NOT_LIST:receive_ids'):
        m.build_frontier(s,c,r)


def test_duplicate_offer_id_refused():
    s,c,r=setup(); a=r['channels'][2]['action']['offers'][0]
    r['channels'][2]['action']['offers'].append(copy.deepcopy(a))
    with pytest.raises(m.CertificationBlocked,match='DUPLICATE_NATIVE_OFFER_ID'):
        m.build_frontier(s,c,r)


def test_overlapping_and_partner_only_couplings_distinguished():
    s,c,r=setup()
    # Different receive target, same partner and same Lamar giving asset.
    a=copy.deepcopy(r['channels'][2]['action']['offers'][0])
    a['receive_ids']=[100]
    a['receive_names']=['CeeDee Lamb']
    a['receive_positions']=['WR']
    a['user_auto_drop_ids']=[]
    r['channels'][2]['action']['offers'].append(a)
    x=m.build_frontier(s,c,r)
    assert len(x['couplings'])==1
    pair=x['couplings'][0]
    assert pair['shared_given_ids']==[11]
    assert pair['same_partner'] is True
    assert pair['direct_asset_conflict'] is True
    assert pair['combined_strategy_evaluated'] is False


def test_same_partner_distinct_assets_is_coupled_not_direct_conflict():
    s,c,r=setup()
    first=r['channels'][2]['action']['offers'][0]
    first.update({'receive_ids':[101], 'receive_names':['Ravens D/ST'], 'receive_positions':['DST'],
                  'user_auto_drop_ids':[]})
    a=copy.deepcopy(r['channels'][2]['action']['offers'][0])
    a.update({'give_ids':[14], 'give_names':['Other'], 'receive_ids':[100],
              'receive_names':['CeeDee Lamb'], 'receive_positions':['WR'],
              'user_auto_drop_ids':[]})
    r['channels'][2]['action']['offers'].append(a)
    pair=m.build_frontier(s,c,r)['couplings'][0]
    assert pair['same_partner'] is True
    assert pair['direct_asset_conflict'] is False


def test_alternative_frontier_truncates_explicitly_and_keeps_native():
    s,c,r=setup()
    x=m.build_frontier(s,c,r,limit=1)['offers'][0]
    assert x['structural_options_truncated']
    assert 'STRUCTURAL_ALTERNATIVES_TRUNCATED' in x['blocking_evidence']
    assert any(v['native_selected_normalization'] for v in x['structural_options'])


def test_causally_changed_capture_fails_before_frontier():
    s,c,r=setup()
    s['espn']['teams'][0]['roster'][0]['injury_status']='OUT'
    with pytest.raises(m.CertificationBlocked,match='CAPTURE_SNAPSHOT_BINDING_INVALID'):
        m.build_frontier(s,c,r)


def test_tool_never_invokes_mc_or_espn():
    txt=FILE.read_text('utf-8')
    for disallowed in ('requests.get(', 'requests.post(', 'subprocess.run(', 'evaluate_specialist_trade(', 'evaluate_trade('):
        assert disallowed not in txt
