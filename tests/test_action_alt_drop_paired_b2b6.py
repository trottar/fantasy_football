"""Synthetic no-network regression for conditional matched-state B2b6 evidence."""
import copy
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

OPERATIONS = Path(__file__).resolve().parents[1] / 'tools' / 'operations'
if OPERATIONS.is_dir() and str(OPERATIONS) not in sys.path:
    sys.path.insert(0, str(OPERATIONS))
import action_alt_drop_paired_b2b6 as b2
import action_frontier as frontier

OFFER='a'*24


def fixtures(monkeypatch, *, options=2, change_fill=False, partner_blockers=None):
    opts=[]
    for i in range(options):
        opts.append({'drop_ids':[i+10], 'native_selected_normalization':i==0,
                     'feasibility_evidence':[]})
    offer={'offer_id':OFFER, 'partner_team_id':8,
           'modeled_native_auto_drop_ids':[10], 'structural_options_truncated':False,
           'structural_options':opts}
    monkeypatch.setattr(frontier, 'build_frontier',
                        lambda *args: {'offers':[copy.deepcopy(offer)]})
    monkeypatch.setattr(b2,'partner_drop_proof',
                        lambda *args: list(partner_blockers or []))
    def provider(_snapshot,_capture,_receipt,_league,_oid,drops):
        opt=next(o for o in opts if o['drop_ids']==drops)
        fill_id=800 + (1 if change_fill and drops!=[10] else 0)
        branches=[{'fill_outcomes':[{'side':'user','id':fill_id,'conditional_success':ok}],
                   'unresolved':['FUTURE_FILL_AT_PROCESSING_UNVERIFIED:user'] if ok else [],
                   'user':{'frozen_static_constraints_pass':True},
                   'partner':{'frozen_static_constraints_pass':True}}
                  for ok in (False,True)]
        return ({'offer_id':OFFER}, {'offer_id':OFFER},
                {'drop_ids':drops,'branches':branches})
    frozen=({'snapshot_utc':'2026-10-28T19:00:00+00:00'}, {}, {'team_id':7}, {}, {})
    return frozen,provider,opts


def kernel(_snapshot,_league,_model,_values,_offer,opt,branch,user,scenarios,_runtime,cache):
    ids=opt['drop_ids']
    modifier=(0.4 if ids==[10] else 1.5)
    modifier+=0.3 if branch['fill_outcomes'][0]['conditional_success'] else 0.0
    base=np.arange(scenarios,dtype=float)/10
    return {user:(base,base+modifier),8:(base,base+modifier/2)},({} if cache is None else cache)


def run(monkeypatch,**kwargs):
    frozen,provider,opts=fixtures(monkeypatch,**kwargs)
    return b2.evaluate(*frozen,Path('/tmp/values'),Path('/tmp/runtime'),OFFER,
                       scenarios=32,kernel=kernel,frontier_provider=provider)


def test_matched_future_fill_and_native_reference(monkeypatch):
    report=run(monkeypatch)
    assert report['certified_actions']==0 and report['espn_action_authority']=='NONE'
    assert report['conditional_cases_total']==4 and report['native_mc_cases_evaluated']==4
    alt=[x for x in report['options'] if x['drop_ids']==[11] and not x['hypothetical_future_fill']][0]
    assert alt['hold_comparison']['user']['paired_delta_mean']==pytest.approx(1.5)
    assert alt['versus_native_drop_same_fill_state']['user']['paired_delta_mean']==pytest.approx(1.1)
    assert alt['versus_native_drop_same_fill_state']['partner']['paired_delta_mean']==pytest.approx(.55)
    assert alt['hold_comparison']['user']['paired_mean_interval_p16']==pytest.approx(1.5)
    assert alt['hold_comparison']['user']['paired_mean_interval_p84']==pytest.approx(1.5)
    assert all(x['state'].startswith('CONDITIONAL_MC_') for x in report['options'])
    assert all(x['future_fill_probability']=='UNKNOWN' for x in report['options'])
    assert report['comparisons_crossing_fill_states']=='PROHIBITED'


def test_result_determinism_and_does_not_modify_inputs(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch)
    source=copy.deepcopy(frozen)
    args=(*frozen,Path('/tmp/value'),Path('/tmp/runtime'),OFFER)
    a=b2.evaluate(*args,kernel=kernel,frontier_provider=provider)
    c=b2.evaluate(*args,kernel=kernel,frontier_provider=provider)
    assert a==c and source==frozen


def test_mismatched_fill_lattice_is_blocked(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch,change_fill=True)
    with pytest.raises(b2.CertificationBlocked,match='FILL_STATES_DIFFER'):
        b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,kernel=kernel,frontier_provider=provider)


def test_partner_permission_blocked_without_running_kernel(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch,partner_blockers=['PARTNER_DROP_UNVERIFIED'])
    def forbidden(*_args):
        raise AssertionError('native kernel must not run')
    report=b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,
                       kernel=forbidden,frontier_provider=provider)
    assert report['native_mc_cases_evaluated']==0
    assert all('PARTNER_DROP_UNVERIFIED' in x['blockers'] for x in report['options'])


def test_missing_native_reference_fails_closed(monkeypatch):
    frozen,provider,opts=fixtures(monkeypatch)
    opts[0]['native_selected_normalization']=False
    with pytest.raises(b2.CertificationBlocked,match='NATIVE_DROP_REFERENCE'):
        b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,kernel=kernel,frontier_provider=provider)


def test_offer_not_in_frozen_frontier(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch)
    with pytest.raises(b2.CertificationBlocked,match='OFFER_NOT_UNIQUE_OR_MISSING'):
        b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),'b'*24,kernel=kernel,frontier_provider=provider)


def test_invalid_mc_shape_blocks_only_case(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch)
    def wrong_shape(*args):
        return {7:(np.ones(2),np.ones(2)),8:(np.ones(2),np.ones(2))},{}
    report = b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,
                         kernel=wrong_shape,frontier_provider=provider)
    assert report['native_mc_cases_evaluated']==0
    assert all('B2B6_PAIRED_RESPONSE_SHAPE_OR_FINITE_INVALID' in x['blockers']
               for x in report['options'])


def test_option_budget_and_scenario_budget(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch,options=25)
    with pytest.raises(b2.CertificationBlocked,match='DROP_OPTIONS_EXCEED_BUDGET'):
        b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,kernel=kernel,frontier_provider=provider)
    with pytest.raises(b2.CertificationBlocked,match='SCENARIO_BUDGET'):
        b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,scenarios=8,kernel=kernel,frontier_provider=provider)


def test_source_guard_requires_exact_predecessor(tmp_path):
    root=tmp_path/'fantasy_football'
    root.mkdir()
    with pytest.raises(b2.CertificationBlocked,match='DEPENDENCY_SOURCE_DRIFT'):
        b2.check_source(root)


def test_changed_baseline_blocks_comparison(monkeypatch):
    frozen,provider,_=fixtures(monkeypatch)
    def unstable(*args):
        response,cache=kernel(*args)
        if args[6]['fill_outcomes'][0]['conditional_success']:
            response[7]=(response[7][0]+1,response[7][1])
        return response,cache
    report=b2.evaluate(*frozen,Path('/tmp/a'),Path('/tmp/b'),OFFER,
                       kernel=unstable,frontier_provider=provider)
    assert report['native_mc_cases_evaluated'] == 2
    assert sum('B2B6_COMMON_BASELINE_SCENARIO_AXIS_DRIFT' in x['blockers']
               for x in report['options']) == 2
