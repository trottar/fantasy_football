from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import Any, Dict, Iterable, List, Tuple

FORMAT_VERSION = 1
MANIFEST_SCHEMA_VERSION = 1
PACKAGE_MANIFEST_NAME = "package.json"
MAX_CARRIER_BYTES = 128 * 1024 * 1024
MAX_ARCHIVE_BYTES = 96 * 1024 * 1024
MAX_MEMBERS = 4096
MAX_EXPANDED_BYTES = 256 * 1024 * 1024
ALLOWED_PACKAGE_TYPES = {"diagnostic", "local_apply", "runtime_sync", "release_install", "maintenance"}


class PackageError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relpath(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise PackageError(f"{field} must be a non-empty string")
    if "\\" in value:
        raise PackageError(f"{field} must use forward slashes: {value!r}")
    if ":" in value or "\x00" in value:
        raise PackageError(f"unsafe {field}: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise PackageError(f"unsafe {field}: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise PackageError(f"non-canonical {field}: {value!r}")
    return normalized


def _require_dict(value: Any, field: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise PackageError(f"{field} must be an object")
    return value


def _require_int(value: Any, field: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise PackageError(f"{field} must be an integer >= {minimum}")
    return value


def _require_hex_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise PackageError(f"{field} must be a 64-character SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise PackageError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise PackageError(
            f"unsupported manifest schema_version: {manifest.get('schema_version')!r}"
        )
    package_id = manifest.get("package_id")
    if not isinstance(package_id, str) or not package_id.strip():
        raise PackageError("manifest package_id must be a non-empty string")
    package_type = manifest.get("package_type")
    if package_type not in ALLOWED_PACKAGE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_PACKAGE_TYPES))
        raise PackageError(f"manifest package_type must be one of: {allowed}")

    entrypoint = _require_dict(manifest.get("entrypoint"), "manifest.entrypoint")
    entrypoint_type = entrypoint.get("type")
    if entrypoint_type not in {"python", "powershell", "cmd"}:
        raise PackageError(
            "manifest.entrypoint.type must be one of: python, powershell, cmd"
        )
    entrypoint_path = _safe_relpath(
        entrypoint.get("path"), field="manifest.entrypoint.path"
    )

    files = manifest.get("files")
    if not isinstance(files, list):
        raise PackageError("manifest.files must be an array")
    seen = set()
    seen_casefold = set()
    normalized_files: List[Dict[str, Any]] = []
    for index, item in enumerate(files):
        obj = _require_dict(item, f"manifest.files[{index}]")
        rel = _safe_relpath(obj.get("path"), field=f"manifest.files[{index}].path")
        if rel == PACKAGE_MANIFEST_NAME:
            raise PackageError("manifest.files must not list package.json itself")
        folded = rel.casefold()
        if rel in seen or folded in seen_casefold:
            raise PackageError(f"duplicate/colliding manifest file path: {rel}")
        seen.add(rel)
        seen_casefold.add(folded)
        normalized_files.append(
            {
                "path": rel,
                "bytes": _require_int(
                    obj.get("bytes"), f"manifest.files[{index}].bytes"
                ),
                "sha256": _require_hex_sha256(
                    obj.get("sha256"), f"manifest.files[{index}].sha256"
                ),
            }
        )

    if entrypoint_path not in seen:
        raise PackageError(
            f"manifest entrypoint is not present in file inventory: {entrypoint_path}"
        )

    normalized = dict(manifest)
    normalized["files"] = normalized_files
    normalized["entrypoint"] = {"type": entrypoint_type, "path": entrypoint_path}
    return normalized


def _validate_zip_member(info: zipfile.ZipInfo) -> str:
    name = info.filename
    if name.endswith("/"):
        raise PackageError(f"directory entries are not allowed in package archive: {name}")
    rel = _safe_relpath(name, field="archive member")
    # Reject symlink-like Unix entries.
    unix_mode = (info.external_attr >> 16) & 0xFFFF
    if unix_mode and (unix_mode & 0o170000) == 0o120000:
        raise PackageError(f"symlink archive member is not allowed: {rel}")
    return rel


def inspect_archive(archive_bytes: bytes, *, expected_package_id: str | None = None) -> Tuple[Dict[str, Any], Dict[str, bytes]]:
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise PackageError(f"archive exceeds maximum size: {len(archive_bytes)} bytes")
    try:
        with zipfile.ZipFile(io_bytes := _BytesReader(archive_bytes), "r") as zf:
            infos = zf.infolist()
            if len(infos) > MAX_MEMBERS:
                raise PackageError(f"archive contains too many members: {len(infos)}")
            names: List[str] = []
            members: Dict[str, bytes] = {}
            seen_casefold = set()
            expanded = 0
            for info in infos:
                rel = _validate_zip_member(info)
                folded = rel.casefold()
                if rel in members or folded in seen_casefold:
                    raise PackageError(f"duplicate/colliding archive member: {rel}")
                expanded += int(info.file_size)
                if expanded > MAX_EXPANDED_BYTES:
                    raise PackageError(f"archive expanded size exceeds limit: {expanded} bytes")
                names.append(rel)
                seen_casefold.add(folded)
                members[rel] = zf.read(info)
    except zipfile.BadZipFile as exc:
        raise PackageError("payload is not a valid ZIP archive") from exc

    if PACKAGE_MANIFEST_NAME not in members:
        raise PackageError("archive is missing package.json")
    try:
        manifest_obj = json.loads(members[PACKAGE_MANIFEST_NAME].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError("package.json is not valid UTF-8 JSON") from exc
    manifest = validate_manifest(_require_dict(manifest_obj, "package.json"))

    if expected_package_id is not None and manifest["package_id"] != expected_package_id:
        raise PackageError(
            "carrier/package package_id mismatch: "
            f"{expected_package_id!r} != {manifest['package_id']!r}"
        )

    inventory = {item["path"]: item for item in manifest["files"]}
    actual_payload = set(members) - {PACKAGE_MANIFEST_NAME}
    if actual_payload != set(inventory):
        missing = sorted(set(inventory) - actual_payload)
        extra = sorted(actual_payload - set(inventory))
        raise PackageError(
            f"archive inventory mismatch: missing={missing} extra={extra}"
        )

    for rel, meta in inventory.items():
        data = members[rel]
        if len(data) != meta["bytes"]:
            raise PackageError(
                f"file byte-count mismatch for {rel}: expected {meta['bytes']} actual {len(data)}"
            )
        actual_sha = sha256_bytes(data)
        if actual_sha != meta["sha256"]:
            raise PackageError(
                f"file SHA-256 mismatch for {rel}: expected {meta['sha256']} actual {actual_sha}"
            )

    return manifest, members


class _BytesReader:
    """Minimal seekable wrapper accepted by zipfile without importing io at call sites."""

    def __init__(self, data: bytes):
        import io

        self._buffer = io.BytesIO(data)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._buffer, name)

    def __enter__(self) -> "_BytesReader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._buffer.close()


def load_carrier(path: Path) -> Tuple[Dict[str, Any], bytes]:
    if not path.is_file():
        raise PackageError(f"package carrier not found: {path}")
    size = path.stat().st_size
    if size > MAX_CARRIER_BYTES:
        raise PackageError(f"carrier exceeds maximum size: {size} bytes")
    try:
        text = path.read_text(encoding="utf-8")
        carrier = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError("carrier is not valid UTF-8 JSON") from exc
    carrier = _require_dict(carrier, "carrier")
    if carrier.get("ffpkg_format") != FORMAT_VERSION:
        raise PackageError(
            f"unsupported carrier ffpkg_format: {carrier.get('ffpkg_format')!r}"
        )
    package_id = carrier.get("package_id")
    if not isinstance(package_id, str) or not package_id.strip():
        raise PackageError("carrier package_id must be a non-empty string")
    archive = _require_dict(carrier.get("archive"), "carrier.archive")
    if archive.get("encoding") != "base64":
        raise PackageError("carrier.archive.encoding must be 'base64'")
    expected_bytes = _require_int(archive.get("bytes"), "carrier.archive.bytes")
    expected_sha = _require_hex_sha256(
        archive.get("sha256"), "carrier.archive.sha256"
    )
    payload = archive.get("data")
    if not isinstance(payload, str):
        raise PackageError("carrier.archive.data must be a base64 string")
    try:
        archive_bytes = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise PackageError("carrier archive data is not valid base64") from exc
    if len(archive_bytes) != expected_bytes:
        raise PackageError(
            f"carrier archive byte-count mismatch: expected {expected_bytes} actual {len(archive_bytes)}"
        )
    actual_sha = sha256_bytes(archive_bytes)
    if actual_sha != expected_sha:
        raise PackageError(
            f"carrier archive SHA-256 mismatch: expected {expected_sha} actual {actual_sha}"
        )
    return carrier, archive_bytes


def verify_carrier(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any], bytes]:
    carrier, archive_bytes = load_carrier(path)
    manifest, _ = inspect_archive(
        archive_bytes, expected_package_id=carrier["package_id"]
    )
    return carrier, manifest, archive_bytes


def extract_archive(archive_bytes: bytes, destination: Path) -> Dict[str, Any]:
    manifest, members = inspect_archive(archive_bytes)
    destination.mkdir(parents=True, exist_ok=False)
    for rel, data in members.items():
        target = destination.joinpath(*PurePosixPath(rel).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return manifest


def _run_entrypoint(manifest: Dict[str, Any], package_root: Path, project_root: Path) -> int:
    entry = manifest["entrypoint"]
    entry_path = package_root.joinpath(*PurePosixPath(entry["path"]).parts)
    common = [
        "--project-root",
        str(project_root),
        "--package-root",
        str(package_root),
        "--package-id",
        manifest["package_id"],
    ]
    if entry["type"] == "python":
        command = [sys.executable, str(entry_path), *common]
    elif entry["type"] == "powershell":
        command = [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(entry_path),
            "-ProjectRoot",
            str(project_root),
            "-PackageRoot",
            str(package_root),
            "-PackageId",
            manifest["package_id"],
        ]
    else:
        command = [
            "cmd.exe",
            "/d",
            "/c",
            str(entry_path),
            str(project_root),
            str(package_root),
            manifest["package_id"],
        ]
    try:
        completed = subprocess.run(command, cwd=str(project_root), check=False)
    except OSError as exc:
        raise PackageError(f"failed to start package entrypoint: {exc}") from exc
    return int(completed.returncode)


def default_project_root() -> Path:
    # Installed location: <root>/tools/delivery/run_package.py
    return Path(__file__).resolve().parents[2]


def run_package(carrier_path: Path, project_root: Path) -> int:
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise PackageError(f"project root is not a directory: {project_root}")

    carrier, manifest, archive_bytes = verify_carrier(carrier_path)
    print("FFPKG RUNNER PREFLIGHT PASS")
    print(f"Package: {manifest['package_id']}")
    print(f"Type: {manifest['package_type']}")
    print(f"Archive bytes: {len(archive_bytes)}")
    print(f"Archive SHA256: {carrier['archive']['sha256']}")

    with tempfile.TemporaryDirectory(prefix="fantasy_ffpkg_") as tmp:
        package_root = Path(tmp) / "package"
        extracted_manifest = extract_archive(archive_bytes, package_root)
        if extracted_manifest != manifest:
            raise PackageError("manifest changed between verification and extraction")
        rc = _run_entrypoint(manifest, package_root, project_root)

    if rc != 0:
        print("FFPKG RUNNER FAIL")
        print(f"Package: {manifest['package_id']}")
        print(f"Entrypoint exit code: {rc}")
        return rc

    print("FFPKG RUNNER COMPLETE")
    print(f"Package: {manifest['package_id']}")
    print("Entrypoint exit code: 0")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a validated fantasy-football .ffpkg package")
    parser.add_argument("package", type=Path, help="Path to the text .ffpkg carrier")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project/control root (defaults to the runner's repository root)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Validate carrier/archive/manifest without executing its entrypoint",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv) if argv is not None else None)
    try:
        carrier, manifest, archive_bytes = verify_carrier(args.package.resolve())
        if args.verify_only:
            print("FFPKG VERIFY PASS")
            print(f"Package: {manifest['package_id']}")
            print(f"Type: {manifest['package_type']}")
            print(f"Archive bytes: {len(archive_bytes)}")
            print(f"Archive SHA256: {carrier['archive']['sha256']}")
            return 0
        root = args.project_root.resolve() if args.project_root else default_project_root()
        return run_package(args.package.resolve(), root)
    except PackageError as exc:
        print("FFPKG RUNNER FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
