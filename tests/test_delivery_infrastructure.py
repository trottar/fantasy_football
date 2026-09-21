from __future__ import annotations

import base64
import importlib.util
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile
from io import BytesIO

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
DELIVERY = REPO_ROOT / "tools" / "delivery"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(DELIVERY))
run_package = _load_module("run_package", DELIVERY / "run_package.py")
build_package = _load_module("ff_build_package", DELIVERY / "build_package.py")


def _source_package(tmp_path: Path, *, exit_code: int = 0, stderr: bool = False) -> Path:
    source = tmp_path / "pkgsrc"
    source.mkdir()
    manifest = {
        "schema_version": 1,
        "package_id": "test-package",
        "package_type": "diagnostic",
        "entrypoint": {"type": "python", "path": "apply.py"},
        "description": "delivery infrastructure test package",
    }
    (source / "package.json").write_text(json.dumps(manifest), encoding="utf-8")
    code = [
        "from pathlib import Path",
        "import argparse, sys",
        "p=argparse.ArgumentParser()",
        "p.add_argument('--project-root', required=True)",
        "p.add_argument('--package-root', required=True)",
        "p.add_argument('--package-id', required=True)",
        "a=p.parse_args()",
        "Path(a.project_root, 'runner_marker.txt').write_text(a.package_id, encoding='utf-8')",
    ]
    if stderr:
        code.append("print('expected stderr', file=sys.stderr)")
    code.append(f"raise SystemExit({exit_code})")
    (source / "apply.py").write_text("\n".join(code) + "\n", encoding="utf-8")
    return source


def _build(tmp_path: Path, **kwargs) -> Path:
    source = _source_package(tmp_path, **kwargs)
    out = tmp_path / "package.ffpkg"
    build_package.build_carrier(source, out)
    return out


def test_valid_package_round_trip_and_execution(tmp_path: Path):
    carrier = _build(tmp_path)
    project = tmp_path / "project with spaces"
    project.mkdir()
    assert run_package.run_package(carrier, project) == 0
    assert (project / "runner_marker.txt").read_text(encoding="utf-8") == "test-package"


