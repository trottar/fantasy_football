"""Targeted, network-free regressions for the Week 7 MC guard ownership/bye defect."""
from __future__ import annotations
import importlib.util
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/operations/guarded_weekly_cycle.py'
spec=importlib.util.spec_from_file_location('corrected_guard_under_test',SOURCE)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
NOW=datetime(2026,10,24,16,20,tzinfo=timezone.utc)


def example(bye_team='BUF',bye_kickoff=None,owner=1):
    rows=[{'espn_id':i+100,'side':'LEAGUE','fantasy_team_id':owner,
           'nfl_team':'NYJ','position':'WR',
           'kickoff_utc':(NOW+timedelta(hours=20)).isoformat()} for i in range(13)]
    rows.append({'espn_id':130,'side':'LEAGUE','fantasy_team_id':owner,
                 'nfl_team':bye_team,'position':'WR','kickoff_utc':bye_kickoff})
    specialists=[{'espn_id':200,'position':'DST','owner_team_id':1,'nfl_team':'NYJ',
                  'kickoff_utc':(NOW-timedelta(hours=4)).isoformat()},
                 {'espn_id':201,'position':'K','owner_team_id':1,'nfl_team':'NYJ',
                  'kickoff_utc':(NOW+timedelta(hours=22)).isoformat()}]
    cap={'team_id':1,'week':7,'season':2026,
         'league_player_predictions':{'records':rows},
         'specialist_predictions':{'records':specialists}}
    snapshot={'espn':{'week':7,'season':2026},'matchup_context':{
        'team_week':{'BUF':{},'NYJ':{'7':{'opponent':'NE'}}}}}
    league={'bye_weeks_2026':{'BUF':7,'NYJ':13}}
    official={'BUF':7,'NYJ':13}
    return cap,snapshot,league,official


def check(cap,snapshot,league,official):
    return g._lock_candidates(cap,NOW,snapshot=snapshot,league=league,official_byes=official)


def test_full_14_player_two_specialist_ownership_and_exact_bye():
    args=example()
    result=check(*args)
    assert result['owned_records']==16
    assert result['owned_players']==14 and result['owned_specialists']==2
    assert result['verified_owned_byes']==1
    assert result['deadline']==NOW+timedelta(hours=20)
    assert result['expired_records']==1


def test_player_owner_is_fantasy_team_id_not_side():
    cap,s,l,o=example(owner=2)
    with pytest.raises(g.Blocked,match='OWNED_PLAYER_COVERAGE_MISSING'):
        check(cap,s,l,o)


def test_team_id_beats_misleading_side_us():
    cap,s,l,o=example(owner=2)
    cap['league_player_predictions']['records'][0]['side']='US'
    with pytest.raises(g.Blocked,match='OWNED_PLAYER_COVERAGE_MISSING'):
        check(cap,s,l,o)


@pytest.mark.parametrize('kind', ['official','configured','schedule','week','season','team','kickoff'])
def test_absent_kickoff_needs_independent_three_way_bye_proof(kind):
    cap,s,l,o=example()
    if kind=='official':o['BUF']=8
    elif kind=='configured':l['bye_weeks_2026']['BUF']=8
    elif kind=='schedule':s['matchup_context']['team_week']['BUF']['7']={'opponent':'NYJ'}
    elif kind=='week':s['espn']['week']=8
    elif kind=='season':s['espn']['season']=2025
    elif kind=='team':cap['league_player_predictions']['records'][-1]['nfl_team']='LAC'
    elif kind=='kickoff':cap['league_player_predictions']['records'][-1]['kickoff_utc']='invalid'
    if kind=='kickoff':
        # An invalid kickoff is still a missing known lock unless proven a bye;
        # a *real* bye with no scheduled match remains acceptable.
        assert check(cap,s,l,o)['verified_owned_byes']==1
    else:
        with pytest.raises(g.Blocked,match='UNKNOWN_OWNED_PLAYER_LOCK'):
            check(cap,s,l,o)


def test_missing_kickoff_non_bye_denied():
    cap,s,l,o=example()
    cap['league_player_predictions']['records'][-1]['nfl_team']='NYJ'
    with pytest.raises(g.Blocked,match='UNKNOWN_OWNED_PLAYER_LOCK'):
        check(cap,s,l,o)


def test_specialist_unknown_kickoff_is_not_a_bye():
    cap,s,l,o=example()
    cap['specialist_predictions']['records'][1]['kickoff_utc']=None
    with pytest.raises(g.Blocked,match='UNKNOWN_OWNED_PLAYER_LOCK'):
        check(cap,s,l,o)


def test_no_owned_future_game_rejects():
    cap,s,l,o=example()
    for row in cap['league_player_predictions']['records'][:13]:
        row['kickoff_utc']=(NOW-timedelta(minutes=1)).isoformat()
    cap['specialist_predictions']['records'][1]['kickoff_utc']=(NOW-timedelta(minutes=1)).isoformat()
    with pytest.raises(g.Blocked,match='NO_UNLOCKED_OWNED_ASSETS'):
        check(cap,s,l,o)


def test_missing_league_schema_owner_rejected():
    cap,s,l,o=example()
    cap['league_player_predictions']['records'][0].pop('fantasy_team_id')
    with pytest.raises(g.Blocked,match='LEAGUE_PLAYER_OWNER_ID_MISSING'):
        check(cap,s,l,o)


def test_prior_readonly_bug_cannot_return_just_specialists():
    cap,s,l,o=example()
    assert check(cap,s,l,o)['owned_records'] != 2


def test_official_bye_table_matches_published_readonly_source():
    src=(ROOT/'tools/operations/weekly_operator_calendar_evidence.py')
    if not src.exists():
        pytest.skip('Only local control-root source checkout provides the published official table')
    assert g._source_bound_official_byes(ROOT)['BUF']==7


def test_legacy_direct_helper_fixture_without_week_does_not_weaken_live_inspect():
    # The published test_guarded_weekly_cycle.py uses a compact direct-call
    # fixture without week. Production inspect passes snapshot and must not.
    cap,snapshot,league,official = example()
    cap['league_player_predictions']['records'].pop()
    cap.pop('week')
    report = g._lock_candidates(cap,NOW)
    assert report['owned_players'] == 13 and report['owned_specialists'] == 2
    with pytest.raises(g.Blocked,match='CAPTURE_WEEK_INVALID'):
        check(cap,snapshot,league,official)
