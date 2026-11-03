"""Network-free regression for exact Week 9 supervised prelaunch source pin.

The source-guard check must accept the published 2026 decision-cycle source and
continue rejecting changed bytes. This never launches MC or reaches providers.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / 'tools/operations/guarded_weekly_cycle.py'
spec = importlib.util.spec_from_file_location('week9_source_pin_guard', GUARD)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

PUBLISHED_CYCLE_BLOB = '1c4c40ffc856e27d7b8c0919ee363ec15ce21f89'
HISTORICAL_CYCLE_BLOB = 'c4c7fafbdeabb9454b8eb0c82a5aa4a466f7d12a'
PATCHED_GUARD_BLOB = '801a87ae3787aa9e159f52964d880d8ff1d1e2ac'


def test_updated_pin_matches_current_published_decision_cycle():
    assert g._git_blob(GUARD.read_bytes()) == PATCHED_GUARD_BLOB
    source = ROOT / 'src/weekly_decision_cycle.py'
    assert g._git_blob(source.read_bytes()) == PUBLISHED_CYCLE_BLOB
    assert g.EXPECTED_BLOBS['src/weekly_decision_cycle.py'] == PUBLISHED_CYCLE_BLOB
    assert PUBLISHED_CYCLE_BLOB != HISTORICAL_CYCLE_BLOB


def test_unrelated_commissioned_buckets_remain_pinned():
    assert g.EXPECTED_SOURCE_CHECKPOINT == '68dfabed5088a6ddf90a5d3af4f5497bf25f334a'
    assert g.EXPECTED_BLOBS == {
        'fantasy.py': 'dd3a0a2b39ea1c6b424e71f6a11273f2503ccc64',
        'src/weekly_decision_cycle.py': PUBLISHED_CYCLE_BLOB,
        'src/closure.py': '9e7602dde722a999c5077904cb5d485d9015f34e',
    }


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / 'fantasy_football'
    runtime = root / g.EXPECTED_RUNTIME
    (root / 'tools/operations').mkdir(parents=True)
    (root / 'tools/operations/deadline_budget.py').write_text('# test sentinel\n', encoding='utf-8')
    runtime.mkdir()
    (runtime / 'VERSION').write_text(g.EXPECTED_VERSION, encoding='utf-8')
    for rel in g.EXPECTED_BLOBS:
        src = ROOT / rel
        dst = runtime / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return root, runtime


def test_source_identity_accepts_only_exact_published_blobs(tmp_path):
    root, runtime = _fixture(tmp_path)
    assert g.validate_root(root) == runtime
    target = runtime / 'src/weekly_decision_cycle.py'
    target.write_bytes(target.read_bytes() + b'\n# unauthorized source mutation\n')
    with pytest.raises(g.Blocked, match='SOURCE_BLOB_MISMATCH:src/weekly_decision_cycle.py'):
        g.validate_root(root)


def test_non_cycle_source_mutation_still_blocks(tmp_path):
    root, runtime = _fixture(tmp_path)
    target = runtime / 'src/closure.py'
    target.write_bytes(target.read_bytes() + b'\n# unauthorized source mutation\n')
    with pytest.raises(g.Blocked, match='SOURCE_BLOB_MISMATCH:src/closure.py'):
        g.validate_root(root)


def test_incorrect_runtime_version_still_blocks(tmp_path):
    root, runtime = _fixture(tmp_path)
    (runtime / 'VERSION').write_text('0.35', encoding='utf-8')
    with pytest.raises(g.Blocked, match='COMMISSIONED_RUNTIME_UNVERIFIED'):
        g.validate_root(root)
