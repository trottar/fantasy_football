from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from typing import Any


_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def sha256_bytes(data: bytes | bytearray | memoryview) -> str:
    """Return the SHA-256 digest for exact bytes."""
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes-like")
    return hashlib.sha256(bytes(data)).hexdigest()


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Hash exact file bytes without retaining file content in provenance output."""
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    file_path = Path(path)
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_json(value: Any, path: str = "value") -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} mapping keys must be strings")
            normalized[key] = _normalize_json(item, f"{path}.{key}")
        return normalized
    if isinstance(value, (list, tuple)):
        return [
            _normalize_json(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    raise TypeError(
        f"{path} contains unsupported JSON value type {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return stable UTF-8 JSON bytes for JSON-compatible values."""
    normalized = _normalize_json(value)
    text = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8")


def sha256_json(value: Any) -> str:
    """Hash canonical JSON so object key ordering does not change identity."""
    return sha256_bytes(canonical_json_bytes(value))


def sha256_json_file(path: str | Path) -> str:
    """Parse JSON and hash its canonical semantic representation."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    return sha256_json(value)


def read_release_version(
    repo_root: str | Path,
    *,
    relative_path: str | Path = "VERSION",
) -> str:
    """Read the release/version marker without modifying the repository."""
    path = Path(repo_root) / Path(relative_path)
    value = path.read_text(encoding="utf-8-sig").strip()
    if not value:
        raise ValueError(f"release version file is empty: {path}")
    return value


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def git_source_state(repo_root: str | Path) -> tuple[str, bool]:
    """Return HEAD commit and tracked-dirty state, ignoring untracked files.

    The returned tuple contains no path list and therefore does not expose local
    filenames in provenance output.
    """
    root = Path(repo_root)
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode != 0:
        raise RuntimeError(
            f"git rev-parse HEAD failed ({head.returncode}): "
            f"{head.stderr.strip()}"
        )
    commit = head.stdout.strip().lower()
    if not _COMMIT_RE.fullmatch(commit):
        raise RuntimeError(f"cannot parse Git HEAD commit: {head.stdout!r}")

    status = _git(root, "status", "--porcelain", "--untracked-files=no")
    if status.returncode != 0:
        raise RuntimeError(
            f"git status failed ({status.returncode}): {status.stderr.strip()}"
        )
    return commit, bool(status.stdout.strip())


@dataclass(frozen=True)
class SourceProvenance:
    """Hashes and source identity suitable for immutable run context."""

    release_version: str
    source_commit: str
    source_tracked_dirty: bool
    config_hash: str | None = None
    input_snapshot_hash: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.release_version, str) or not self.release_version.strip():
            raise ValueError("release_version must be a non-empty string")
        object.__setattr__(self, "release_version", self.release_version.strip())

        if not isinstance(self.source_commit, str) or not _COMMIT_RE.fullmatch(
            self.source_commit
        ):
            raise ValueError("source_commit must be a 40-character hexadecimal Git SHA")
        object.__setattr__(self, "source_commit", self.source_commit.lower())

        if not isinstance(self.source_tracked_dirty, bool):
            raise TypeError("source_tracked_dirty must be a bool")

        for field in ("config_hash", "input_snapshot_hash"):
            value = getattr(self, field)
            if value is None:
                continue
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
                raise ValueError(f"{field} must be a 64-character SHA-256 or None")
            object.__setattr__(self, field, value.lower())

    def context_kwargs(self) -> dict[str, str | None]:
        """Return the subset accepted by RunContext without introducing coupling."""
        return {
            "release_version": self.release_version,
            "source_commit": self.source_commit,
            "config_hash": self.config_hash,
            "input_snapshot_hash": self.input_snapshot_hash,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "release_version": self.release_version,
            "source_commit": self.source_commit,
            "source_tracked_dirty": self.source_tracked_dirty,
            "config_hash": self.config_hash,
            "input_snapshot_hash": self.input_snapshot_hash,
        }


def collect_provenance(
    repo_root: str | Path,
    *,
    config_path: str | Path | None = None,
    input_snapshot_path: str | Path | None = None,
    canonicalize_config_json: bool = True,
) -> SourceProvenance:
    """Collect source/version/hash identity without returning file contents.

    Config JSON defaults to semantic canonical hashing. Input snapshots use exact
    byte hashing because frozen input identity should change when the stored
    snapshot bytes change.
    """
    root = Path(repo_root)
    commit, dirty = git_source_state(root)
    version = read_release_version(root)

    config_hash = None
    if config_path is not None:
        path = Path(config_path)
        config_hash = (
            sha256_json_file(path)
            if canonicalize_config_json
            else sha256_file(path)
        )

    input_hash = None
    if input_snapshot_path is not None:
        input_hash = sha256_file(Path(input_snapshot_path))

    return SourceProvenance(
        release_version=version,
        source_commit=commit,
        source_tracked_dirty=dirty,
        config_hash=config_hash,
        input_snapshot_hash=input_hash,
    )
