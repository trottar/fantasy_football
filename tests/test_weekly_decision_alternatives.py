from __future__ import annotations
import unittest
from src.weekly_decision_alternatives import player_alternatives, trade_alternatives, LIMIT_PER_CLASS


class AlternativesTests(unittest.TestCase):
    def test_player_unchanged_decisions_and_bounded_ranked_rejected(self):
        report={'candidate_pool_evaluated':80,'screen_actions_total':50,'predictive_actions_evaluated':8,
                'predictive_actions_final_stage':2,'free_agent_actions':[
                    {'add_name':'B','drop_name':'C','combined_action_classification':'NO_RESOLVED_EDGE',
                     'expected_delta_utility':-.02,'mc_stage':'SCREEN1','mc_futility_stop':True,'mc_scenarios':1024},
                    {'add_name':'A','drop_name':'D','combined_action_classification':'POSSIBLE_EDGE',
                     'expected_delta_utility':.009,'p_acquire':1.0,'delta_total_utility_p16':-.001,
                     'delta_total_utility_p84':.02,'mc_stage':'FINAL','mc_scenarios':16384}],
                'waiver_actions':[{'add_name':'W','drop_name':'D','combined_action_classification':'NO_RESOLVED_EDGE',
                                   'expected_delta_utility':-.01,'p_acquire':.4}]}
        before=repr(report)
        x=player_alternatives(report)
        self.assertEqual(repr(report),before)
        self.assertEqual(x['candidate_pool_preselected'],80)
        self.assertEqual(x['predictive_actions_evaluated'],8)
        self.assertEqual(x['groups'][0]['alternatives'][0]['add'],'A')
        self.assertEqual(x['groups'][0]['alternatives'][0]['classification'],'POSSIBLE_EDGE')
        self.assertEqual(x['groups'][0]['alternatives'][1]['mc_stage'],'SCREEN1')
        self.assertEqual(x['groups'][1]['alternatives'][0]['p_acquire'],.4)
        self.assertTrue(all(z['transaction_authority']=='NONE' for g in x['groups'] for z in g['alternatives']))
    def test_player_no_evaluated_rows_does_not_fabricate(self):
        x=player_alternatives({'candidate_pool_evaluated':80,'predictive_actions_evaluated':0})
        self.assertEqual(sum(g['retained_count'] for g in x['groups']),0)
    def test_trade_bounded_and_native_class_untouched(self):
        rows=[{'give_name':f'G{i}','receive_name':f'R{i}', 'partner_name':'Partner',
               'classification':'OUR_EDGE_PARTNER_LOSS','expected_offer_value': i/100,
               'p_accept':.01*i,'our_delta_season_ppg':.03*i,'partner_delta_season_ppg':-.02*i,'mc_scenarios':4096} for i in range(12)]
        before=repr(rows)
        x=trade_alternatives(rows,family='1x1')
        self.assertEqual(repr(rows),before)
        self.assertEqual(x['native_reported_count'],12)
        self.assertEqual(x['retained_count'],LIMIT_PER_CLASS)
        self.assertEqual(x['alternatives'][0]['give'],'G11')
        self.assertEqual(x['alternatives'][0]['classification'],'OUR_EDGE_PARTNER_LOSS')
        self.assertAlmostEqual(x['alternatives'][0]['our_delta_season_ppg'],.33)
        self.assertAlmostEqual(x['alternatives'][0]['partner_delta_season_ppg'],-.22)
        self.assertTrue(x['truncated'])
    def test_untrusted_numeric_fields_never_become_nonfinite(self):
        x=trade_alternatives([{'expected_offer_value':float('nan'),'p_accept':float('inf'),
                               'classification':'ACTIONABLE_OFFER'}],family='1x1')
        self.assertIsNone(x['alternatives'][0]['expected_offer_value'])
        self.assertIsNone(x['alternatives'][0]['p_accept'])
        self.assertEqual(x['authority'],'OBSERVATION_ONLY')
    def test_missing_native_class_is_not_promoted(self):
        x=player_alternatives({'free_agent_actions':[{'expected_delta_utility':.01}]})
        self.assertEqual(x['groups'][0]['alternatives'][0]['classification'],'UNCLASSIFIED_NATIVE_ROW')
        self.assertEqual(x['groups'][0]['alternatives'][0]['transaction_authority'],'NONE')



import hashlib,json,tempfile
from pathlib import Path
from src.gui.weekly_decision_view import _verified_bye, collect, DecisionViewBlocked

