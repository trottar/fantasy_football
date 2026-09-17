from datetime import datetime, timezone
import json
import random
import subprocess

import pytest

from src.observability.context import RunContext
from src.observability.provenance import (
    SourceProvenance,
    canonical_json_bytes,
    collect_provenance,
    git_source_state,
    sha256_bytes,
    sha256_file,
    sha256_json,
    sha256_json_file,
)


def _git(root, *args):
    cp = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stdout
    return cp.stdout.strip()


def test_canonical_json_hash_is_key_order_independent_but_value_sensitive():
    left = {"b": [2, 3], "a": 1}
    right = {"a": 1, "b": [2, 3]}
    changed = {"a": 1, "b": [2, 4]}

    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert sha256_json(left) == sha256_json(right)
    assert sha256_json(left) != sha256_json(changed)


def test_canonical_json_rejects_non_finite_and_non_string_keys():
    with pytest.raises(ValueError, match="non-finite"):
        sha256_json({"value": float("nan")})
    with pytest.raises(TypeError, match="keys must be strings"):
        sha256_json({1: "value"})


def test_file_hash_tracks_exact_bytes_and_json_file_hash_tracks_semantics(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text('{"a": 1, "b": [2, 3]}\n', encoding="utf-8")
    second.write_text('{\n  "b": [2, 3],\n  "a": 1\n}\n', encoding="utf-8")

    assert sha256_file(first) != sha256_file(second)
    assert sha256_json_file(first) == sha256_json_file(second)
    assert sha256_bytes(b"abc") == sha256_file(_write_bytes(tmp_path / "raw.bin", b"abc"))


def _write_bytes(path, data):
    path.write_bytes(data)
    return path


def test_git_source_state_ignores_untracked_but_detects_tracked_changes(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "qa@example.com")
    _git(repo, "config", "user.name", "QA")
    (repo / "VERSION").write_text("0.36\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("one\n", encoding="utf-8")
    _git(repo, "add", "VERSION", "tracked.txt")
    _git(repo, "commit", "-m", "initial")

    commit, dirty = git_source_state(repo)
    assert len(commit) == 40
    assert dirty is False

    (repo / "untracked.txt").write_text("local only\n", encoding="utf-8")
    assert git_source_state(repo) == (commit, False)

    (repo / "tracked.txt").write_text("two\n", encoding="utf-8")
    assert git_source_state(repo) == (commit, True)


def test_collect_provenance_returns_hashes_not_file_contents_and_fits_context(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "qa@example.com")
    _git(repo, "config", "user.name", "QA")
    (repo / "VERSION").write_text("0.36\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "VERSION", "tracked.txt")
    _git(repo, "commit", "-m", "initial")

    config = tmp_path / "config.json"
    snapshot = tmp_path / "snapshot.json"
    config.write_text('{"secret_like": "value", "n": 2}\n', encoding="utf-8")
    snapshot.write_text('{"private_like": "payload"}\n', encoding="utf-8")

    provenance = collect_provenance(
        repo,
        config_path=config,
        input_snapshot_path=snapshot,
    )
    row = provenance.as_dict()
    rendered = json.dumps(row, sort_keys=True)
    assert "secret_like" not in rendered
    assert "private_like" not in rendered
    assert "payload" not in rendered
    assert row["release_version"] == "0.36"
    assert row["source_tracked_dirty"] is False
    assert len(row["config_hash"]) == 64
    assert len(row["input_snapshot_hash"]) == 64

    context = RunContext.create(
        subsystem="observability",
        timestamp=datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc),
        **provenance.context_kwargs(),
    )
    assert context.release_version == "0.36"
    assert context.source_commit == row["source_commit"]


def test_provenance_hashing_does_not_advance_python_random_state(tmp_path):
    path = tmp_path / "value.json"
    path.write_text('{"a": 1}\n', encoding="utf-8")
    random.seed(919191)
    before = random.getstate()
    sha256_file(path)
    sha256_json_file(path)
    after = random.getstate()
    assert after == before
