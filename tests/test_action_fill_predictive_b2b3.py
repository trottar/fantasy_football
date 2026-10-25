"""B2b3 conditional fill MC: isolated deterministic safety boundaries."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys
import types

import numpy as np
import pytest

FILE = Path(__file__).resolve().parents[1] / 'tools/operations/action_fill_predictive_b2b3.py'


def prepare(monkeypatch, *, unsafe=False, both_legal=True, nofill_legal=True):
    offer = {'offer_id': 'fixed-id', 'partner_team_id': 2, 'give_ids': [11],
             'receive_ids': [101], 'modeled_partner_auto_drop_ids': [],
             'structural_options': [{'drop_ids': [13],
                                     'feasibility_evidence':
                                       ['FROZEN_ESPN_DROPPABLE_NOT_TRUE'] if unsafe else [],
                                     'native_selected_normalization':True}]}
    def state(legal):
        return {'frozen_static_constraints_pass': legal}
    branches=[]
    for assumed in (False,True):
        branches.append({'fill_outcomes':[{'side':'user','id':201,
                                         'conditional_success':assumed,
                                         'materialized_from_frozen_market':assumed}],
                         'unresolved':['FUTURE_FILL_AT_PROCESSING_UNVERIFIED:user'] if assumed else [],
                         'user':state(both_legal if assumed else nofill_legal),
                         'partner':state(True),
                         'frozen_static_constraints_pass':not assumed and nofill_legal})
    structure={'offer_id':'fixed-id','options':[{'drop_ids':[13],
                                                'branches':branches}]}
    deps={
        'action_portfolio_b2b2':{'audit':lambda *args:{'offers':[structure]},
                                'MAX_FILLS_PER_OFFER':4},
        'action_partner_b2b':{'partner_drop_proof':lambda *args:[]},
        'action_predictive_b2':{
             'CertificationBlocked':ValueError,'MAX_SCENARIOS':512,
             'canonical_sha256':lambda x: __import__('hashlib').sha256(repr(x).encode()).hexdigest(),
             'paired_summary':paired_summary,
             'require':require,'verify_runtime':lambda r:None},
        'action_frontier':{'build_frontier':lambda *args:{'offers':[offer]}}}
    for name,attrs in deps.items():
        m=types.ModuleType(name)
        m.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules,name,m)
    spec=importlib.util.spec_from_file_location('test_b2b3_target',FILE)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    snapshot={'espn':{'week':7,'season':2026,
      'transaction_settings':{'trade_review_hours':48},
      'teams':[{'team_id':1,'roster':[{'espn_id':11,'position':'QB'},{'espn_id':13,'position':'QB'}]},
               {'team_id':2,'roster':[{'espn_id':101,'position':'WR'}]}],
      'available_players':[{'espn_id':201,'position':'TE','fantasy_status':'FREEAGENT'}]}}
    return mod, (snapshot,{'capture':'immutable'},{'team_id':1},{'roster':{}},{'model':'frozen'})


def require(ok,why):
    if not ok:raise ValueError(why)


def paired_summary(a,b):
    x=np.asarray(b,dtype=float)-np.asarray(a,dtype=float)
    if x.shape!=(16,) or not np.isfinite(x).all(): raise ValueError('BAD_ARRAYS')
    return {'mc_scenarios':len(x),'paired_delta_mean':float(x.mean())}


def call(mod,docs,kernel,**kw):
    return mod.evaluate(*docs,Path('/does/not/read'),Path('/fake/runtime'),
                        'fixed-id',[13],scenarios=16,kernel=kernel,**kw)


def safe_kernel(*args):
    cache=args[-1]
    n=16
    return {1:(np.zeros(n),np.ones(n)),2:(np.zeros(n),np.ones(n)*2)}, (cache or {'frozen':1})


def test_conditional_success_valued_without_claiming_its_probability(monkeypatch):
    mod,docs=prepare(monkeypatch)
    observed=[]
    def kernel(*args):
        observed.append((args[6]['fill_outcomes'][0]['conditional_success'],args[-1]))
        return safe_kernel(*args)
    original=copy.deepcopy(docs)
    result=call(mod,docs,kernel)
    assert len(result['branches'])==2
    assert result['branches_evaluated']==2
    assert observed[0][1] is None and observed[1][1]=={'frozen':1}
    assert result['branches'][1]['conditional_assumptions_not_proven']==[
        'FUTURE_FILL_AT_PROCESSING_UNVERIFIED:user']
    assert result['branches'][1]['state']=='CONDITIONAL_MC_NOT_TRANSACTION_CERTIFIED'
    assert result['branches'][1]['versus_no_fill_conditional']['user']['paired_delta_mean']==0
    assert result['certified_actions']==0
    assert result['future_fill_success_probabilities']=='UNKNOWN'
    assert result['espn_action_authority']=='NONE'
    assert docs==original


def test_no_fill_illegal_does_not_block_legal_conditional_success(monkeypatch):
    mod,docs=prepare(monkeypatch,nofill_legal=False)
    result=call(mod,docs,safe_kernel)
    assert result['branches_evaluated']==1
    assert result['no_fill_reference_evaluated'] is False
    assert result['branches'][0]['state']=='BLOCKED'
    assert result['branches'][1]['state'].startswith('CONDITIONAL_MC_')
    assert 'versus_no_fill_conditional' not in result['branches'][1]


def test_unproven_drop_permission_blocks_all_branches(monkeypatch):
    mod,docs=prepare(monkeypatch,unsafe=True)
    def forbidden(*args):raise AssertionError('MC SHOULD NOT RUN')
    result=call(mod,docs,forbidden)
    assert result['branches_evaluated']==0
    assert all('FROZEN_ESPN_DROPPABLE_NOT_TRUE' in b['blockers'] for b in result['branches'])


def test_illegal_fill_branch_stays_blocked(monkeypatch):
    mod,docs=prepare(monkeypatch,both_legal=False)
    result=call(mod,docs,safe_kernel)
    assert result['branches_evaluated']==1
    assert result['branches'][1]['state']=='BLOCKED'


def test_frozen_snapshot_mutation_blocks_even_with_kernel_success(monkeypatch):
    mod,docs=prepare(monkeypatch)
    def mutate(*args):
        args[0]['espn']['week']=8
        return safe_kernel(*args)
    with pytest.raises(ValueError,match='B2B3_FROZEN_INPUT_OR_CONFIG_MUTATED'):
        call(mod,docs,mutate)


def test_malformed_two_manager_response_fails_closed(monkeypatch):
    mod,docs=prepare(monkeypatch)
    def malformed(*args):return {1:(np.zeros(16),np.ones(16))},None
    result=call(mod,docs,malformed)
    assert result['branches_evaluated']==0
    assert result['certified_actions']==0


def test_scenario_budget_and_selected_drop_exactness(monkeypatch):
    mod,docs=prepare(monkeypatch)
    with pytest.raises(ValueError,match='SCENARIO_BUDGET_INVALID'):
        mod.evaluate(*docs,Path('x'),Path('y'),'fixed-id',[13],scenarios=10,kernel=safe_kernel)
    with pytest.raises(ValueError,match='DROP_OPTION_NOT_UNIQUE_OR_MISSING'):
        mod.evaluate(*docs,Path('x'),Path('y'),'fixed-id',[99],scenarios=16,kernel=safe_kernel)


def test_frozen_market_waiver_or_missing_cannot_materialize(monkeypatch):
    mod,docs=prepare(monkeypatch)
    branch={'fill_outcomes':[{'side':'user','id':201,'conditional_success':True,
                             'materialized_from_frozen_market':True}]}
    snap=docs[0]
    assert mod._frozen_fill_rows(snap,{},branch)[201]['fantasy_status']=='FREEAGENT'
    snap['espn']['available_players'][0]['fantasy_status']='WAIVERS'
    with pytest.raises(ValueError,match='UNPROVEN_CONDITIONAL_FREEAGENT_FILL'):
        mod._frozen_fill_rows(snap,{},branch)
    snap['espn']['available_players']=[]
    with pytest.raises(ValueError,match='UNPROVEN_CONDITIONAL_FREEAGENT_FILL'):
        mod._frozen_fill_rows(snap,{},branch)


def test_native_pair_temporal_splice_both_managers_and_no_frozen_mutation(monkeypatch):
    mod,docs=prepare(monkeypatch)
    snapshot=docs[0]
    before=copy.deepcopy(snapshot)
    fake_src=types.ModuleType('src');fake_src.__path__=[]
    st=types.ModuleType('src.specialist_trade')
    seen=[]
    def norm(orig,rows,team_id,incoming_ids,outgoing_ids):
        seen.append(('normalize',team_id,tuple(sorted(incoming_ids))))
        return rows
    def with_rosters(snap,rosters):
        out=copy.deepcopy(snap)
        for t in out['espn']['teams']:
            if t['team_id'] in rosters:t['roster']=copy.deepcopy(rosters[t['team_id']])
        return out
    def composed(hybrid,final,league,model,values,tid,scenarios,progress_label):
        assert len(hybrid['espn']['available_players'])==0
        assert len(final['espn']['available_players'])==0
        return 'ctx',None,np.ones((scenarios,2))*tid,np.ones((scenarios,2))
    st._assert_supported_trade_specialist_state=lambda *a,**kw:None
    st._normalize_incoming_assignments=norm
    st._snapshot_with_rosters=with_rosters
    st._hybrid_player_snapshot=lambda origin,final,tids:with_rosters(origin,
        {t['team_id']:t['roster'] for t in final['espn']['teams']})
    st._baseline_state=lambda s,l,m,v,tid,n,progress_label:(None,np.zeros(n),np.zeros((n,2)),np.zeros((n,2)))
    st._composed_after_state=composed
    st._scenario_h2h_utility_against=lambda w,o,c:np.sum(w,axis=1)
    mk=types.ModuleType('src.market_manager')
    mk.roster_is_legal=lambda *a,**kw:True
    tm=types.ModuleType('src.trade_timing')
    tm.splice_effective_week=lambda baseline,after,week:after
    for name,val in [('src',fake_src),('src.specialist_trade',st),('src.market_manager',mk),('src.trade_timing',tm)]:
        monkeypatch.setitem(sys.modules,name,val)
    fake_src.specialist_trade=st
    offer={'give_ids':[11],'receive_ids':[101], 'partner_team_id':2,
           'modeled_partner_auto_drop_ids':[]}
    branch={'fill_outcomes':[{'side':'user','id':201,'conditional_success':True,
                             'materialized_from_frozen_market':True}]}
    responses,cache=mod._native_pair(snapshot,{}, {},Path('unused'),offer,
                      {'drop_ids':[13]},branch,1,16,Path('/fake'),None)
    assert set(responses)=={1,2}
    assert len(cache)==2
    assert ('normalize',1,(101,201)) in seen
    assert snapshot==before


def test_no_unintended_execution_paths():
    raw=FILE.read_text('utf-8')
    for forbidden in ('requests.post(', 'fetch_private_league(', 'create_trade(', 'os.system(',
                      'subprocess.run(', 'AUTO_APPROVED', 'GenUI.'):
        assert forbidden not in raw
    assert '--execute-native' in raw
