"""Synthetic frozen position-repair frontier (no private rosters or MC)."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import pytest

OPS = Path(__file__).resolve().parents[1] / 'tools' / 'operations'
if OPS.is_dir() and str(OPS) not in sys.path:
    sys.path.insert(0, str(OPS))
import action_frontier as b1
import action_portfolio_b2b2 as b2b2
import action_alt_drop_paired_b2b6 as b2b6
from action_certification import CertificationBlocked


def _player(pid, pos, *, droppable=True, locked=False, status=None):
    row={'espn_id':pid,'position':pos,'droppable':droppable,'lineup_locked':locked}
    if status is not None: row['fantasy_status']=status
    return row


def frozen():
    # Equal-count specialist trade gives away K, leaving a K deficiency;
    # the native evaluator drops an unlocked QB and conditionally adds a K.
    user=[_player(101,'QB'),_player(102,'K'),_player(103,'RB'),_player(-17,'DST')]
    partner=[_player(201,'RB'),_player(202,'QB'),_player(203,'K'),_player(-16,'DST')]
    espn={'season':2026,'week':8,'teams':[{'team_id':1,'roster':user},
                 {'team_id':2,'roster':partner}],
          'available_players':[_player(301,'K',status='FREEAGENT'),
                               _player(302,'RB',status='FREEAGENT')]}
    offer={'partner_team_id':2,'give_ids':[102],'receive_ids':[201],
           'user_auto_drop_ids':[101],'user_auto_add_ids':[301],
           'partner_auto_drop_ids':[],'partner_auto_add_ids':[],
           'classification':'ACTIONABLE_OFFER'}
    receipt={'team_id':1,'season':2026,'week':8,'channels':[
        {'key':'trade_specialist_inclusive','action':{'offers':[offer]}}]}
    league={'roster':{'QB':0,'RB':0,'WR':0,'TE':0,'K':1,'DST':1},
            'position_maximums':{'QB':4,'RB':5,'WR':5,'TE':4,'K':2,'DST':2}}
    return {'espn':espn},{},receipt,league


def _inject(monkeypatch):
    monkeypatch.setattr(b1,'certify_receipt',lambda *_: {
        'trade_channel_receipts_missing':[], 'candidate_count':1,'contract':'synthetic'})


def test_equal_count_specialist_repair_has_exact_native_reference(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,league=frozen()
    before=copy.deepcopy((snap,cap,receipt,league))
    f=b1.build_frontier(snap,cap,receipt)
    assert f['offer_count']==1 and f['espn_action_authority']=='NONE'
    row=f['offers'][0]
    assert row['required_user_drops_by_count']==0
    assert row['required_user_fills_by_count']==0
    assert row['modeled_native_auto_drop_ids']==[101]
    assert row['modeled_native_auto_add_ids']==[301]
    assert row['structural_options_truncated'] is False
    assert 'NATIVE_POSITION_REBALANCE_CONDITIONAL_FROZEN_FILL' in row['blocking_evidence']
    opts=row['structural_options']
    assert len(opts)>=2 and len(opts)<=24
    assert sum(x['native_selected_normalization'] is True for x in opts)==1
    assert next(x for x in opts if x['native_selected_normalization'])['drop_ids']==[101]
    assert all(len(x['drop_ids'])==1 for x in opts)
    assert (snap,cap,receipt,league)==before


def test_frozen_position_branch_illegal_no_fill_and_legal_with_k_fill(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,league=frozen()
    report=b2b2.audit(snap,cap,receipt,league)
    assert report['offer_count']==1
    native=next(x for x in report['offers'][0]['options'] if x['native_selected'])
    assert native['drop_ids']==[101] and len(native['branches'])==2
    nofill=next(x for x in native['branches'] if not x['fill_outcomes'][0]['conditional_success'])
    fill=next(x for x in native['branches'] if x['fill_outcomes'][0]['conditional_success'])
    assert nofill['user']['frozen_static_constraints_pass'] is False
    assert nofill['user']['minimum_deficits'].get('K')==1
    assert fill['user']['frozen_static_constraints_pass'] is True
    assert fill['frozen_static_constraints_pass'] is False or any(
        'FUTURE_FILL_AT_PROCESSING_UNVERIFIED' in x for x in fill['unresolved'])
    assert report['espn_action_authority']=='NONE'


def test_alternatives_rejoin_identical_fill_state(monkeypatch):
    _inject(monkeypatch)
    from action_fill_predictive_b2b3 import select_branch_frontier
    snap,cap,receipt,league=frozen()
    offer=b1.build_frontier(snap,cap,receipt)['offers'][0]
    states=[]
    for opt in offer['structural_options']:
        selected=select_branch_frontier(snap,cap,receipt,league,offer['offer_id'],opt['drop_ids'])
        assert selected[0]['offer_id']==selected[1]['offer_id']==offer['offer_id']
        assert selected[2]['drop_ids']==opt['drop_ids']
        states.append(tuple(tuple((x['side'],x['id'],x['conditional_success']) for x in b['fill_outcomes'])
                            for b in selected[2]['branches']))
    assert len(set(states))==1


def test_unverified_future_k_fill_does_not_invent_native_option(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,_=frozen()
    snap['espn']['available_players'][0]['fantasy_status']='WAIVERS'
    row=b1.build_frontier(snap,cap,receipt)['offers'][0]
    assert not any(x['native_selected_normalization'] for x in row['structural_options'])
    assert 'NATIVE_NORMALIZATION_COUNT_INCONSISTENT_WITH_FROZEN_ROSTER' in row['blocking_evidence']


def test_non_specialist_equal_count_extra_drop_not_promoted(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,_=frozen()
    receipt['channels'][0]['key']='trade_multi_player_unequal'
    row=b1.build_frontier(snap,cap,receipt)['offers'][0]
    assert not any(x['native_selected_normalization'] for x in row['structural_options'])


def test_no_specialist_deficit_does_not_promote_extra_drop(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,_=frozen()
    receipt['channels'][0]['action']['offers'][0]['give_ids']=[103]
    row=b1.build_frontier(snap,cap,receipt)['offers'][0]
    assert not any(x['native_selected_normalization'] for x in row['structural_options'])


def test_no_native_drop_or_fill_normalization_regression(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,_=frozen()
    raw=receipt['channels'][0]['action']['offers'][0]
    raw['give_ids']=[103];raw['user_auto_drop_ids']=[];raw['user_auto_add_ids']=[]
    row=b1.build_frontier(snap,cap,receipt)['offers'][0]
    assert len(row['structural_options'])==1
    assert row['structural_options'][0]['drop_ids']==[]
    assert row['structural_options'][0]['native_selected_normalization'] is True
    assert 'NATIVE_POSITION_REBALANCE_CONDITIONAL_FROZEN_FILL' not in row['blocking_evidence']


def test_native_drop_locked_retained_as_reference_but_blocked(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,league=frozen()
    snap['espn']['teams'][0]['roster'][0]['lineup_locked']=True
    row=b1.build_frontier(snap,cap,receipt)['offers'][0]
    native=next(x for x in row['structural_options'] if x['native_selected_normalization'])
    assert 'FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED' in native['feasibility_evidence']


def test_truncated_alternates_fail_closed_not_silently_selected(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,_=frozen()
    limited=b1.build_frontier(snap,cap,receipt,limit=1)['offers'][0]
    assert limited['structural_options_truncated'] is True
    assert 'STRUCTURAL_ALTERNATIVES_TRUNCATED' in limited['blocking_evidence']


def test_malformed_signed_specialist_roster_identity_rejected(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,_=frozen()
    snap['espn']['teams'][0]['roster'][3]['position']='QB'
    with pytest.raises(CertificationBlocked,match='ROSTER_ASSET_ID_SIGN_OR_POSITION_INVALID'):
        b1.build_frontier(snap,cap,receipt)


def test_position_repair_never_promotes_future_k_fill_to_mc_authority(monkeypatch):
    _inject(monkeypatch)
    snap,cap,receipt,league=frozen()
    offer=b1.build_frontier(snap,cap,receipt)['offers'][0]
    calls=[]
    def forbidden_native(*args):
        calls.append(True)
        raise AssertionError('conditional future fill may not become guaranteed')
    result=b2b6.evaluate(snap,cap,receipt,league,{},Path('none.csv'),Path('none'),
                        offer['offer_id'],scenarios=16,kernel=forbidden_native)
    assert calls==[] and result['native_mc_cases_evaluated']==0
    assert result['certified_actions']==0 and result['espn_action_authority']=='NONE'
    assert any('FUTURE_USER_FILL_REQUIRED_NO_GUARANTEE' in row['blockers']
               for row in result['options'])
