"""B2b4b synthetic joint response contracts (no private ESPN or native MC)."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys
import types
import hashlib

import numpy as np
import pytest

FILE = Path(__file__).resolve().parents[1] / 'tools/operations/action_joint_predictive_b2b4b.py'


def _case(order, success, state='CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED'):
    return {'offer_order':list(order), 'fill_states':[
                {'offer_id':'A','success_ids':[41] if success else []},
                {'offer_id':'B','success_ids':[]}],
            'steps':[{'partner_team_id':2},{'partner_team_id':3}] if state.startswith('CONDITIONAL_') else [],
            'state':state, 'blockers':[] if state.startswith('CONDITIONAL_') else ['SEQUENTIAL_OWNER_CONFLICT'],
            'final_owned_ids_by_team':{'1':[21,31]+([41] if success else []),
                        '2':[11,12,22], '3':[13,32,33]},
            'final_market_asset_ids':[23]+([] if success else [41]),
            'released_to_field_ids':[23]}


def setup(monkeypatch, *, blocked=False):
    def player(pid, tid):
        return {'espn_id':pid,'on_team_id':tid,'position':'RB',
                'fantasy_status':'ROSTERED','lineup_locked':False}
    snapshot={'espn':{'season':2026,'week':8,
        'transaction_settings':{'trade_review_hours':48},
        'teams':[{'team_id':i,'roster':[player(p,i) for p in ids]}
            for i,ids in ((1,[11,12,13]),(2,[21,22,23]),(3,[31,32,33]))],
        'available_players':[{'espn_id':41,'position':'RB','fantasy_status':'FREEAGENT'}]}}
    cases=[_case(('A','B'),False),_case(('A','B'),True),
           _case(('B','A'),False),_case(('B','A'),True)]
    if blocked:
        cases=[_case(('A','B'),False,'BLOCKED'), _case(('A','B'),True,'BLOCKED'),
               _case(('B','A'),False,'BLOCKED'),_case(('B','A'),True,'BLOCKED')]
    def frozen(s):
        roster={t['team_id']:{p['espn_id']:copy.deepcopy(p) for p in t['roster']}
                for t in s['espn']['teams']}
        market={p['espn_id']:copy.deepcopy(p) for p in s['espn']['available_players']}
        return roster,market
    deps={'action_frontier':{'CertificationBlocked':ValueError,
        'canonical_sha256':lambda obj:hashlib.sha256(repr(obj).encode()).hexdigest()},
          'action_joint_state_b2b4a':{
             'audit':lambda *args:{'orders':2,'branch_pairs_per_order':2,'cases':copy.deepcopy(cases)},
             '_frozen_state':frozen},
          'action_predictive_b2':{'MAX_SCENARIOS':512, 'paired_summary':paired,
             'require':require, 'verify_runtime':lambda *a:None}}
    for name,members in deps.items():
        m=types.ModuleType(name);m.__dict__.update(members)
        monkeypatch.setitem(sys.modules,name,m)
    spec=importlib.util.spec_from_file_location('b2b4b_under_test',FILE)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    docs=(snapshot,{'capture':'frozen'}, {'team_id':1}, {'roster':{}}, {'model':True})
    return mod,docs,cases


def require(ok, reason):
    if not ok:raise ValueError(reason)


def paired(a,b):
    a,b=np.asarray(a),np.asarray(b)
    if a.shape != (16,) or b.shape != (16,) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('PAIR_INVALID')
    d=b-a
    return {'mc_scenarios':16,'paired_delta_mean':float(d.mean())}


def kernel(snapshot,league,model,values,runtime,case,ids,n,cache):
    assert n==16
    assert ids==(1,2,3)
    assert case['released_to_field_ids']==[23]
    shift=1 if case['offer_order']==['A','B'] else 3
    shift+=2 if case['fill_states'][0]['success_ids'] else 0
    out={tid:{'hold':np.zeros(n),'joint':np.full(n,shift+tid),
              'hold_opponent_reference':np.full(n,10),
              'joint_opponent_reference':np.full(n,11+shift)} for tid in ids}
    return out, (cache or {tid:'baseline' for tid in ids})


def evaluate(mod,docs,mc=kernel):
    return mod.evaluate(*docs,Path('fake'),Path('/fake/runtime'),'A','B',[],[],scenarios=16,kernel=mc)


def test_all_orders_and_fill_states_are_jointly_valued_without_probabilities(monkeypatch):
    mod,docs,_=setup(monkeypatch)
    before=copy.deepcopy(docs)
    result=evaluate(mod,docs)
    assert result['structural_cases']==4
    assert result['joint_mc_cases_evaluated']==4
    assert result['certified_actions']==0
    assert result['future_acquisition_joint_probability']=='UNKNOWN'
    assert result['released_asset_field_exposure']=='LEDGER_ONLY_NO_REACQUISITION_MODEL'
    assert result['espn_action_authority']=='NONE'
    assert docs==before
    assert all('opponent_reference_shift' in r['affected_managers']['1'] for r in result['cases'])
    assert all(r['versus_other_order']['1']['paired_delta_mean'] != 0 for r in result['cases'])


def test_release_identity_is_not_frozen_free_agent(monkeypatch):
    mod,docs,cases=setup(monkeypatch)
    final, available, released=mod._reconstruct(docs[0],cases[0])
    assert {x['espn_id'] for x in available}=={41}
    assert released==[23]
    assert 23 not in {x['espn_id'] for x in available}
    final, available, released=mod._reconstruct(docs[0],cases[1])
    assert available==[]
    assert 41 in [p['espn_id'] for p in final[1]]


def test_incomplete_ledger_and_duplicate_ownership_fail_before_kernel(monkeypatch):
    mod,docs,cases=setup(monkeypatch)
    bad=copy.deepcopy(cases[0]);bad['final_market_asset_ids']=[41]
    with pytest.raises(ValueError,match='FIELD_LEDGER_NOT_CONSERVED'):
        mod._reconstruct(docs[0],bad)
    bad=copy.deepcopy(cases[0]);bad['final_owned_ids_by_team']['2'].append(21)
    with pytest.raises(ValueError,match='FINAL_OWNERSHIP_COLLISION'):
        mod._reconstruct(docs[0],bad)
    bad=copy.deepcopy(cases[0]);bad['released_to_field_ids']=[]
    with pytest.raises(ValueError,match='FIELD_LEDGER_NOT_CONSERVED'):
        mod._reconstruct(docs[0],bad)


def test_all_blocked_branches_do_not_invoke_mc(monkeypatch):
    mod,docs,_=setup(monkeypatch,blocked=True)
    def forbidden(*args):raise AssertionError('MC must not run')
    result=evaluate(mod,docs,forbidden)
    assert result['joint_mc_cases_evaluated']==0
    assert all(r['state']=='BLOCKED' for r in result['cases'])


def test_nonfinite_missing_manager_and_mutated_model_fail_closed(monkeypatch):
    mod,docs,_=setup(monkeypatch)
    def missing(*args):
        response,cache=kernel(*args)
        del response[3]
        return response,cache
    result=evaluate(mod,docs,missing)
    assert result['joint_mc_cases_evaluated']==0
    def infinite(*args):
        response,cache=kernel(*args)
        response[1]['joint']=np.asarray(response[1]['joint'],dtype=float)
        response[1]['joint'][0]=np.inf
        return response,cache
    result=evaluate(mod,docs,infinite)
    assert result['joint_mc_cases_evaluated']==0
    def mutate(*args):
        args[2]['model']=False
        return kernel(*args)
    with pytest.raises(ValueError,match='B2B4B_FROZEN_INPUT_OR_CONFIG_MUTATED'):
        evaluate(mod,docs,mutate)


def test_budget_and_paired_semantics(monkeypatch):
    mod,docs,_=setup(monkeypatch)
    with pytest.raises(ValueError,match='B2B4B_MC_BUDGET_INVALID'):
        mod.evaluate(*docs,Path('x'),Path('y'),'A','B',[],[],scenarios=8,kernel=kernel)
    orig=mod.structural_audit
    def oversized(*args):
        x=copy.deepcopy(orig(*args));x['cases']*=10
        return x
    mod.structural_audit=oversized
    with pytest.raises(ValueError,match='B2B4B_STRUCTURAL_CASE_SET_INVALID'):
        evaluate(mod,docs)


def test_native_joint_composes_all_team_rosters_and_hides_releases(monkeypatch):
    mod,docs,cases=setup(monkeypatch)
    source=types.ModuleType('src');source.__path__=[]
    st=types.ModuleType('src.specialist_trade')
    seen=[]
    def with_rosters(s,rosters):
        out=copy.deepcopy(s)
        for team in out['espn']['teams']:
            if team['team_id'] in rosters:team['roster']=copy.deepcopy(rosters[team['team_id']])
        return out
    def composed(hybrid,final,league,model,values,tid,n,progress_label):
        seen.append((tid, {t['team_id']:tuple(p['espn_id'] for p in t['roster'])
                  for t in final['espn']['teams']}))
        assert {p['espn_id'] for p in hybrid['espn']['available_players']}=={41}
        assert {p['espn_id'] for p in final['espn']['available_players']}=={41}
        assert 23 not in {p['espn_id'] for p in final['espn']['available_players']}
        return object(),None,np.ones((n,2))*tid,np.ones((n,2))*5
    st._assert_supported_trade_specialist_state=lambda *a,**k:None
    st._normalize_incoming_assignments=lambda before,rows,**kwargs:rows
    st._snapshot_with_rosters=with_rosters
    st._hybrid_player_snapshot=lambda snapshot,final,ids:copy.deepcopy(final)
    st._baseline_state=lambda snapshot,league,model,values,tid,n,progress_label:(object(),np.zeros(n),np.zeros((n,2)),np.zeros((n,2)))
    st._composed_after_state=composed
    st._scenario_h2h_utility_against=lambda w,o,ctx:w.sum(axis=1)
    st._scenario_season_ppg=lambda weekly,ctx:weekly.mean(axis=1)
    src_market=types.ModuleType('src.market_manager')
    src_market.roster_is_legal=lambda *args,**kwargs:True
    time=types.ModuleType('src.trade_timing')
    time.splice_effective_week=lambda before,after,w:after
    for name,m in [('src',source),('src.specialist_trade',st),
                   ('src.market_manager',src_market),('src.trade_timing',time)]:
        monkeypatch.setitem(sys.modules,name,m)
    source.specialist_trade=st
    for module,name in ((st,'specialist_trade'),(src_market,'market_manager'),
                        (time,'trade_timing')):
        module.__file__=str((Path('fake').resolve()/'src'/ (name+'.py')))
    out,cache=mod._native_joint(docs[0],docs[3],docs[4],Path('unused'),
                 Path('fake'),cases[0],(1,2,3),16,None)
    assert set(out)=={1,2,3} and len(cache)==3
    assert len(seen)==3 and seen[0][1][1]==(21,31)


def test_source_read_only_and_no_provider_or_transaction_methods():
    text=FILE.read_text(encoding='utf-8')
    assert '--execute-native' in text and 'CHECK_ONLY' in text
    for forbidden in ('requests.post(', 'fetch_private_league(', 'create_trade(',
                      'subprocess.run(', 'os.system(', 'AUTO_APPROVED'):
        assert forbidden not in text
