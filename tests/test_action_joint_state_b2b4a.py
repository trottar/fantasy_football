"""B2b4a ordered frozen portfolio: synthetic independent state-transition tests."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import types

import pytest

PATH = Path(__file__).resolve().parents[1] / 'tools/operations/action_joint_state_b2b4a.py'


def fixtures(monkeypatch, *, conflict=False, duplicate_fill=False, unsafe_drop=False):
    def person(pid,team,*,drop=True,pos='RB'):
        return {'espn_id':pid,'on_team_id':team,'position':pos,'fantasy_status':'ROSTERED',
                'lineup_locked':False,'droppable':drop}
    s={'espn':{'season':2026,'week':8,'teams':[
        {'team_id':1,'roster':[person(11,1),person(12,1),person(13,1)]},
        {'team_id':2,'roster':[person(21,2),person(22,2),person(23,2)]},
        {'team_id':3,'roster':[person(31,3),person(32,3),person(33,3)]}],
        'available_players':[{'espn_id':41,'position':'RB','fantasy_status':'FREEAGENT'}]}}
    league={'roster':{x:0 for x in ('QB','RB','WR','TE','DST','K')},
            'position_maximums':{x:10 for x in ('QB','RB','WR','TE','DST','K')}}
    one={'offer_id':'A','partner_team_id':2,'give_ids':[11,12], 'receive_ids':[21],
         'modeled_partner_auto_drop_ids':[23],
         'structural_options':[{'drop_ids':[], 'feasibility_evidence':[],
                                'native_selected_normalization':True}],
         'structural_options_truncated':False}
    two={'offer_id':'B','partner_team_id':3,'give_ids':[11 if conflict else 13],
         'receive_ids':[31], 'modeled_partner_auto_drop_ids':[],
         'structural_options':[{'drop_ids':[], 'feasibility_evidence':[
                 'FROZEN_ESPN_DROPPABLE_NOT_TRUE'] if unsafe_drop else [],
                 'native_selected_normalization':True}],
         'structural_options_truncated':False}
    def branch(success, asset=41):
        return {'fill_outcomes':[{'side':'user','id':asset,
               'conditional_success':success,'materialized_from_frozen_market':success}],
               'unresolved':['FUTURE_FILL_AT_PROCESSING_UNVERIFIED:user'] if success else []}
    st=[{'offer_id':'A','options':[{'drop_ids':[],'branches':[branch(False),branch(True)]}]},
        {'offer_id':'B','options':[{'drop_ids':[],
             'branches':[branch(False,41),branch(True,41)] if duplicate_fill else [
               {'fill_outcomes':[],'unresolved':[]}]}]}]
    mods={
        'action_frontier':{'build_frontier':lambda *a:{'offer_count':2,'offers':[one,two]},
            'canonical_sha256':lambda x:hashlib.sha256(repr(x).encode()).hexdigest(),
            'CertificationBlocked':ValueError},
        'action_portfolio_b2b2':{
            'audit':lambda *a:{'offer_count':2,'offers':st},
            '_league':lambda l:(l['roster'],l['position_maximums']),
            '_owned':lambda t:{p['espn_id']:p for p in t['roster']},
            '_state':lambda r,target,mn,mx:{'frozen_static_constraints_pass':len(r)<=target},
            '_available':lambda v:{p['espn_id']:p for p in v['espn']['available_players']},
            'POSITIONS':frozenset(('QB','RB','WR','TE','DST','K'))}}
    for name,attr in mods.items():
        module=types.ModuleType(name);module.__dict__.update(attr)
        monkeypatch.setitem(sys.modules,name,module)
    spec=importlib.util.spec_from_file_location('b2b4a_test_target',PATH)
    tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
    return tool, (s,{'frozen':True},{'team_id':1},league)


def audit(mod,docs):return mod.audit(*docs,'A','B',[],[])


def test_both_sequences_reconcile_real_ownership_and_released_field(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    orig=copy.deepcopy(docs)
    result=audit(mod,docs)
    assert result['orders']==2
    assert result['branch_pairs_per_order']==2
    assert len(result['cases'])==4
    assert all(case['state']=='CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED' for case in result['cases'])
    for case in result['cases']:
        assert case['released_to_field_ids']==[23]
        assert set(case['final_owned_ids_by_team']['1']) in ({21,31},{21,31,41})
        assert 23 in case['final_market_asset_ids']
        assert case['joint_football_utility']=='NOT_COMPUTED'
        assert case['conditional_fill_joint_probability']=='UNKNOWN'
        assert case['espn_action_authority']=='NONE'
    assert docs==orig
    assert result['certified_actions']==0


def test_shared_given_asset_cannot_be_two_independent_trades(monkeypatch):
    mod,docs=fixtures(monkeypatch,conflict=True)
    result=audit(mod,docs)
    assert result['cases_conditional_static_pass']==0
    assert all(case['state']=='BLOCKED' for case in result['cases'])
    assert all('SEQUENTIAL_TRADE_PARTICIPANT_OWNERSHIP_CHANGED' in case['blockers']
               for case in result['cases'])


def test_unknown_drop_permission_is_fail_closed(monkeypatch):
    mod,docs=fixtures(monkeypatch,unsafe_drop=True)
    with pytest.raises(ValueError, match='B2B4A_FROZEN_DROP_PERMISSION_BLOCKED'):
        audit(mod,docs)


def test_duplicate_acquisition_must_not_be_factored_independently(monkeypatch):
    mod,docs=fixtures(monkeypatch,duplicate_fill=True)
    with pytest.raises(ValueError, match='SHARED_FUTURE_FILL_REQUIRES_COUPLED_ACQUISITION_STATE'):
        audit(mod,docs)


def test_hypothetical_required_fill_is_not_guaranteed(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    got,assumptions,blockers=mod._evidence({'fill_outcomes':[],
        'unresolved':['FUTURE_USER_FILL_REQUIRED_NO_GUARANTEE','FUTURE_USER_FILL_ASSUMPTION']})
    assert got==[] and not blockers
    assert len(assumptions)==2


def test_wrong_source_fill_does_not_make_a_free_agent(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    docs[0]['espn']['available_players'][0]['fantasy_status']='WAIVERS'
    result=audit(mod,docs)
    assert sum(x['state']=='BLOCKED' for x in result['cases'])==2
    assert sum(x['state'].startswith('CONDITIONAL_') for x in result['cases'])==2
    assert all('CONDITIONAL_FILL_NOT_FROZEN_FREEAGENT_OR_ALREADY_CONSUMED' in x['blockers']
               for x in result['cases'] if x['state']=='BLOCKED')


def test_all_branch_outcomes_must_be_boolean_and_source_materialized(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    branch={'fill_outcomes':[{'side':'user','id':41,'conditional_success':1,
                              'materialized_from_frozen_market':True}], 'unresolved':[]}
    with pytest.raises(ValueError,match='B2B4A_MALFORMED_FILL_OUTCOME'):
        mod._evidence(branch)
    branch['fill_outcomes'][0]['conditional_success']=True
    branch['fill_outcomes'][0]['materialized_from_frozen_market']=False
    with pytest.raises(ValueError,match='FROZEN_FREEAGENT_IDENTITY_NOT_PROVEN'):
        mod._evidence(branch)


def test_immutable_input_guard_detects_an_adversarial_dependency(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    normal=mod._state
    def mutate(rows,target,mi,ma):
        docs[0]['espn']['week']=9
        return normal(rows,target,mi,ma)
    mod._state=mutate
    with pytest.raises(ValueError,match='B2B4A_FROZEN_INPUT_MUTATED'):
        audit(mod,docs)


def test_same_offer_and_malformed_selection_rejected(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    with pytest.raises(ValueError,match='B2B4A_DISTINCT_OFFER_IDS_REQUIRED'):
        mod.audit(*docs,'A','A',[],[])
    with pytest.raises(ValueError,match='B2B4A_EXPLICIT_DROP_IDS_INVALID'):
        mod.audit(*docs,'A','B',[13,13],[])
    with pytest.raises(ValueError,match='B2B4A_DROP_OPTION_NOT_UNIQUE_OR_MISSING'):
        mod.audit(*docs,'A','B',[13],[])


def test_no_live_mc_or_automatic_transaction_route():
    src=PATH.read_text(encoding='utf-8')
    assert 'NATIVE_MC=NONE' in src and 'ACTION_AUTHORITY=NONE' in src
    for forbidden in ('requests.post(', 'fetch_private_league(', 'subprocess.run(',
                      'create_trade(', '--execute-native', 'os.system('):
        assert forbidden not in src


def test_invalid_partner_step_does_not_commit_a_partial_trade(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    owners,market=mod._frozen_state(docs[0])
    original=copy.deepcopy((owners,market))
    offer={'offer_id':'A','partner_team_id':2,'give_ids':[11,12],
           'receive_ids':[21],'modeled_partner_auto_drop_ids':[23]}
    branch={'fill_outcomes':[],'unresolved':[]}
    # A frozen min/max evaluator failure on the partner must leave both original.
    def fail_partner(rows,target,mn,mx):
        return {'frozen_static_constraints_pass':not (21 not in rows and 11 in rows)}
    mod._state=fail_partner
    with pytest.raises(ValueError,match='PARTNER_SEQUENTIAL_STATIC_ROSTER_ILLEGAL'):
        mod._apply(owners,market,offer,{'drop_ids':[]},branch,1,
                   {1:3,2:3,3:3},docs[3]['roster'],docs[3]['position_maximums'])
    assert (owners,market)==original


def test_missing_market_frozen_identity_blocks_branch(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    docs[0]['espn']['available_players']=[]
    result=audit(mod,docs)
    assert result['cases_conditional_static_pass']==2
    assert all(x['state']=='BLOCKED' for x in result['cases'] if x['fill_states'][0]['success_ids'])


def test_branch_limit_is_rejected_without_thinning(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    prior=mod.structural_audit
    def expanded(*args):
        report=copy.deepcopy(prior(*args))
        report['offers'][0]['options'][0]['branches'] *= 17
        return report
    mod.structural_audit=expanded
    with pytest.raises(ValueError,match='B2B4A_FILL_LATTICE_NOT_EXHAUSTIVE'):
        audit(mod,docs)


def test_duplicate_boolean_branch_is_not_treated_as_complete(monkeypatch):
    mod,docs=fixtures(monkeypatch)
    branch={'fill_outcomes':[{'side':'user','id':41,'conditional_success':False}]}
    with pytest.raises(ValueError,match='B2B4A_FILL_LATTICE_DUPLICATE_OUTCOME'):
        mod._lattice_variables([branch,copy.deepcopy(branch)])
