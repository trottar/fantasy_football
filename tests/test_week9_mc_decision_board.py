"""Week 9 ranked MC decision board: deterministic, provider-free business checks."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path


def module(path: Path):
    s=importlib.util.spec_from_file_location('weekly_mc_decision_board_test',path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    return m


NOW=datetime(2026,11,2,20,tzinfo=timezone.utc)


def fake(week=9):
    return {'week':week,'native_overall':'COMPLETE / ACTION_REQUIRED','trial_state':'INCOMPLETE_COVERAGE',
            'review_blocker':'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED',
            'channels':[{'name':x,'status':'PASS / ACTION'} for x in (
                'lineup_availability','player_waiver_free_agent', 'dst_waiver_free_agent',
                'kicker_waiver_free_agent','ir_reserve_open_slot_injury_replacement',
                'trade_one_for_one_player','trade_multi_player_unequal',
                'trade_specialist_inclusive','prospective_capture_provenance')],
            'lineup':[{'direction':'START','name':'QB Alpha','position':'QB','state':'PENDING_ESPN_EXACT_SLOT_CONFIRMATION'}],
            'review':[{'family':'IR','state':'CAPTURE_REQUIRED_OWNED_DRIFT'}],
            'candidates':[
                {'family':'player_waiver_free_agent','description':'ADD RB Target / DROP RB Low','score':0.18,'classification':'ACTIONABLE'},
                {'family':'player_waiver_free_agent','description':'ADD RB Backup / DROP RB Low','score':0.09,'classification':'ACTIONABLE'},
                {'family':'trade_specialist_inclusive','description':'DST A -> WR B','score':0.90,'classification':'ACTIONABLE_OFFER'},
                {'family':'dst_waiver_free_agent','description':'DST A -> DST B','classification':'CHANNEL_SPECIFIC'},
            ],
            'alternatives':[
                {'family':'WAIVERS','description':'ADD RB Target / DROP RB Low','score':0.18,'probability':0.35,'classification':'ACTIONABLE', 'interval_p16':0.02,'interval_p84':0.42},
                {'family':'FREEAGENT','description':'ADD RB Other / DROP RB Low','score':0.10,'classification':'CLOSE_CALL','probability':0.9},
                {'family':'trade_specialist_inclusive','description':'DST A -> WR B','score':0.90,'classification':'ACTIONABLE_OFFER'},
                {'family':'trade_multi_player_unequal','description':'Lost / not uniquely retained — do not act','score':20.0,'classification':'ACTIONABLE_OFFER'},
            ]}


def test_current_week_and_prior_week_historical():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    a=m.build_board(fake(),now=NOW)
    assert a['state']=='CURRENT_MC_LEADS_ESPN_UNVERIFIED'
    assert a['current_week'] is True and a['action_authority']=='NONE'
    assert all(x['state']!='RECOMMEND_FOR_APPROVAL' for x in a['items'])
    b=m.build_board(fake(8),now=NOW)
    assert b['state']=='SAVED_WEEK_NOT_CURRENT_DO_NOT_ACT'
    assert all(x['state']=='HISTORICAL_DO_NOT_ACT' for x in b['items'])


def test_priority_without_cross_channel_score_comparison():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    a=m.build_board(fake(),now=NOW)
    labels=[r['family'] for r in a['items']]
    assert labels[:2]==['LINEUP','IR']
    assert labels.index('TRADE_SPECIALIST')>labels.index('PLAYER')
    player=[x for x in a['items'] if x['family']=='PLAYER']
    assert player[0]['score']==.18 and player[1]['score']==.09
    assert a['ranking_method']=='SAFETY_FIRST_THEN_WITHIN_CHANNEL_MODEL_SCORE'
    assert all(x['family_label'] for x in a['items'])


def test_alternative_dedup_and_unsupported_identity():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    a=m.build_board(fake(),now=NOW)
    assert len([r for r in a['items'] if r['description']=='ADD RB Target / DROP RB Low'])==1
    merged = next(r for r in a['items'] if r['description']=='ADD RB Target / DROP RB Low')
    assert 'behavior probability 35%' in merged['detail']
    assert 'interval [+0.0200, +0.4200]' in merged['detail']
    assert len([r for r in a['items'] if r['description']=='DST A -> WR B'])==1
    assert all('not uniquely retained' not in r['description'] for r in a['items'])
    assert any(r['state']=='MODEL_ALTERNATIVE_NOT_RECOMMENDED' for r in a['items'])
    assert not any('Unavailable' in r['description'] for r in a['items'])


def test_missing_channel_cannot_become_roster_hold():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    d=fake();d['channels'][2]['status']='INCOMPLETE_COVERAGE:DST_WAIVERS'
    d['candidates']=[];d['alternatives']=[];d['lineup']=[];d['review']=[]
    a=m.build_board(d,now=NOW)
    assert a['state']=='CURRENT_MC_INCOMPLETE_REVIEW_ONLY'
    assert 'dst_waiver_free_agent' in a['channel_gaps']
    assert any(x['family']=='DST' and x['state']=='COVERAGE_GAP' for x in a['items'])


def test_absent_matrix_and_zero_candidates_not_complete():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    d=fake();d['channels']=d['channels'][:8];d['candidates']=[];d['alternatives']=[];d['lineup']=[];d['review']=[]
    a=m.build_board(d,now=NOW)
    assert 'NINE_CHANNEL_MATRIX_MISSING_OR_DUPLICATE' in a['channel_gaps']
    assert a['state']=='CURRENT_MC_INCOMPLETE_REVIEW_ONLY'
    d=fake();d['candidates']=[];d['alternatives']=[];d['lineup']=[];d['review']=[]
    b=m.build_board(d,now=NOW)
    assert b['state']=='CURRENT_MC_NO_RETAINED_CANDIDATES_NOT_ROSTER_WIDE_HOLD'


def test_non_finite_or_invalid_scores_are_not_ranked():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    d=fake();d['candidates'].extend([
        {'family':'player_waiver_free_agent','description':'ADD WR Foo / DROP RB Low','score':float('nan'),'classification':'ACTIONABLE'},
        {'family':'trade_one_for_one_player','description':'QB A -> WR B','score':float('inf'),'classification':'ACTIONABLE_OFFER'},
    ])
    b=m.build_board(d,now=NOW)
    assert all(r['score'] is None for r in b['items'] if r['description'] in ('ADD WR Foo / DROP RB Low','QB A -> WR B'))
    assert 'nan' not in m.format_board(b).lower() and 'inf' not in m.format_board(b).lower().replace('information','')


def test_tuesday_week_boundary_dst_convention():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    assert m.week_at(datetime(2026,11,2,4,59,tzinfo=timezone.utc))==8
    assert m.week_at(datetime(2026,11,2,5,0,tzinfo=timezone.utc))==9
    assert m.week_at(datetime(2026,10,26,4,tzinfo=timezone.utc))==8


def test_output_bounded_and_no_private_provider_access():
    m=module(Path(__file__).resolve().parents[1]/'src/gui/weekly_mc_decision_board.py')
    b=m.build_board(fake(),now=NOW)
    txt=m.format_board(b,limit=3)
    assert txt.count('#')==3 and 'ESPN_ACTION_AUTHORITY=NONE' in txt
    assert 'REQUESTS' not in m.__doc__.upper()
