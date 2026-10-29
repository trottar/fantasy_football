"""Synthetic signed-ESPN-DST contract across B1 -> B2b2 -> B2b6.

No actual team, roster, trade, observed outcome, or private ID is used.
Negative player identifiers are rejected unless the frozen source position is DST.
"""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import numpy as np
import pytest

OPERATIONS = Path(__file__).resolve().parents[1] / 'tools' / 'operations'
if str(OPERATIONS) not in sys.path:
    sys.path.insert(0,str(OPERATIONS))
import action_frontier as b1
import action_portfolio_b2b2 as b2b2
import action_alt_drop_paired_b2b6 as b2b6
from action_certification import CertificationBlocked

POSITIONS=('QB','RB','WR','TE','DST','K')

def frozen():
    source={'espn':{'season':2026,'week':8,'teams':[
        {'team_id':1,'roster':[{'espn_id':101,'position':'QB','droppable':True,'lineup_locked':False},
                               {'espn_id':102,'position':'RB','droppable':True,'lineup_locked':False},
                               {'espn_id':-17,'position':'DST','droppable':True,'lineup_locked':False}]},
        {'team_id':2,'roster':[{'espn_id':-16,'position':'DST','droppable':True,'lineup_locked':False},
                               {'espn_id':201,'position':'RB','droppable':True,'lineup_locked':False},
                               {'espn_id':202,'position':'QB','droppable':True,'lineup_locked':False}]},
    ],'available_players':[{'espn_id':-18,'position':'DST','fantasy_status':'FREEAGENT'},
                           {'espn_id':203,'position':'RB','fantasy_status':'FREEAGENT'}]}}
    offer={'partner_team_id':2,'give_ids':[101],'receive_ids':[-16],
           'user_auto_drop_ids':[],'user_auto_add_ids':[],
           'partner_auto_drop_ids':[],'partner_auto_add_ids':[],
           'classification':'ACTIONABLE_OFFER'}
    receipt={'team_id':1,'season':2026,'week':8,'channels':[
        {'key':'trade_specialist_inclusive','action':{'offers':[offer]}}]}
    league={'roster':{p:0 for p in POSITIONS},'position_maximums':{p:12 for p in POSITIONS}}
    return source,{},receipt,league

def inject_cert(monkeypatch):
    monkeypatch.setattr(b1,'certify_receipt',lambda *_: {
        'trade_channel_receipts_missing':[], 'candidate_count':1,'contract':'synthetic'})

def test_signed_dst_frontier_has_exact_native_receive_identity(monkeypatch):
    inject_cert(monkeypatch)
    snap,cap,receipt,league=frozen()
    result=b1.build_frontier(snap,cap,receipt)
    assert result['offer_count']==1
    offer=result['offers'][0]
    assert offer['receive_ids']==[-16]
    assert offer['structural_options'][0]['native_selected_normalization'] is True
    assert offer['structural_options'][0]['drop_ids']==[]
    assert len(offer['offer_id'])==24
    assert result['espn_action_authority']=='NONE'

def test_signed_dst_b2b2_conditional_roster_and_branch(monkeypatch):
    inject_cert(monkeypatch)
    snap,cap,receipt,league=frozen()
    result=b2b2.audit(snap,cap,receipt,league)
    assert result['offer_count']==1
    assert result['offers'][0]['options'][0]['branches'][0]['frozen_static_constraints_pass'] is True
    assert result['espn_action_authority']=='NONE'

def test_signed_dst_b2b6_end_to_end_zero_native_mc_with_injected_response(monkeypatch):
    inject_cert(monkeypatch)
    snap,cap,receipt,league=frozen()
    orig=copy.deepcopy((snap,cap,receipt,league))
    offerid=b1.build_frontier(snap,cap,receipt)['offers'][0]['offer_id']
    calls=[]
    def kernel(_snapshot,_league,_model,_values,_offer,_option,_branch,user,scenarios,_runtime,cache):
        calls.append((user,scenarios))
        return {1:(np.zeros(scenarios), np.ones(scenarios)),
                2:(np.zeros(scenarios),np.full(scenarios,.5))}, {}
    out=b2b6.evaluate(snap,cap,receipt,league,{},Path('not_accessed.csv'),
                      Path('not_accessed_runtime'),offerid,scenarios=16,kernel=kernel)
    assert calls==[(1,16)]
    assert out['native_mc_cases_evaluated']==1
    assert out['options'][0]['hold_comparison']['user']['paired_delta_mean']==1.0
    assert out['options'][0]['hold_comparison']['partner']['paired_delta_mean']==0.5
    assert out['espn_action_authority']=='NONE'
    assert (snap,cap,receipt,league)==orig

def test_negative_dst_in_frozen_roster_allowed():
    snap,_,_,_=frozen()
    assert -16 in b2b2._owned(snap['espn']['teams'][1])
    assert -16 in b1._exact_roster(snap['espn']['teams'][1])

def test_negative_non_dst_in_frozen_roster_refused():
    snap,_,_,_=frozen()
    for invalid in ('QB','RB','WR','TE','K','UNKNOWN'):
        row=copy.deepcopy(snap['espn']['teams'][1])
        row['roster'][0]['position']=invalid
        with pytest.raises(CertificationBlocked):
            b1._exact_roster(row)
        with pytest.raises(CertificationBlocked):
            b2b2._owned(row)

def test_native_signed_int_only_and_nonzero():
    assert b1._ids_strict({'receive_ids':[-16]},'receive_ids')==(-16,)
    for invalid in (0,'-16',-16.0,None,True):
        with pytest.raises(CertificationBlocked):
            b1._ids_strict({'receive_ids':[invalid]},'receive_ids')
    with pytest.raises(CertificationBlocked):
        b1._ids_strict({'receive_ids':[-16,-16]},'receive_ids')

def test_negative_dst_conditional_freeagent_fill_allowed():
    snap,_,_,_=frozen()
    rows,blockers=b2b2._future_fill_rows(snap,[('user',-18)],set())
    assert blockers==[] and rows[-18]['position']=='DST'
    assert b2b6._signature({'fill_outcomes':[{'side':'user','id':-18,'conditional_success':True}]})==(('user',-18,True),)

def test_negative_non_dst_conditional_fill_refused():
    snap,_,_,_=frozen()
    snap['espn']['available_players'].append({'espn_id':-19,'position':'RB','fantasy_status':'FREEAGENT'})
    with pytest.raises(CertificationBlocked,match='FUTURE_NEGATIVE_ID_NOT_FROZEN_DST'):
        b2b2._future_fill_rows(snap,[('user',-19)],set())

def test_zero_bool_and_string_conditional_ids_refused():
    for invalid in (0,True,'-18',-18.0,None):
        with pytest.raises(CertificationBlocked):
            b2b6._signature({'fill_outcomes':[{'side':'user','id':invalid,'conditional_success':True}]})

def test_player_trade_positive_ids_unchanged(monkeypatch):
    inject_cert(monkeypatch)
    snap,cap,receipt,league=frozen()
    receipt['channels'][0]['action']['offers'][0]['receive_ids']=[201]
    assert b1.build_frontier(snap,cap,receipt)['offer_count']==1
