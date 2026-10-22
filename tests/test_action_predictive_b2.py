"""B2a frozen paired-utility diagnostic tests; never execute live ESPN/MC."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from test_action_frontier_b1 import setup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/operations'))
P=ROOT/'tools/operations/action_predictive_b2.py'
spec=importlib.util.spec_from_file_location('action_predictive_b2',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def inputs():
    s,c,r=setup()
    f=m.build_frontier(s,c,r)
    return s,c,r,f['offers'][0]['offer_id']


def test_bounded_selection_lamar_options_and_lock_evidence():
    s,c,r,oid=inputs()
    frontier,offer=m.selection(s,c,r,oid)
    assert len(offer['structural_options'])==3
    assert {tuple(x['drop_ids']) for x in offer['structural_options']}=={(12,),(13,),(14,)}
    assert not offer['structural_options_truncated']


def test_bounded_partial_frontier_is_explicit():
    s,c,r,oid=inputs()
    _,offer=m.selection(s,c,r,oid,max_options=2)
    chosen,not_selected=m.probe_options(offer,limit=2)
    assert len(chosen)==2 and not_selected==1
    assert chosen[0]['native_selected_normalization'] is True
    result=m.evaluate(s,c,r,{}, {},Path('x'),Path('mock'),oid,scenarios=32,max_options=2,
                      kernel=lambda *args:(np.ones(32),np.ones(32),None))
    assert result['structural_options_not_selected_for_bounded_probe']==1
    assert 'UNEVALUATED_ALTERNATIVE_DROP_OPTIONS' in result['unresolved']


def test_forged_offer_id_blocks():
    s,c,r,oid=inputs()
    with pytest.raises(m.CertificationBlocked,match='OFFER_ID_NOT_UNIQUE_OR_MISSING'):
        m.selection(s,c,r,'forged')


def test_native_locked_drop_never_assessed():
    s,c,r,oid=inputs()
    s['espn']['teams'][0]['roster'][2]['droppable']=False
    c['behavioral_observation_state']['snapshot_sha256']=m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=m.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})
    _,offer=m.selection(s,c,r,oid)
    row=next(x for x in offer['structural_options'] if x['native_selected_normalization'])
    assert not m._safe_option(offer,row)[0]


def test_user_future_fill_must_not_be_assumed():
    s,c,r,oid=inputs()
    a=r['channels'][2]['action']['offers'][0]
    a.update({'give_ids':[11,13], 'receive_ids':[100],
              'user_auto_drop_ids':[], 'user_auto_add_ids':[999],
              'partner_auto_add_ids':[]})
    f=m.build_frontier(s,c,r)['offers'][0]
    _, reasons=m._safe_option(f,f['structural_options'][0])
    assert 'FUTURE_USER_FILL_REQUIRED_NO_GUARANTEE' in reasons


def test_paired_summary_common_scenarios_and_nonfinite_gate():
    base=np.arange(64,dtype=float)
    alt=base + 0.25
    x=m.paired_summary(base,alt)
    assert x['mc_scenarios']==64
    assert x['paired_delta_mean']==pytest.approx(.25)
    assert x['paired_p_better']==1
    with pytest.raises(m.CertificationBlocked,match='PAIRED_MC_ARRAY_SHAPE'):
        m.paired_summary(base,alt[:-1])
    alt[4]=np.nan
    with pytest.raises(m.CertificationBlocked,match='NONFINITE'):
        m.paired_summary(base,alt)


def test_all_three_options_use_same_frozen_scenario_baseline():
    s,c,r,oid=inputs()
    calls=[]
    def fake(snapshot,league,model,values,offer,option,tid,n,runtime,prior):
        # native adapter contract checks that baseline is passed on after first
        if calls: assert prior is calls[0]
        marker=object() if not calls else prior
        calls.append(marker)
        base=np.arange(n,dtype=float)/n
        return base,base+(.01*option['drop_ids'][0]),marker
    result=m.evaluate(s,c,r,{}, {},Path('x'),Path('mock'),oid,scenarios=32,kernel=fake)
    assert len(calls)==3
    assert result['options_evaluated']==3
    assert all(item['comparison_state'].startswith('NATIVE_MC_EVALUATED') for item in result['options'])
    assert result['espn_action_authority']=='NONE'
    assert result['state'].startswith('BLOCKED_')


def test_external_snapshot_mutation_never_silently_accepted():
    s,c,r,oid=inputs()
    def mutate(snapshot,league,model,values,offer,option,tid,n,runtime,prior):
        snapshot['espn']['teams'][0]['roster'][0]['injury_status']='OUT'
        a=np.ones(n)
        return a,a,prior
    with pytest.raises(m.CertificationBlocked,match='FROZEN_INPUT_OR_CONFIG_MUTATED'):
        m.evaluate(s,c,r,{}, {},Path('x'),Path('mock'),oid,scenarios=32,kernel=mutate)


def test_runner_fails_closed_when_missing_runtime(tmp_path):
    with pytest.raises(m.CertificationBlocked,match='UNEXPECTED_COMMISSIONED_RUNTIME_ROOT'):
        m.verify_runtime(tmp_path)


def test_no_espn_or_model_code_writes():
    code=P.read_text('utf-8')
    for bad in ('requests.post(', 'requests.get(', 'create_trade(', 'subprocess.run(', 'os.system('):
        assert bad not in code


def test_baseline_error_explicit_no_partial_certification():
    s,c,r,oid=inputs()
    def failing(*args): raise ValueError('no valid matchup')
    out=m.evaluate(s,c,r,{}, {},Path('x'),Path('mock'),oid,scenarios=32,kernel=failing)
    assert out['options_evaluated']==0
    assert all(x['comparison_state']=='BLOCKED' for x in out['options'])
    assert out['espn_action_authority']=='NONE'


def test_native_adapter_no_future_fill_state_and_shared_baseline(monkeypatch,tmp_path):
    import types
    s,c,r,oid=inputs()
    _,offer=m.selection(s,c,r,oid)
    option=offer['structural_options'][0]
    # Only structural evidence here, not fake football scores from a screen:
    # the stubbed native functions verify call and state wiring to real native API.
    import sys
    src=types.ModuleType('src');src.__path__=[]
    sp=types.ModuleType('src.specialist_trade')
    mm=types.ModuleType('src.market_manager')
    timing=types.ModuleType('src.trade_timing')
    state={}
    def roster_legal(roster,league,*,target_size):
        return len(roster)<=target_size and bool(roster)
    mm.roster_is_legal=roster_legal
    sp._assert_supported_trade_specialist_state=lambda roster,side: None
    def norm(original, final,*,team_id,incoming_ids,outgoing_ids):
        assert all(p['espn_id'] not in set(outgoing_ids) for p in final if p['espn_id'] not in set(incoming_ids))
        return copy.deepcopy(final)
    sp._normalize_incoming_assignments=norm
    def modify(snapshot,rosters):
        x=copy.deepcopy(snapshot)
        for team in x['espn']['teams']:
            if team['team_id'] in rosters: team['roster']=copy.deepcopy(rosters[team['team_id']])
        state['rosters']=rosters
        return x
    sp._snapshot_with_rosters=modify
    sp._hybrid_player_snapshot=lambda original,final,teams:copy.deepcopy(final)
    def baseline(snapshot,league,model,values,tid,n,*,progress_label):
        return types.SimpleNamespace(team_id=tid),np.ones(n),np.ones((n,17)),np.ones((n,17))
    sp._baseline_state=baseline
    def after(hybrid,final,league,model,values,tid,n,*,progress_label):
        return types.SimpleNamespace(team_id=tid),None,np.full((n,17),2.),np.ones((n,17))
    sp._composed_after_state=after
    sp._scenario_h2h_utility_against=lambda week,opponent,ctx: np.mean(week,axis=1)
    timing.splice_effective_week=lambda before,after,week: np.concatenate((before[:,:week-1],after[:,week-1:]),axis=1)
    timing.season_ppg_from_weekly=lambda *args:np.ones(32)
    monkeypatch.setitem(sys.modules,'src',src)
    monkeypatch.setitem(sys.modules,'src.specialist_trade',sp)
    monkeypatch.setitem(sys.modules,'src.market_manager',mm)
    monkeypatch.setitem(sys.modules,'src.trade_timing',timing)
    base,after_,base_cache=m._native_arrays(s,{'roster':{}},{},Path('value.csv'),offer,option,1,32,tmp_path)
    assert base.shape==after_.shape==(32,)
    # 48h review -> Week 8 effective; weeks 1..7 baseline, remaining 2
    assert after_[0]>base[0]
    assert all(1001 != p['espn_id'] for roster in state['rosters'].values() for p in roster)
    # No call has secretly added the native future free agent for the partner.
    assert state['rosters'][2] and len(state['rosters'][2])==1
