"""Provider-free guarded GUI launch tests; no ESPN, capture, MC or local runtime."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

import pytest


def load(path: Path):
    spec=importlib.util.spec_from_file_location('weekly_evaluation_runner_test',path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def runner():
    return load(Path(__file__).resolve().parents[1]/'src/gui/weekly_evaluation_runner.py')

NOW=datetime(2026,11,3,16,0,tzinfo=timezone.utc)


def layout(tmp_path, monkeypatch, module):
    runtime=tmp_path/module.PORTABLE/'fantasy_football'/module.RELEASE
    (runtime/'data/season_decisions').mkdir(parents=True)
    (runtime/'fantasy.py').write_text('pass\n')
    source=runtime.parent/'tools/operations/weekly_operator_v2.py'
    source.parent.mkdir(parents=True)
    source.write_text('pass\n')
    monkeypatch.setattr(module,'blob',lambda p:module.OPERATOR_BLOB)
    return runtime


def public_line(plan, **changed):
    row={'contract':'WEEK8_INTEGRATED_OPERATOR_V2_SOURCE_CANDIDATE_V1',
         'week':plan['week'],'slot':plan['slot'],'operator_state':'INCOMPLETE_COVERAGE',
         'completed_phases':['CALENDAR','SYNC','CAPTURE','MC','REVIEW'],
         'blocker':'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED',
         'transaction_authority':'NONE','commissioning_trial':True}
    row.update(changed)
    return ('WEEKLY_OPERATOR_RESULT='+json.dumps(row)+'\nNO_ESPN_WRITES=TRUE\n').encode()


def test_calendar_tuesday_and_dst_boundary():
    m=runner()
    assert m.clock(NOW)==(9,'TUE','20261103')
    assert m.clock(datetime(2026,11,2,4,59,tzinfo=timezone.utc))[0]==8
    assert m.clock(datetime(2026,11,2,5,0,tzinfo=timezone.utc))[0]==9
    assert m.clock(datetime(2026,11,5,16,tzinfo=timezone.utc))[1]=='PASSIVE'


def test_portable_identity_and_launch_reuse_fail_closed(tmp_path,monkeypatch):
    m=runner(); runtime=layout(tmp_path,monkeypatch,m)
    p=m.prepare(runtime,Path(sys.executable),now=NOW)
    assert p['week']==9 and p['slot']=='TUE'
    assert p['name']=='operator_v2_trial_2026_w09_TUE_20261103'
    (p['folder']/(p['name']+'.launch.json')).write_text('{}')
    with pytest.raises(m.EvaluationBlocked,match='TRIAL_ALREADY_STARTED_THIS_SLOT'):
        m.prepare(runtime,Path(sys.executable),now=NOW)
    with pytest.raises(m.EvaluationBlocked,match='NOT_EXISTING_PORTABLE_V2'):
        m.prepare(tmp_path/'random'/m.RELEASE,Path(sys.executable),now=NOW)
    (p['folder']/(p['name']+'.launch.json')).unlink()
    monkeypatch.setattr(m,'blob',lambda p:'0000000000000000000000000000000000000000')
    with pytest.raises(m.EvaluationBlocked,match='IDENTITY_MISMATCH'):
        m.prepare(runtime,Path(sys.executable),now=NOW)


def test_phase_progress_only_checks_receipt_names(tmp_path,monkeypatch):
    m=runner(); p=m.prepare(layout(tmp_path,monkeypatch,m),Path(sys.executable),now=NOW)
    assert m.phase_status(p)=='LAUNCH_PENDING'
    for suffix,state in [('.launch.json','CALENDAR_OR_PREFLIGHT'),
                         ('.sync.start.json','SYNC_RUNNING_OR_INTERRUPTED'),
                         ('.sync.done.json','SYNC_COMPLETE'),
                         ('.capture.start.json','CAPTURE_RUNNING_OR_INTERRUPTED'),
                         ('.mc.start.json','MC_RUNNING_OR_INTERRUPTED'),
                         ('.report.json','REPORT_WRITTEN')]:
        (p['folder']/(p['name']+suffix)).write_text('not parsed private content')
        assert m.phase_status(p)==state


def test_completed_MC_never_claims_ESPN_action_authority(tmp_path,monkeypatch):
    m=runner(); p=m.prepare(layout(tmp_path,monkeypatch,m),Path(sys.executable),now=NOW)
    r=m.outcome(0,public_line(p),p)
    assert r['state']=='NATIVE_MC_COMPLETE_ACTION_CERTIFICATION_BLOCKED'
    assert r['action_authority']=='NONE'
    assert r['blocker']=='FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED'
    assert m.outcome(0,public_line(p,transaction_authority='YES'),p)['state']=='BLOCKED_OPERATOR_AUTHORITY_OR_IDENTITY'
    assert m.outcome(0,public_line(p,week=8),p)['state']=='BLOCKED_OPERATOR_AUTHORITY_OR_IDENTITY'
    assert m.outcome(3,b'WEEKLY_OPERATOR_BLOCKED=NOT_A_PROTECTED_OPERATION_SLOT\n',p)['state']=='BLOCKED_NOT_A_PROTECTED_OPERATION_SLOT'
    assert m.outcome(3,b'WEEKLY_OPERATOR_BLOCKED=private cookie id:xyz\n',p)['state']=='BLOCKED_NO_VALID_PUBLIC_RESULT'
    assert m.outcome(0,b'x'*(m.MAX_OPERATOR_OUTPUT+1),p)['state']=='BLOCKED_UNBOUNDED_OPERATOR_OUTPUT'
    assert m.outcome(3,public_line(p),p)['state']=='BLOCKED_INCOMPLETE_COVERAGE'


def test_one_child_launch_pins_flags_and_never_retries(tmp_path,monkeypatch):
    m=runner(); runtime=layout(tmp_path,monkeypatch,m)
    plan=m.prepare(runtime,Path(sys.executable),now=NOW)
    # The second in-process preflight reuses this synthetic fixed UTC epoch.
    original=m.prepare
    monkeypatch.setattr(m,'prepare',lambda rt, exe: original(rt,exe,now=NOW))
    calls=[]
    class Child:
        returncode=0
        async def communicate(self):
            assert plan['id'] in m._RUNNING
            with pytest.raises(m.EvaluationBlocked,match='ALREADY_RUNNING'):
                await m.supervised_run(plan)
            return public_line(plan), None
    async def fake_spawn(*args,**kwargs):
        calls.append((args,kwargs))
        return Child()
    monkeypatch.setattr(m.asyncio,'create_subprocess_exec',fake_spawn)
    got=asyncio.run(m.supervised_run(plan))
    assert got['state']=='NATIVE_MC_COMPLETE_ACTION_CERTIFICATION_BLOCKED'
    assert len(calls)==1
    args,kwargs=calls[0]
    assert args[-3:]==('--mode','trial','--ack-live-readonly')
    assert '--project-root' in args and '--week' in args
    assert kwargs['cwd']==str(plan['root'])
    assert not m._RUNNING
