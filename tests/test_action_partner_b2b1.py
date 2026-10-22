"""B2b1 two-manager conditional response; all MC kernels synthetic or stubbed."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import sys
import types
import numpy as np
import pytest
from test_action_predictive_b2 import inputs

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/operations'))
SPEC=importlib.util.spec_from_file_location('action_partner_b2b', ROOT/'tools/operations/action_partner_b2b.py')
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

def fake_joint(snapshot,league,model,values,offer,option,tid,n,runtime,cache):
    if cache is not None:
        assert cache['seed'] == 27
    base=np.arange(n,dtype=float)/n
    bump=option['drop_ids'][0]/1000
    return {1:(base,base+bump), 2:(base,base+.5)}, {'seed':27}

def test_two_manager_paired_and_native_relative_deltas():
    s,c,r,oid=inputs()
    out=m.evaluate(s,c,r,{}, {},Path('values'),Path('runtime'),oid,scenarios=32,kernel=fake_joint)
    assert out['two_manager_options_evaluated']==3
    assert out['native_drop_choice_comparison_reference']==[13]
    assert out['espn_action_authority']=='NONE'
    assert out['options'][0]['native_selected']
    for x in out['options']:
        assert x['state']=='CONDITIONAL_TWO_MANAGER_MC_NOT_CERTIFIED'
        assert x['partner']['paired_delta_mean']==pytest.approx(.5)
        assert x['user']['mc_scenarios']==32
    alt=next(x for x in out['options'] if x['drop_ids']==[12])
    assert alt['versus_native_drop_choice']['user']['paired_delta_mean']==pytest.approx(-.001)
    assert alt['versus_native_drop_choice']['partner']['paired_delta_mean']==pytest.approx(0.)


def test_partner_locked_auto_drop_blocks_all_options():
    s,c,r,oid=inputs()
    p=s['espn']['teams'][1]['roster'][0]
    p['droppable']=False; p['lineup_locked']=True
    # Directly request a model-dropped owned partner asset (not received asset).
    offer=r['channels'][2]['action']['offers'][0]
    offer['partner_auto_drop_ids']=[101]
    c['behavioral_observation_state']['snapshot_sha256']=m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=m.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})
    calls=[]
    def forbidden(*args): calls.append(1);raise AssertionError('must not run MC')
    out=m.evaluate(s,c,r,{}, {},Path('x'),Path('x'),oid,scenarios=32,kernel=forbidden)
    assert not calls
    assert out['two_manager_options_evaluated']==0
    assert all('PARTNER_MODELED_DROP_PERMISSION_OR_LOCK_UNPROVEN' in x['blockers'] for x in out['options'])


def test_missing_partner_drop_proof_fails_closed():
    s,c,r,oid=inputs()
    _,offer=m.selection(s,c,r,oid)
    offer=copy.deepcopy(offer)
    offer['modeled_partner_auto_drop_ids']=[99999]
    assert m.partner_drop_proof(s,offer)==['PARTNER_MODELED_DROP_NOT_FROZEN_OWNED']



def test_partner_auto_drop_cannot_also_be_trade_outgoing():
    s,c,r,oid=inputs()
    _,offer=m.selection(s,c,r,oid)
    offer=copy.deepcopy(offer)
    offer['modeled_partner_auto_drop_ids']=[100]
    assert 'PARTNER_MODELED_DROP_ALREADY_OUTGOING' in m.partner_drop_proof(s,offer)

def test_invalid_kernel_shape_causes_blockers_not_authority():
    s,c,r,oid=inputs()
    bad=lambda *args:({1:(np.ones(32),np.ones(32))},{})
    out=m.evaluate(s,c,r,{}, {},Path('x'),Path('x'),oid,scenarios=32,kernel=bad)
    assert out['two_manager_options_evaluated']==0
    assert all(x['state']=='BLOCKED' for x in out['options'])
    assert all('BOTH_MANAGER_PAIRED_MC_REQUIRED' in x['blockers'] for x in out['options'])


def test_mutation_cannot_be_hidden_by_kernel():
    s,c,r,oid=inputs()
    def mutating(snapshot,league,model,values,offer,option,tid,n,runtime,cache):
        snapshot['espn']['teams'][0]['roster'][0]['injury_status']='OUT'
        return fake_joint(snapshot,league,model,values,offer,option,tid,n,runtime,cache)
    with pytest.raises(m.CertificationBlocked,match='FROZEN_INPUT_OR_CONFIG_MUTATED'):
        m.evaluate(s,c,r,{}, {},Path('x'),Path('x'),oid,scenarios=32,kernel=mutating)


def test_scenario_bounds_and_missing_offer_fail():
    s,c,r,oid=inputs()
    with pytest.raises(m.CertificationBlocked,match='SCENARIO_BUDGET_INVALID'):
        m.evaluate(s,c,r,{}, {},Path('x'),Path('x'),oid,scenarios=1024,kernel=fake_joint)
    with pytest.raises(m.CertificationBlocked,match='OFFER_ID_NOT_UNIQUE_OR_MISSING'):
        m.evaluate(s,c,r,{}, {},Path('x'),Path('x'),'missing',scenarios=32,kernel=fake_joint)


def test_bounded_partial_options_still_blocked():
    s,c,r,oid=inputs()
    out=m.evaluate(s,c,r,{}, {},Path('x'),Path('x'),oid,scenarios=32,max_options=1,kernel=fake_joint)
    assert out['two_manager_options_evaluated']==1
    assert out['structural_options_not_selected_for_bounded_probe']==2
    assert 'UNEVALUATED_DROP_OPTIONS' in out['unresolved']


def test_cli_check_only_does_not_read_runtime_or_execute_mc(monkeypatch,tmp_path,capsys):
    import json
    s,c,r,oid=inputs()
    paths=[]
    for name,obj in (('snapshot',s),('capture',c),('receipt',r)):
        p=tmp_path/(name+'.json');p.write_text(json.dumps(obj));paths += ['--'+name,str(p)]
    cli=paths+['--offer-id',oid,'--runtime',str(tmp_path/'NOT_INSTALLED'), '--league', 'notexist','--model','notexist','--values','notexist']
    assert m.main(cli)==0
    assert 'NATIVE_MC_NOT_STARTED=TRUE' in capsys.readouterr().out


def test_native_joint_adapts_native_apis_and_partner_no_fill(monkeypatch,tmp_path):
    s,c,r,oid=inputs()
    _,offer=m.selection(s,c,r,oid)
    option=offer['structural_options'][0]
    src=types.ModuleType('src');src.__path__=[]
    st=types.ModuleType('src.specialist_trade')
    market=types.ModuleType('src.market_manager')
    timing=types.ModuleType('src.trade_timing')
    checked=[]
    def legal(roster,league,*,target_size):
        checked.append(len(roster));return 0<len(roster)<=target_size
    market.roster_is_legal=legal
    st._assert_supported_trade_specialist_state=lambda roster,side:None
    st._normalize_incoming_assignments=lambda original,final,*,team_id,incoming_ids,outgoing_ids:copy.deepcopy(final)
    def swapped(snapshot,rosters):
        result=copy.deepcopy(snapshot)
        assert 1001 not in {p['espn_id'] for rows in rosters.values() for p in rows}
        for team in result['espn']['teams']:
            if team['team_id'] in rosters:team['roster']=rosters[team['team_id']]
        return result
    st._snapshot_with_rosters=swapped
    st._hybrid_player_snapshot=lambda before,after,team_ids:copy.deepcopy(after)
    calls=[]
    def baseline(snapshot,league,model,values,tid,n,*,progress_label):
        calls.append(tid)
        return types.SimpleNamespace(team_id=tid), np.ones(n),np.ones((n,17)),np.ones((n,17))
    st._baseline_state=baseline
    st._composed_after_state=lambda hybrid,final,league,model,values,tid,n,*,progress_label:(types.SimpleNamespace(team_id=tid),None,np.full((n,17),2.),np.ones((n,17)))
    st._scenario_h2h_utility_against=lambda weekly,opp,ctx:np.mean(weekly,axis=1)
    timing.splice_effective_week=lambda before,after,effective:np.concatenate([before[:,:effective-1],after[:,effective-1:]],axis=1)
    monkeypatch.setitem(sys.modules,'src',src)
    monkeypatch.setitem(sys.modules,'src.specialist_trade',st)
    monkeypatch.setitem(sys.modules,'src.market_manager',market)
    monkeypatch.setitem(sys.modules,'src.trade_timing',timing)
    response,baseline_cache=m._native_joint(s,{}, {},Path('x'),offer,option,1,32,tmp_path,None)
    assert checked==[4,1]
    assert calls==[1,2]
    assert set(response)=={1,2}
    assert response[1][1][0]>response[1][0][0]
    assert response[2][1][0]>response[2][0][0]
    second,cache2=m._native_joint(s,{}, {},Path('x'),offer,option,1,32,tmp_path,baseline_cache)
    assert cache2.keys()==baseline_cache.keys()
    assert calls==[1,2]
    assert all(len(y[0])==32 for y in second.values())


def test_zero_review_blocked_before_native_calls(monkeypatch,tmp_path):
    s,c,r,oid=inputs()
    s['espn']['transaction_settings']['trade_review_hours']=0
    _,offer=m.selection(*_rehash(s,c,r),oid)
    option=offer['structural_options'][0]
    with pytest.raises(m.CertificationBlocked,match='TRADE_EFFECTIVE_WEEK_NOT_SOURCE_RESOLVED'):
        m._native_joint(s,{}, {},Path('x'),offer,option,1,32,tmp_path,None)


def _rehash(s,c,r):
    c['behavioral_observation_state']['snapshot_sha256']=m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=m.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})
    return s,c,r


def test_source_has_no_espn_or_transaction_submission():
    raw=(ROOT/'tools/operations/action_partner_b2b.py').read_text()
    for forbidden in ('requests.get(', 'requests.post(', 'create_trade(', 'subprocess.run(', 'os.system('):
        assert forbidden not in raw
