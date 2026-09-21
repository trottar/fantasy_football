from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple


SPEC_SCHEMA_VERSION = 1
SENTINEL_NAME = ".checkpoint_stage_id"


class StageError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run(
    cmd: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    input_bytes: Optional[bytes] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    cp = subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and cp.returncode != 0:
        raise StageError(
            "command failed rc={0}: {1}\nstdout:\n{2}\nstderr:\n{3}".format(
                cp.returncode,
                " ".join(cmd),
                cp.stdout.decode("utf-8", "replace").strip(),
                cp.stderr.decode("utf-8", "replace").strip(),
            )
        )
    return cp


def _git(
    repo: Path,
    *args: str,
    input_bytes: Optional[bytes] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return _run(
        ["git", "-C", str(repo)] + list(args),
        input_bytes=input_bytes,
        check=check,
    )


def _git_text(repo: Path, *args: str) -> str:
    return _git(repo, *args).stdout.decode("utf-8", "replace").strip()


def _safe_relpath(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise StageError("{0} must be a non-empty string".format(field))
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise StageError("{0} must be a safe repository-relative path: {1}".format(field, value))
    return value.replace("\\", "/")


def load_stage_spec(path: Path) -> Dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise StageError("stage spec is not valid UTF-8 JSON") from exc

    if not isinstance(obj, dict):
        raise StageError("stage spec root must be an object")
    if obj.get("schema_version") != SPEC_SCHEMA_VERSION:
        raise StageError("unsupported stage spec schema_version")

    required = {
        "checkpoint_id",
        "repo",
        "branch",
        "expected_remote_head",
        "project_root",
        "stage_root",
        "source_paths",
        "exact_sha256",
        "semantic_markers",
        "manifest",
    }
    missing = sorted(required.difference(obj))
    if missing:
        raise StageError("stage spec missing keys: {0}".format(", ".join(missing)))

    if not isinstance(obj["source_paths"], list) or not obj["source_paths"]:
        raise StageError("source_paths must be a non-empty list")
    paths = [_safe_relpath(p, field="source_paths") for p in obj["source_paths"]]
    if len(paths) != len(set(paths)):
        raise StageError("source_paths contains duplicates")
    obj["source_paths"] = paths

    exact = obj["exact_sha256"]
    if not isinstance(exact, dict):
        raise StageError("exact_sha256 must be an object")
    for rel, digest in exact.items():
        safe = _safe_relpath(rel, field="exact_sha256 path")
        if safe not in paths:
            raise StageError("exact_sha256 path is not in source_paths: {0}".format(safe))
        if not isinstance(digest, str) or len(digest) != 64:
            raise StageError("exact_sha256 value must be a 64-character SHA-256: {0}".format(safe))

    markers = obj["semantic_markers"]
    if not isinstance(markers, list):
        raise StageError("semantic_markers must be a list")
    for marker in markers:
        if not isinstance(marker, dict):
            raise StageError("semantic marker must be an object")
        rel = _safe_relpath(marker.get("path"), field="semantic marker path")
        if rel not in paths:
            raise StageError("semantic marker path is not in source_paths: {0}".format(rel))
        if not isinstance(marker.get("contains"), str) or not marker["contains"]:
            raise StageError("semantic marker contains must be non-empty")

    manifest = obj["manifest"]
    if not isinstance(manifest, dict):
        raise StageError("manifest must be an object")
    manifest["root"] = _safe_relpath(manifest.get("root"), field="manifest root").rstrip("/")
    manifest["path"] = _safe_relpath(manifest.get("path"), field="manifest path")
    if not manifest["path"].startswith(manifest["root"] + "/"):
        raise StageError("manifest path must be inside manifest root")

    return obj


def remote_head(repo_url: str, branch: str) -> str:
    cp = _run(["git", "ls-remote", repo_url, "refs/heads/{0}".format(branch)])
    text = cp.stdout.decode("utf-8", "replace").strip()
    if not text:
        raise StageError("remote branch not found: {0}".format(branch))
    return text.split()[0]


def validate_control_root(root: Path, spec: Dict[str, Any]) -> None:
    if not root.is_dir():
        raise StageError("project root missing: {0}".format(root))

    for rel in spec["source_paths"]:
        if not (root / rel).is_file():
            raise StageError("reviewed source path missing: {0}".format(rel))

    # exact_sha256 is explicitly a raw control-root/worktree byte contract.
    for rel, expected in spec["exact_sha256"].items():
        actual = sha256_bytes((root / rel).read_bytes())
        if actual != expected:
            raise StageError(
                "raw control-root identity mismatch: {0}: expected {1} actual {2}".format(
                    rel, expected, actual
                )
            )

    for marker in spec["semantic_markers"]:
        text = (root / marker["path"]).read_text(encoding="utf-8-sig")
        if marker["contains"] not in text:
            raise StageError(
                "semantic marker missing in {0}: {1}".format(
                    marker["path"], marker["contains"]
                )
            )


def clone_exact(spec: Dict[str, Any], stage: Path) -> None:
    checkpoint_id = spec["checkpoint_id"]

    if stage.exists():
        sentinel = stage / SENTINEL_NAME
        if (
            not sentinel.is_file()
            or sentinel.read_text(encoding="utf-8").strip() != checkpoint_id
        ):
            raise StageError(
                "stage path exists and is not owned by this checkpoint: {0}".format(stage)
            )
        shutil.rmtree(stage)

    stage.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "git",
            "clone",
            "--no-tags",
            "--branch",
            spec["branch"],
            spec["repo"],
            str(stage),
        ]
    )
    (stage / SENTINEL_NAME).write_text(checkpoint_id + "\n", encoding="utf-8")

    actual = _git_text(stage, "rev-parse", "HEAD")
    if actual != spec["expected_remote_head"]:
        raise StageError(
            "staging clone HEAD mismatch: expected {0} actual {1}".format(
                spec["expected_remote_head"], actual
            )
        )


def copy_and_stage(root: Path, stage: Path, source_paths: Sequence[str]) -> None:
    for rel in source_paths:
        src = root / rel
        dst = stage / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        # Copy identity is a raw-byte comparison; Git representation is checked separately.
        if src.read_bytes() != dst.read_bytes():
            raise StageError("raw copy identity mismatch: {0}".format(rel))
    _git(stage, "add", "--", *source_paths)


def staged_bytes(stage: Path, rel: str) -> bytes:
    return _git(stage, "show", ":{0}".format(rel)).stdout


def staged_blob_oid(stage: Path, rel: str) -> str:
    return _git_text(stage, "rev-parse", ":{0}".format(rel))


def expected_filtered_blob_oid(stage: Path, rel: str, raw_worktree_bytes: bytes) -> str:
    # `git hash-object --path <path> --stdin` applies the checkout's clean filters
    # for that path without writing an object. This is the representation the
    # index is expected to contain after `git add`.
    cp = _git(
        stage,
        "hash-object",
        "--path",
        rel,
        "--stdin",
        input_bytes=raw_worktree_bytes,
    )
    oid = cp.stdout.decode("ascii", "replace").strip()
    if not oid:
        raise StageError("failed to derive filtered Git blob OID: {0}".format(rel))
    return oid


def validate_source_index_representation(
    root: Path,
    stage: Path,
    source_paths: Sequence[str],
) -> None:
    for rel in source_paths:
        raw = (root / rel).read_bytes()
        expected_oid = expected_filtered_blob_oid(stage, rel, raw)
        actual_oid = staged_blob_oid(stage, rel)
        if expected_oid != actual_oid:
            raise StageError(
                "staged Git representation mismatch: {0}: expected blob {1} actual {2}".format(
                    rel, expected_oid, actual_oid
                )
            )


def build_manifest(stage: Path, cfg: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    root = cfg["root"].rstrip("/")
    manifest_path = cfg["path"]
    prefix = root + "/"

    cp = _git(stage, "ls-files", "-z", "--", root)
    repo_paths: List[str] = []
    for raw in cp.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8")
        if rel != manifest_path:
            repo_paths.append(rel)
    repo_paths.sort()

    entries: List[Dict[str, Any]] = []
    for repo_rel in repo_paths:
        if not repo_rel.startswith(prefix):
            raise StageError(
                "manifest source path outside configured root: {0}".format(repo_rel)
            )
        data = staged_bytes(stage, repo_rel)
        entries.append(
            {
                "path": repo_rel[len(prefix):],
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )

    obj = {
        "schema": 2,
        "representation": "git_index_blob_bytes",
        "generated_at": datetime.now().astimezone().isoformat(),
        "durable_memory_updated": bool(cfg.get("durable_memory_updated", True)),
        "files": entries,
    }
    return obj, len(entries)


def write_stage_manifest(stage: Path, cfg: Dict[str, Any]) -> int:
    obj, count = build_manifest(stage, cfg)
    path = stage / cfg["path"]
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _git(stage, "add", "--", cfg["path"])
    return count


def validate_manifest(stage: Path, cfg: Dict[str, Any]) -> int:
    manifest_path = cfg["path"]
    root = cfg["root"].rstrip("/")
    prefix = root + "/"
    obj = json.loads(staged_bytes(stage, manifest_path).decode("utf-8"))

    if obj.get("schema") != 2:
        raise StageError("manifest schema != 2")
    if obj.get("representation") != "git_index_blob_bytes":
        raise StageError("manifest representation mismatch")

    entries = obj.get("files")
    if not isinstance(entries, list):
        raise StageError("manifest files must be a list")

    seen = set()
    for entry in entries:
        rel = entry["path"]
        p = Path(rel)
        if rel in seen or p.is_absolute() or ".." in p.parts:
            raise StageError("duplicate/unsafe manifest path: {0}".format(rel))
        seen.add(rel)
        repo_rel = prefix + rel
        if repo_rel == manifest_path:
            raise StageError("manifest must exclude itself")
        data = staged_bytes(stage, repo_rel)
        if len(data) != entry["bytes"] or sha256_bytes(data) != entry["sha256"]:
            raise StageError("manifest staged-byte mismatch: {0}".format(rel))

    actual = set()
    cp = _git(stage, "ls-files", "-z", "--", root)
    for raw in cp.stdout.split(b"\0"):
        if not raw:
            continue
        repo_rel = raw.decode("utf-8")
        if repo_rel == manifest_path:
            continue
        actual.add(repo_rel[len(prefix):])

    if actual != seen:
        raise StageError("manifest path-set mismatch")
    return len(entries)


def validate_stage(
    root: Path,
    stage: Path,
    spec: Dict[str, Any],
) -> Tuple[str, int]:
    validation = spec.get("validation", {})
    memory_health = validation.get("strict_memory_health")
    if memory_health:
        cp = _run([sys.executable] + list(memory_health), cwd=stage, check=False)
        if cp.returncode != 0:
            raise StageError(
                "strict memory health failed\n{0}\n{1}".format(
                    cp.stdout.decode("utf-8", "replace"),
                    cp.stderr.decode("utf-8", "replace"),
                )
            )

    _git(stage, "diff", "--check")
    _git(stage, "diff", "--cached", "--check")

    expected = sorted(spec["source_paths"] + [spec["manifest"]["path"]])
    changed = _git(
        stage,
        "diff",
        "--cached",
        "--name-only",
        "--diff-filter=ACMR",
    ).stdout
    actual = sorted(p.decode("utf-8") for p in changed.splitlines() if p)
    if actual != expected:
        raise StageError(
            "staged allowlist mismatch\nexpected={0}\nactual={1}".format(
                expected, actual
            )
        )

    unstaged = _git(stage, "diff", "--name-only").stdout.decode(
        "utf-8", "replace"
    ).strip()
    if unstaged:
        raise StageError("unstaged tracked residue: {0}".format(unstaged))

    untracked = _git(
        stage, "ls-files", "--others", "--exclude-standard"
    ).stdout.decode("utf-8", "replace")
    unexpected = [
        p for p in untracked.splitlines() if p and p != SENTINEL_NAME
    ]
    if unexpected:
        raise StageError("unexpected untracked residue: {0}".format(unexpected))

    # Critical representation rule: raw control-root SHA-256 is not compared to
    # staged bytes. Verify that Git's clean-filtered form of each copied raw file
    # is exactly the blob present in the index.
    validate_source_index_representation(root, stage, spec["source_paths"])

    manifest_count = validate_manifest(stage, spec["manifest"])
    tree_oid = _git_text(stage, "write-tree")
    return tree_oid, manifest_count


def prepare_checkpoint(spec_path: Path) -> int:
    spec = load_stage_spec(spec_path.resolve())
    root = Path(spec["project_root"]).resolve()
    stage = Path(spec["stage_root"]).resolve()

    print("=" * 68, flush=True)
    print("GENERIC REPOSITORY CHECKPOINT STAGING", flush=True)
    print("=" * 68, flush=True)
    print("Checkpoint: {0}".format(spec["checkpoint_id"]), flush=True)
    print("Control root: {0}".format(root), flush=True)
    print("Stage root: {0}".format(stage), flush=True)
    print("Mode: isolated staging + manifest only; NO COMMIT / NO PUSH", flush=True)
    print("", flush=True)

    print("[1/6] Validating declarative checkpoint spec and control-root scope...", flush=True)
    validate_control_root(root, spec)
    print("      PASS", flush=True)

    print("[2/6] Re-checking remote movement guard...", flush=True)
    actual_remote = remote_head(spec["repo"], spec["branch"])
    if actual_remote != spec["expected_remote_head"]:
        raise StageError(
            "remote moved: expected {0} actual {1}".format(
                spec["expected_remote_head"], actual_remote
            )
        )
    print("      PASS / {0}".format(actual_remote), flush=True)

    print("[3/6] Creating fresh isolated staging clone...", flush=True)
    clone_exact(spec, stage)
    print("      PASS / HEAD={0}".format(_git_text(stage, "rev-parse", "HEAD")), flush=True)

    print("[4/6] Copying/staging exact reviewed source scope...", flush=True)
    copy_and_stage(root, stage, spec["source_paths"])
    print("      PASS / source paths={0}".format(len(spec["source_paths"])), flush=True)

    print("[5/6] Regenerating staged-blob manifest...", flush=True)
    manifest_count = write_stage_manifest(stage, spec["manifest"])
    print("      PASS / manifest entries={0}".format(manifest_count), flush=True)

    print("[6/6] Running health, diff, residue, representation, and allowlist gates...", flush=True)
    tree_oid, checked_count = validate_stage(root, stage, spec)
    print("      PASS", flush=True)

    print("GENERIC REPOSITORY CHECKPOINT STAGING PASS", flush=True)
    print("Checkpoint: {0}".format(spec["checkpoint_id"]), flush=True)
    print("Base/remote HEAD: {0}".format(spec["expected_remote_head"]), flush=True)
    print("Stage root: {0}".format(stage), flush=True)
    print("Reviewed source paths: {0}".format(len(spec["source_paths"])), flush=True)
    print(
        "Staged paths including manifest: {0} / EXACT".format(
            len(spec["source_paths"]) + 1
        ),
        flush=True,
    )
    print("Manifest entries: {0}".format(checked_count), flush=True)
    print("Raw control-root identities: PASS", flush=True)
    print("Git clean-filter/index identities: PASS", flush=True)
    print("Strict memory health: PASS", flush=True)
    print("git diff --check: PASS", flush=True)
    print("git diff --cached --check: PASS", flush=True)
    print("Unstaged/untracked residue: NONE", flush=True)
    print("Staged tree OID: {0}".format(tree_oid), flush=True)
    print("Commit: NOT PERFORMED", flush=True)
    print("Push: NOT PERFORMED", flush=True)
    print("Next: assistant verification -> local commit -> remote guard -> push", flush=True)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generic isolated staging/manifest preflight. Never commits or pushes."
    )
    parser.add_argument("spec", type=Path)
    args = parser.parse_args(argv)

    try:
        return prepare_checkpoint(args.spec)
    except Exception as exc:
        print("GENERIC REPOSITORY CHECKPOINT STAGING FAIL", file=sys.stderr, flush=True)
        print(str(exc), file=sys.stderr, flush=True)
        print("Commit: NOT PERFORMED", file=sys.stderr, flush=True)
        print("Push: NOT PERFORMED", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