def test_verify_only_does_not_execute(tmp_path: Path):
    carrier = _build(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    _, manifest, archive = run_package.verify_carrier(carrier)
    assert manifest["package_id"] == "test-package"
    assert archive
    assert not (project / "runner_marker.txt").exists()


def test_truncated_carrier_fails(tmp_path: Path):
    carrier = _build(tmp_path)
    carrier.write_text(carrier.read_text(encoding="utf-8")[:20], encoding="utf-8")
    with pytest.raises(run_package.PackageError, match="valid UTF-8 JSON"):
        run_package.verify_carrier(carrier)


def test_invalid_base64_fails(tmp_path: Path):
    carrier = _build(tmp_path)
    obj = json.loads(carrier.read_text(encoding="utf-8"))
    obj["archive"]["data"] = "%%%"
    carrier.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(run_package.PackageError, match="valid base64"):
        run_package.verify_carrier(carrier)


def test_wrong_archive_hash_fails_before_execution(tmp_path: Path):
    carrier = _build(tmp_path)
    obj = json.loads(carrier.read_text(encoding="utf-8"))
    obj["archive"]["sha256"] = "0" * 64
    carrier.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(run_package.PackageError, match="SHA-256 mismatch"):
        run_package.verify_carrier(carrier)


def test_archive_path_traversal_rejected(tmp_path: Path):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("../escape.txt", b"x")
        zf.writestr("package.json", b"{}")
    with pytest.raises(run_package.PackageError, match="unsafe archive member"):
        run_package.inspect_archive(buffer.getvalue())


def test_missing_manifest_rejected(tmp_path: Path):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("apply.py", b"pass\n")
    with pytest.raises(run_package.PackageError, match="missing package.json"):
        run_package.inspect_archive(buffer.getvalue())


def test_inventory_hash_mismatch_rejected(tmp_path: Path):
    carrier = _build(tmp_path)
    obj = json.loads(carrier.read_text(encoding="utf-8"))
    archive = base64.b64decode(obj["archive"]["data"])
    with zipfile.ZipFile(BytesIO(archive), "r") as zf:
        manifest = json.loads(zf.read("package.json"))
        apply_data = zf.read("apply.py")
    manifest["files"][0]["sha256"] = "0" * 64
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("package.json", json.dumps(manifest))
        zf.writestr("apply.py", apply_data)
    with pytest.raises(run_package.PackageError, match="SHA-256 mismatch"):
        run_package.inspect_archive(buffer.getvalue())


def test_missing_entrypoint_inventory_rejected(tmp_path: Path):
    source = _source_package(tmp_path)
    (source / "apply.py").unlink()
    with pytest.raises(run_package.PackageError, match="entrypoint is not present"):
        build_package.build_archive(source)


def test_nonzero_child_exit_is_propagated(tmp_path: Path):
    carrier = _build(tmp_path, exit_code=7)
    project = tmp_path / "project"
    project.mkdir()
    assert run_package.run_package(carrier, project) == 7
    assert (project / "runner_marker.txt").exists()


def test_stderr_with_zero_exit_is_not_failure(tmp_path: Path):
    carrier = _build(tmp_path, stderr=True)
    project = tmp_path / "project"
    project.mkdir()
    assert run_package.run_package(carrier, project) == 0


def test_repeat_execution_is_supported(tmp_path: Path):
    carrier = _build(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    assert run_package.run_package(carrier, project) == 0
    assert run_package.run_package(carrier, project) == 0


def test_builder_is_deterministic(tmp_path: Path):
    source = _source_package(tmp_path)
    a = tmp_path / "a.ffpkg"
    b = tmp_path / "b.ffpkg"
    build_package.build_carrier(source, a)
    build_package.build_carrier(source, b)
    assert a.read_bytes() == b.read_bytes()


def test_corrupt_zip_rejected():
    with pytest.raises(run_package.PackageError, match="valid ZIP archive"):
        run_package.inspect_archive(b"not-a-zip")


def test_case_colliding_archive_members_rejected():
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("package.json", b"{}")
        zf.writestr("A.txt", b"a")
        zf.writestr("a.txt", b"b")
    with pytest.raises(run_package.PackageError, match="duplicate/colliding archive member"):
        run_package.inspect_archive(buffer.getvalue())


prepare_checkpoint_stage = _load_module(
    "ff_prepare_checkpoint_stage", DELIVERY / "prepare_checkpoint_stage.py"
)


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def test_stage_identity_uses_git_clean_filter_not_raw_sha(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / ".gitattributes").write_text("*.cmd text eol=crlf\n", encoding="utf-8")
    raw = b"@echo off\r\necho hello\r\n"
    (repo / "runner.cmd").write_bytes(raw)
    _git(repo, "add", ".gitattributes", "runner.cmd")

    staged = prepare_checkpoint_stage.staged_bytes(repo, "runner.cmd")
    assert staged == b"@echo off\necho hello\n"
    assert hashlib.sha256(staged).hexdigest() != hashlib.sha256(raw).hexdigest()

    expected_oid = prepare_checkpoint_stage.expected_filtered_blob_oid(
        repo, "runner.cmd", raw
    )
    actual_oid = prepare_checkpoint_stage.staged_blob_oid(repo, "runner.cmd")
    assert expected_oid == actual_oid


def test_stage_representation_validator_accepts_crlf_worktree_to_lf_index(tmp_path: Path):
    control = tmp_path / "control"
    stage = tmp_path / "stage"
    control.mkdir()
    stage.mkdir()
    _git(stage, "init")
    _git(stage, "config", "user.email", "test@example.com")
    _git(stage, "config", "user.name", "Test")
    (stage / ".gitattributes").write_text("*.cmd text eol=crlf\n", encoding="utf-8")
    _git(stage, "add", ".gitattributes")
    raw = b"@echo off\r\necho hello\r\n"
    (control / "runner.cmd").write_bytes(raw)
    (stage / "runner.cmd").write_bytes(raw)
    _git(stage, "add", "runner.cmd")

    prepare_checkpoint_stage.validate_source_index_representation(
        control, stage, ["runner.cmd"]
    )


def test_stage_spec_rejects_unsafe_path(tmp_path: Path):
    spec = {
        "schema_version": 1,
        "checkpoint_id": "x",
        "repo": "repo",
        "branch": "main",
        "expected_remote_head": "0" * 40,
        "project_root": "root",
        "stage_root": "stage",
        "source_paths": ["../escape"],
        "exact_sha256": {},
        "semantic_markers": [],
        "manifest": {"root": "docs/memory", "path": "docs/memory/manifest.json"},
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    with pytest.raises(prepare_checkpoint_stage.StageError, match="safe repository-relative"):
        prepare_checkpoint_stage.load_stage_spec(path)
