"""B2b2 deterministic frozen fill/portfolio diagnostics; no native football MC."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import sys
import pytest
from test_action_frontier_b1 import setup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/operations'))
SPEC=importlib.util.spec_from_file_location('action_portfolio_b2b2',ROOT/'tools/operations/action_portfolio_b2b2.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)


def league():
    return {'roster':{'QB':1,'WR':0,'DST':0,'K':0},
            'position_maximums':{'QB':5,'WR':6,'DST':3,'K':2}}


def rehash(s,c):
    c['behavioral_observation_state']['snapshot_sha256']=m.canonical_sha256(s)
    c['integrity']['canonical_payload_sha256']=m.canonical_sha256({k:v for k,v in c.items() if k!='integrity'})


def test_no_fill_and_success_are_distinct_without_guessed_probability():
    s,c,r=setup()
    out=m.audit(s,c,r,league())
    assert out['offer_count']==1 and out['pair_count']==0
    assert out['state'].startswith('BLOCKED_') and out['espn_action_authority']=='NONE'
    assert out['eligible_for_approval_count']==0
    branch=out['offers'][0]['options'][0]['branches']
    assert len(branch)==2
    assert branch[0]['fill_outcomes'][0]['conditional_success'] is False
    assert branch[1]['fill_outcomes'][0]['conditional_success'] is True
    assert 'FUTURE_FILL_AT_PROCESSING_UNVERIFIED:partner' in branch[1]['unresolved']
    assert out['offers'][0]['options'][0]['future_fill_acquisition_probabilities']=='UNKNOWN_NOT_ESTIMATED'
    assert out['offers'][0]['options'][0]['paired_mc_for_all_fill_branches']=='NOT_RUN'


def test_missing_future_fill_not_silently_inserted():
    s,c,r=setup()
    out=m.audit(s,c,r,league())
    row=out['offers'][0]
    assert 'FUTURE_FILL_NOT_IN_FROZEN_AVAILABLE_POOL:partner' in row['future_fill_sources_unverified']
    branches=row['options'][0]['branches']
    assert branches[0]['partner']['owned_count']==branches[1]['partner']['owned_count']


def test_freeagent_in_snapshot_still_future_unknown():
    s,c,r=setup()
    s['espn'].setdefault('available_players',[]).append({'espn_id':1001,'name':'Candidate',
         'position':'WR','fantasy_status':'FREEAGENT'})
    rehash(s,c)
    out=m.audit(s,c,r,league())
    rows=out['offers'][0]['options'][0]['branches']
    assert rows[1]['partner']['owned_count']==rows[0]['partner']['owned_count']+1
    assert 'FUTURE_FILL_AT_PROCESSING_UNVERIFIED:partner' in rows[1]['unresolved']
    assert out['offers'][0]['future_fill_sources_unverified']==[]


def test_waiver_is_not_assumed_to_be_freeagent():
    s,c,r=setup()
    s['espn'].setdefault('available_players',[]).append({'espn_id':1001,'name':'Candidate',
          'position':'WR','fantasy_status':'WAIVERS'})
    rehash(s,c)
    out=m.audit(s,c,r,league())
    assert 'FUTURE_FILL_NOT_FROZEN_FREEAGENT:partner' in out['offers'][0]['future_fill_sources_unverified']


def test_duplicate_fill_to_both_managers_is_refused():
    s,c,r=setup()
    a=r['channels'][2]['action']['offers'][0]
    a['user_auto_add_ids']=[1001]
    with pytest.raises(m.CertificationBlocked,match='FUTURE_FILL_ASSET_DOUBLE_ASSIGNED'):
        m.audit(s,c,r,league())


def test_more_than_four_fill_states_fails_closed():
    s,c,r=setup()
    a=r['channels'][2]['action']['offers'][0]
    a['partner_auto_add_ids']=[1001,1002,1003,1004,1005]
    with pytest.raises(m.CertificationBlocked,match='FILL_BRANCH_BUDGET_EXCEEDED'):
        m.audit(s,c,r,league())


def test_same_given_asset_is_mutually_exclusive():
    s,c,r=setup()
    a=copy.deepcopy(r['channels'][2]['action']['offers'][0])
    a['receive_ids']=[100]
    a['receive_names']=['CeeDee Lamb'];a['receive_positions']=['WR']
    a['user_auto_drop_ids']=[]
    r['channels'][2]['action']['offers'].append(a)
    out=m.audit(s,c,r,league())
    assert out['pair_count']==1
    assert out['pairs'][0]['direct_conflicting_player_ids']==[11,100]
    assert out['pairs'][0]['status']=='MUTUALLY_EXCLUSIVE_AT_FROZEN_ASSET_STATE'
    assert out['pairs'][0]['joint_utility']=='NOT_COMPUTED_NO_ADDITIVE_STANDALONE_MC'


def test_same_partner_distinct_assets_remain_coupled_not_certified():
    s,c,r=setup()
    a=r['channels'][2]['action']['offers'][0]
    a.update({'receive_ids':[101],'receive_names':['Ravens D/ST'],
              'receive_positions':['DST'],'user_auto_drop_ids':[]})
    b=copy.deepcopy(a)
    b.update({'give_ids':[14], 'give_names':['Other'], 'receive_ids':[100],
              'receive_names':['CeeDee Lamb'],'receive_positions':['WR']})
    r['channels'][2]['action']['offers'].append(b)
    out=m.audit(s,c,r,league())
    pair=out['pairs'][0]
    assert pair['same_partner'] is True
    assert pair['direct_conflicting_player_ids']==[]
    assert pair['status']=='COUPLED_JOINT_ROSTER_AND_EFFECTIVE_TIME_MC_REQUIRED'


def test_cross_trade_native_drop_of_outgoing_asset_detected():
    offers=[{'offer_id':'a','partner_team_id':2,'give_ids':[11],'receive_ids':[100],
             'modeled_native_auto_drop_ids':[14]},
            {'offer_id':'b','partner_team_id':3,'give_ids':[14],'receive_ids':[200],
             'modeled_native_auto_drop_ids':[]}]
    pair=m._portfolios(offers)[0]
    assert pair['direct_conflicting_player_ids']==[14]
    assert pair['status']=='MUTUALLY_EXCLUSIVE_AT_FROZEN_ASSET_STATE'


def test_partial_offer_budget_refused_not_silently_truncated():
    s,c,r=setup()
    with pytest.raises(m.CertificationBlocked,match='INVALID_OFFER_BUDGET'):
        m.audit(s,c,r,league(),max_offers=0)
    with pytest.raises(m.CertificationBlocked,match='OFFER_FRONTIER_TOO_LARGE'):
        m.audit(s,c,r,league(),max_offers=1) if _second_offer(s,c,r) else None


def _second_offer(s,c,r):
    a=copy.deepcopy(r['channels'][2]['action']['offers'][0]);a['receive_ids']=[100]
    a['receive_names']=['CeeDee Lamb'];a['receive_positions']=['WR']
    a['user_auto_drop_ids']=[]
    r['channels'][2]['action']['offers'].append(a)
    return True


def test_missing_league_roster_rules_blocks():
    s,c,r=setup()
    with pytest.raises(m.CertificationBlocked,match='LEAGUE_ROSTER_MIN_MAX_UNVERIFIED'):
        m.audit(s,c,r,{'roster':{}})


def test_unbound_snapshot_change_detected():
    s,c,r=setup()
    s['espn']['teams'][0]['roster'][0]['injury_status']='OUT'
    with pytest.raises(m.CertificationBlocked,match='CAPTURE_SNAPSHOT_BINDING_INVALID'):
        m.audit(s,c,r,league())


def test_result_does_not_mutate_evidence():
    s,c,r=setup()
    before=[m.canonical_sha256(x) for x in (s,c,r)]
    m.audit(s,c,r,league())
    assert [m.canonical_sha256(x) for x in (s,c,r)]==before


def test_no_mc_espn_writes_or_score_addition():
    source=(ROOT/'tools/operations/action_portfolio_b2b2.py').read_text()
    for forbidden in ('requests.', 'subprocess.run(', 'evaluate_roster_predictive(',
                      'evaluate_trade(', 'send_trade(', 'execute_native'):
        assert forbidden not in source


def test_cli_output_must_be_under_private_runtime_data(tmp_path,capsys):
    import json
    s,c,r=setup()
    paths=[]
    for key,obj in (('snapshot',s),('capture',c),('receipt',r),('league',league())):
        p=tmp_path/(key+'.json');p.write_text(json.dumps(obj))
        paths.extend(('--'+key,str(p)))
    out=tmp_path/'public_result.json'
    assert m.main(paths+['--out',str(out)])==3
    assert not out.exists()
    assert 'PRIVATE_RUNTIME_DATA_OUTPUT_ONLY' in capsys.readouterr().out


def test_structural_option_frontier_truncation_refused(monkeypatch):
    s,c,r=setup()
    original=m.build_frontier
    def truncated(*args,**kwargs):
        result=original(*args,**kwargs)
        result['offers'][0]['structural_options_truncated']=True
        return result
    monkeypatch.setattr(m,'build_frontier',truncated)
    with pytest.raises(m.CertificationBlocked,match='STRUCTURAL_OPTION_FRONTIER_TRUNCATED'):
        m.audit(s,c,r,league())
