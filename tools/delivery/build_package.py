from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile
from io import BytesIO
from typing import Any, Dict, Iterable, List

from run_package import (
    FORMAT_VERSION,
    PACKAGE_MANIFEST_NAME,
    PackageError,
    inspect_archive,
    sha256_bytes,
    validate_manifest,
)

FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
IGNORED_NAMES = {"__pycache__", ".pytest_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def _source_files(source_dir: Path) -> List[Path]:
    files: List[Path] = []
    for path in source_dir.rglob("*"):
        rel_parts = path.relative_to(source_dir).parts
        if any(part in IGNORED_NAMES for part in rel_parts):
            continue
        if path.is_symlink():
            raise PackageError(f"symlinks are not allowed in package source: {path}")
        if path.is_file():
            if path.suffix.lower() in IGNORED_SUFFIXES:
                continue
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(source_dir).as_posix())


def _load_source_manifest(source_dir: Path) -> Dict[str, Any]:
    path = source_dir / PACKAGE_MANIFEST_NAME
    if not path.is_file():
        raise PackageError(f"package source is missing {PACKAGE_MANIFEST_NAME}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError("source package.json is not valid UTF-8 JSON") from exc
    if not isinstance(obj, dict):
        raise PackageError("source package.json must be an object")
    if "files" in obj:
        raise PackageError("source package.json must not define files; builder owns inventory")
    return obj


def _canonical_manifest(source_dir: Path) -> tuple[Dict[str, Any], Dict[str, bytes]]:
    source_manifest = _load_source_manifest(source_dir)
    payload: Dict[str, bytes] = {}
    inventory: List[Dict[str, Any]] = []
    for path in _source_files(source_dir):
        rel = path.relative_to(source_dir).as_posix()
        if rel == PACKAGE_MANIFEST_NAME:
            continue
        data = path.read_bytes()
        payload[rel] = data
        inventory.append({"path": rel, "bytes": len(data), "sha256": sha256_bytes(data)})
    manifest = dict(source_manifest)
    manifest["files"] = inventory
    manifest = validate_manifest(manifest)
    return manifest, payload


def _zipinfo(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    return info


def build_archive(source_dir: Path) -> tuple[Dict[str, Any], bytes]:
    manifest, payload = _canonical_manifest(source_dir)
    manifest_bytes = (
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr(_zipinfo(PACKAGE_MANIFEST_NAME), manifest_bytes)
        for rel in sorted(payload):
            zf.writestr(_zipinfo(rel), payload[rel])
    archive = buffer.getvalue()
    checked_manifest, _ = inspect_archive(
        archive, expected_package_id=manifest["package_id"]
    )
    if checked_manifest != manifest:
        raise PackageError("built archive manifest failed round-trip validation")
    return manifest, archive


def build_carrier(source_dir: Path, output: Path) -> Dict[str, Any]:
    manifest, archive = build_archive(source_dir)
    carrier = {
        "ffpkg_format": FORMAT_VERSION,
        "package_id": manifest["package_id"],
        "archive": {
            "encoding": "base64",
            "bytes": len(archive),
            "sha256": sha256_bytes(archive),
            "data": base64.b64encode(archive).decode("ascii"),
        },
    }
    text = json.dumps(carrier, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    return carrier


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a deterministic text .ffpkg carrier")
    parser.add_argument("source_dir", type=Path, help="Directory containing package.json and payload files")
    parser.add_argument("output", type=Path, help="Output .ffpkg path")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv) if argv is not None else None)
    try:
        source = args.source_dir.resolve()
        if not source.is_dir():
            raise PackageError(f"package source directory not found: {source}")
        carrier = build_carrier(source, args.output.resolve())
        print("FFPKG BUILD PASS")
        print(f"Package: {carrier['package_id']}")
        print(f"Carrier: {args.output.resolve()}")
        print(f"Archive bytes: {carrier['archive']['bytes']}")
        print(f"Archive SHA256: {carrier['archive']['sha256']}")
        return 0
    except PackageError as exc:
        print("FFPKG BUILD FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