class ViewTests(unittest.TestCase):
 def test_verified_bye_accepts_missing_and_null_but_not_game(self):
  n={'team_id':3}
  s={'espn':{'season':2026,'week':8,'teams':[{'team_id':3,'roster':[{'name':'George Kittle','nfl_team':'SF'}]}]},
     'matchup_context':{'team_week':{'SF':{}}}}
  l={'bye_weeks_2026':{'SF':8}};off={'SF':8}
  self.assertTrue(_verified_bye('George Kittle',week=8,native=n,snapshot=s,league=l,official=off))
  s['matchup_context']['team_week']['SF']['8']=None
  self.assertTrue(_verified_bye('George Kittle',week=8,native=n,snapshot=s,league=l,official=off))
  s['matchup_context']['team_week']['SF']['8']={'opponent':'NO'}
  self.assertFalse(_verified_bye('George Kittle',week=8,native=n,snapshot=s,league=l,official=off))
  self.assertFalse(_verified_bye('George Kittle',week=8,native=n,snapshot=s,league={},official=off))
 def test_existing_and_future_receipt_presentation(self):
  with tempfile.TemporaryDirectory() as td:
   runtime=Path(td)/'fantasy_season_v0_36_repack1';runtime.mkdir()
   (runtime/'VERSION').write_text('0.36')
   folder=runtime/'data/season_decisions';folder.mkdir(parents=True)
   (runtime/'data/season_snapshots').mkdir();(runtime/'config').mkdir()
   (runtime/'data/season_snapshots/latest.json').write_text(json.dumps({'espn':{'season':2026,'week':8,'teams':[]}}))
   (runtime/'config/league.json').write_text('{}')
   channels=[{'key':k,'status':'PASS / HOLD:TEST','evidence':{}} for k in (
       'lineup_availability','player_waiver_free_agent','dst_waiver_free_agent','kicker_waiver_free_agent',
       'ir_reserve_open_slot_injury_replacement','trade_one_for_one_player',
       'trade_multi_player_unequal','trade_specialist_inclusive','prospective_capture_provenance')]
   channels[1]['evidence']={'candidate_pool_evaluated':80,'evaluated_alternatives':{
      'authority':'OBSERVATION_ONLY','groups':[{'acquisition_state':'FREEAGENT','alternatives':[
         {'add':'Test Candidate','drop':'Test Drop','classification':'NO_RESOLVED_EDGE',
          'expected_delta_utility':-.01,'p_acquire':1.0,'mc_stage':'SCREEN1','futility_stop':True}]}]}}
   channels[5]['evidence']={'evaluated_reported':2,'evaluated_alternatives':{
      'authority':'OBSERVATION_ONLY','alternatives':[{'give':'A','receive':'B',
            'classification':'OUR_EDGE_PARTNER_LOSS','expected_offer_value':-.04,'p_accept':.2}]}}
   native={'season':2026,'week':8,'overall_state':'COMPLETE / NO_ACTION','team_id':3,'operational_health':{'status':'PASS'},'channels':channels}
   receipt=folder/'weekly_decision_receipt_fixture.json';receipt.write_text(json.dumps(native));sha=hashlib.sha256(receipt.read_bytes()).hexdigest()
   prefix='operator_v2_trial_2026_w08_TUE_20261027'
   (folder/(prefix+'.report.json')).write_text(json.dumps({'season':2026,'week':8,'commissioning_trial':True,'transaction_authority':'NONE',
     'espn_writes':False,'completed_phases':['CALENDAR','SYNC','CAPTURE','MC','REVIEW'],'operator_state':'INCOMPLETE_COVERAGE','queue':[]}))
   (folder/(prefix+'.mc.done.json')).write_text(json.dumps({'facts':{'receipt_sha256':sha}}))
   x=collect(runtime)
   self.assertTrue(x['alternatives_available']);self.assertEqual(len(x['alternatives']),2)
   self.assertIn('Test Candidate',x['alternatives'][0]['description'])
   self.assertFalse(any(z['certified'] for z in x['alternatives']))
   channels[1]['evidence'].pop('evaluated_alternatives');channels[5]['evidence'].pop('evaluated_alternatives')
   receipt.write_text(json.dumps(native));sha=hashlib.sha256(receipt.read_bytes()).hexdigest()
   (folder/(prefix+'.mc.done.json')).write_text(json.dumps({'facts':{'receipt_sha256':sha}}))
   old=collect(runtime);self.assertFalse(old['alternatives_available']);self.assertEqual(old['alternatives'],[])
