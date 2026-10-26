"""B2b4d: ESPN source shapes are not certified processing events or action times."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import json

import pytest

PATH = (Path(__file__).resolve().parents[1] / 'tools/operations/'
        'weekly_operator_transaction_source_b2b4d.py')
spec = importlib.util.spec_from_file_location('b2b4d_isolated', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = datetime(2026,10,25,22,15,tzinfo=timezone.utc)


def fixture():
    snap = {'snapshot_utc':(NOW-timedelta(minutes=10)).isoformat(),
            'espn':{'season':2026,'week':8,'league_id':18}}
    txs = [{'id':101,'type':'TRADE','status':'EXECUTED',
            'proposedDate':1792965300000,'processDate':1792965500000,
            'items':[{'playerId':71,'fromTeamId':1,'toTeamId':2}]}]
    raw = {'id':18,'seasonId':2026,'scoringPeriodId':8,'transactions':txs,
           'settings':{'tradeSettings':{'revisionHours':48,'deadlineDate':100},
                       'acquisitionSettings':{'waiverProcessHour':12}}}
    return snap,raw


def classify(snap=None,raw=None,*,started=NOW,ended=NOW+timedelta(seconds=2),
             now=NOW+timedelta(seconds=2)):
    ss,rr=fixture()
    return m.summarize(frozen=ss if snap is None else snap,
                       raw=rr if raw is None else raw,
                       started=started,ended=ended,now=now,week=8)


def test_success_is_explicitly_not_event_or_cutoff_proof():
    snap,raw=fixture()
    before=copy.deepcopy((snap,raw))
    r=classify(snap,raw)
    assert r['transactions_count']==1 and r['reported_process_dates_count']==1
    assert r['transaction_shape']=='MTRANSACTIONS2_ROWS_PRESENT_COMPLETENESS_UNKNOWN'
    assert r['source']=='ONE_DIRECT_AUTHENTICATED_PRIVATE_ESPN_LEAGUE_GET'
    for field in ('source_completeness_attested','reported_process_date_is_verified_effective_time',
                  'claim_cutoff_verified','trade_cutoff_verified',
                  'released_asset_market_status_verified','b2b4c_event_envelope_produced'):
        assert r[field] is False
    assert r['downstream_reacquisition_probability']=='UNKNOWN'
    assert r['action_authority']=='NONE' and r['espn_writes'] is False
    assert (snap,raw)==before
    printed=json.dumps(r)
    assert all(s not in printed for s in ['101','71','18','EXECUTED','1792965500000'])


def test_missing_and_empty_transaction_lists_are_not_full_event_history():
    snap,raw=fixture()
    raw.pop('transactions')
    r=classify(snap,raw)
    assert r['transaction_shape']=='MTRANSACTIONS2_ROWS_ABSENT_NO_EVENT_COVERAGE'
    raw['transactions']=[]
    r=classify(snap,raw)
    assert r['transaction_shape']=='MTRANSACTIONS2_EMPTY_COMPLETENESS_UNKNOWN'
    assert not r['source_completeness_attested']


def test_wrong_league_season_and_week_fail_closed():
    for key,value in [('id',19),('seasonId',2025),('scoringPeriodId',9)]:
        snap,raw=fixture();raw[key]=value
        with pytest.raises(m.Blocked,match='RESPONSE_EPOCH_MISMATCH'):
            classify(snap,raw)


def test_missing_or_duplicate_transaction_ids_block():
    snap,raw=fixture()
    raw['transactions'].append(copy.deepcopy(raw['transactions'][0]))
    with pytest.raises(m.Blocked,match='TRANSACTION_ID_SHAPE_OR_DUPLICATE'):
        classify(snap,raw)
    raw['transactions'][1]['id']=None
    with pytest.raises(m.Blocked,match='TRANSACTION_ID_SHAPE_OR_DUPLICATE'):
        classify(snap,raw)


def test_dates_are_only_shapes_and_must_be_plausible_milliseconds():
    for wrong in (True,12,'2026-10-26',1e12,0,-1):
        snap,raw=fixture();raw['transactions'][0]['processDate']=wrong
        with pytest.raises(m.Blocked,match='TRANSACTION_REPORTED_TIME_SHAPE_INVALID'):
            classify(snap,raw)
    snap,raw=fixture();raw['transactions'][0]['processDate']=None
    r=classify(snap,raw)
    assert r['reported_process_dates_count']==0
    assert not r['reported_process_date_is_verified_effective_time']


def test_unparseable_or_unbounded_items_and_transactions_block():
    snap,raw=fixture();raw['transactions'][0]['items']=['SUSPICIOUS']
    with pytest.raises(m.Blocked,match='TRANSACTION_ITEM_SHAPE_INVALID'):
        classify(snap,raw)
    snap,raw=fixture();raw['transactions']='UNKNOWN'
    with pytest.raises(m.Blocked,match='MTRANSACTIONS2_ROWS_INVALID_OR_UNBOUNDED'):
        classify(snap,raw)
    snap,raw=fixture();raw['transactions']=[{}]*10001
    with pytest.raises(m.Blocked,match='MTRANSACTIONS2_ROWS_INVALID_OR_UNBOUNDED'):
        classify(snap,raw)


def test_transaction_items_missing_is_not_assumed_empty():
    snap,raw=fixture();raw['transactions'][0].pop('items')
    r=classify(snap,raw)
    assert r['transactions_missing_items_count']==1 and r['item_records_count']==0
    assert not r['source_completeness_attested']


def test_naive_future_and_stale_fetched_clocks_fail():
    snap,raw=fixture()
    with pytest.raises(m.Blocked,match='OBSERVATION_CLOCK_NAIVE'):
        classify(snap,raw,started=datetime(2026,10,25,22,15))
    with pytest.raises(m.Blocked,match='DURATION_INVALID'):
        classify(snap,raw,ended=NOW+timedelta(seconds=61),now=NOW+timedelta(seconds=61))
    with pytest.raises(m.Blocked,match='FRESHNESS_INVALID'):
        classify(snap,raw,now=NOW+timedelta(seconds=70))
    with pytest.raises(m.Blocked,match='DURATION_INVALID'):
        classify(snap,raw,ended=NOW-timedelta(seconds=1),now=NOW)


def test_frozen_observation_cannot_be_postdated():
    snap,raw=fixture();snap['snapshot_utc']=(NOW+timedelta(seconds=1)).isoformat()
    with pytest.raises(m.Blocked,match='FROZEN_SNAPSHOT_AFTER_AUTHENTICATED_READ'):
        classify(snap,raw)


def test_source_guard_rejects_wrong_dependency_and_symlink(tmp_path,monkeypatch):
    root=tmp_path/'fantasy_football';root.mkdir()
    expected={}
    for rel in m.DEPENDENCY_BLOBS:
        p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((rel+'\n').encode())
        expected[rel]=m.git_blob(p.read_bytes())
    monkeypatch.setattr(m,'DEPENDENCY_BLOBS',expected)
    m.source_guard(root)
    p=root/next(iter(expected));p.write_text('changed')
    with pytest.raises(m.Blocked,match='SOURCE_DEPENDENCY_DRIFT'):
        m.source_guard(root)


def test_one_get_probe_integrity_and_no_file_side_effect(tmp_path,monkeypatch):
    root=tmp_path/'fantasy_football';runtime=root/'fantasy_season_v0_36_repack1'
    base=runtime/'data/season_snapshots';(base/'001').mkdir(parents=True)
    snap,raw=fixture()
    raw_bytes=json.dumps(snap).encode('utf-8')
    (base/'latest.json').write_bytes(raw_bytes)
    (base/'001/snapshot.json').write_bytes(raw_bytes)
    cfg=root/'config/secrets.json';cfg.parent.mkdir(parents=True);cfg.write_text('INERT_TEST_SENTINEL')
    monkeypatch.setattr(m,'source_guard',lambda root: None)
    asked=[];fake=SimpleNamespace(season=2026,league_id=18)
    def fetch(sec,*,scoring_period_id,views,timeout):
        asked.append((sec,scoring_period_id,views,timeout))
        return copy.deepcopy(raw)
    times=iter([NOW,NOW+timedelta(seconds=2)])
    before={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
    result=m.probe(root,8,runtime_validator=lambda r:runtime,
                   fetcher=fetch,secret_loader=lambda path:fake,clock=lambda:next(times))
    assert asked==[(fake,8,('mSettings','mTeam','mTransactions2'),45)]
    after={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert before==after and result['espn_gets']==1 and not result['persistent_evidence_writes']
    assert not result['b2b4c_event_envelope_produced']


def test_frozen_snapshot_changed_during_read_rejected(tmp_path,monkeypatch):
    root=tmp_path/'fantasy_football';runtime=root/'fantasy_season_v0_36_repack1'
    base=runtime/'data/season_snapshots';(base/'001').mkdir(parents=True)
    snap,raw=fixture();source=json.dumps(snap).encode('utf-8')
    (base/'latest.json').write_bytes(source);(base/'001/snapshot.json').write_bytes(source)
    cfg=root/'config/secrets.json';cfg.parent.mkdir(parents=True);cfg.write_text('FAKE')
    monkeypatch.setattr(m,'source_guard',lambda root: None)
    def malicious(sec,**kwargs):
        (base/'latest.json').write_bytes(source+b' ')
        return raw
    clocks=iter((NOW,NOW+timedelta(seconds=1)))
    with pytest.raises(m.Blocked,match='IMMUTABLE_FROZEN_COPY_NOT_UNIQUE|FROZEN_SNAPSHOT_MUTATED_DURING_PROBE'):
        m.probe(root,8,runtime_validator=lambda r:runtime,
                fetcher=malicious,secret_loader=lambda p:SimpleNamespace(season=2026,league_id=18),
                clock=lambda:next(clocks))


def test_no_production_or_espn_write_hooks():
    code=PATH.read_text('utf-8')
    assert all(forbidden not in code for forbidden in (
        'requests.post(', 'requests.patch(', 'requests.delete(',
        'evaluate_trade(', 'native_mc(', 'sync_season_snapshot(',
        'write_text(', 'write_bytes(', 'open(\'w\'', 'B2B4C_EVENT_ENVELOPE_AUTHENTICATED'))
