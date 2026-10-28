"""Deterministic, synthetic presentation contract tests; no providers/MC."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path


def load(path: Path):
    spec = importlib.util.spec_from_file_location('test_week8_gui', str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_tests(path: Path):
    m=load(path)
    specialist={'give_names':['George Kittle', 'Chiefs D/ST'], 'receive_names':['Josh Allen'], 'classification':'ACTIONABLE_OFFER', 'package_family':'2x1', 'expected_offer_value':1.8112, 'p_accept':.855, 'our_delta_season_ppg':2.12, 'partner_delta_season_ppg':2.46}
    alt={'give':None,'receive':None, 'classification':'ACTIONABLE_OFFER','package_family':'2x1','expected_offer_value':1.8112,'p_accept':.855,'our_delta_season_ppg':2.12,'partner_delta_season_ppg':2.46}
    assert m._resolve_trade_assets('trade_specialist_inclusive',specialist,[specialist])==('George Kittle + Chiefs D/ST','Josh Allen')
    assert m._resolve_trade_assets('trade_specialist_inclusive',alt,[specialist])==('George Kittle + Chiefs D/ST','Josh Allen')
    assert m._resolve_trade_assets('trade_specialist_inclusive',alt,[specialist,specialist]) is None
    assert m._resolve_trade_assets('trade_specialist_inclusive',alt,[]) is None
    assert m._resolve_trade_assets('trade_specialist_inclusive',{**alt,'p_accept':.999},[specialist]) is None
    assert m._resolve_trade_assets('trade_multi_player_unequal',{'give':'Mark Andrews + Jacoby Brissett','receive':'Josh Allen'},[])==('Mark Andrews + Jacoby Brissett','Josh Allen')
    assert m._resolve_trade_assets('trade_multi_player_unequal',{'give_name':'Rashid Shaheed + George Kittle','receive_name':'Josh Allen'},[])==('Rashid Shaheed + George Kittle','Josh Allen')
    assert m._resolve_trade_assets('trade_specialist_inclusive',{**specialist,'give_names':['Good\nBad']},[]) is None
    # Native evidence parsing remains read-only and explicit about authority.
    with tempfile.TemporaryDirectory() as tmp:
        runtime=Path(tmp)
        (runtime/'VERSION').write_text('0.36\n')
        for p in ('data/season_snapshots/latest.json','config/league.json'):
            f=runtime/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps({'espn':{'week':8,'season':2026,'teams':[]}}))
        channels=[]
        for key in m.CHANNEL_ORDER:
            ch={'key':key,'status':'PASS / HOLD','evidence':{}}
            if key=='trade_specialist_inclusive':
                ch['status']='PASS / ACTION'
                ch['action']={'offers':[specialist]}
                ch['evidence']={'evaluated_alternatives':{'authority':'OBSERVATION_ONLY','alternatives':[alt]}}
            elif key=='trade_multi_player_unequal':
                ch['evidence']={'evaluated_alternatives':{'authority':'OBSERVATION_ONLY','alternatives':[{'give':'Mark Andrews','receive':'Josh Allen','classification':'OUR_EDGE_PARTNER_LOSS','p_accept':.2,'expected_offer_value':.1}]}}
            channels.append(ch)
        trial={'slot':'WED','created_utc':'2026-10-28T19:30:00+00:00','operator_state':'INCOMPLETE_COVERAGE','queue':[], 'blocker':'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED'}
        native={'season':2026,'week':8,'overall_state':'COMPLETE / ACTION_REQUIRED','team_id':1,'channels':channels}
        m._parse_trial=lambda _: (trial,native,'a'*64)
        result=m.collect(runtime)
        assert result['slot']=='WED' and result['observed_utc']==trial['created_utc']
        assert result['candidates'][0]['description']=='George Kittle + Chiefs D/ST -> Josh Allen'
        assert any(x['description']=='George Kittle + Chiefs D/ST -> Josh Allen' for x in result['alternatives'])
        assert any(x['description']=='Mark Andrews -> Josh Allen' for x in result['alternatives'])
        assert all(not x['certified'] for x in result['alternatives']+result['candidates'])
    assert 'requests' not in path.read_text() and 'urlopen' not in path.read_text()
    print('SYNTHETIC_WEDNESDAY_GUI_TESTS=PASS:9')

if __name__=='__main__':
    import sys
    run_tests(Path(sys.argv[1]))


def test_wednesday_native_specialist_display() -> None:
    run_tests(Path(__file__).resolve().parents[1] / 'src/gui/weekly_decision_view.py')
