from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Threshold:
    soft_bytes: int
    hard_bytes: int
    soft_lines: int
    hard_lines: int


RULES = {
    "CURRENT.md": Threshold(
        soft_bytes=8 * 1024,
        hard_bytes=16 * 1024,
        soft_lines=175,
        hard_lines=300,
    ),
    "handoffs/CURRENT_HANDOFF.md": Threshold(
        soft_bytes=6 * 1024,
        hard_bytes=10 * 1024,
        soft_lines=125,
        hard_lines=200,
    ),
    "MEMORY.md": Threshold(
        soft_bytes=30 * 1024,
        hard_bytes=50 * 1024,
        soft_lines=350,
        hard_lines=550,
    ),
}

BOOTSTRAP = (
    "AGENTS.md",
    "CURRENT.md",
    "MEMORY.md",
    "handoffs/CURRENT_HANDOFF.md",
    "USER.md",
)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
MARKER_RE = re.compile(r"<!--\s*FANTASY_[A-Z0-9_:-]+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="strict")


def file_metrics(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    lines = len(text.splitlines())
    headings = [m.group(2).strip() for m in HEADING_RE.finditer(text)]
    duplicates = sorted(
        heading
        for heading, count in Counter(headings).items()
        if count > 1
    )
    return {
        "bytes": len(raw),
        "lines": lines,
        "duplicate_headings": duplicates,
        "checkpoint_markers": len(MARKER_RE.findall(text)),
    }


def threshold_status(
    metrics: dict[str, object],
    threshold: Threshold,
) -> str:
    size = int(metrics["bytes"])
    lines = int(metrics["lines"])
    if size >= threshold.hard_bytes or lines >= threshold.hard_lines:
        return "HARD"
    if size >= threshold.soft_bytes or lines >= threshold.soft_lines:
        return "SOFT"
    return "HEALTHY"


def analyze(root: Path) -> dict[str, object]:
    memory = root / "docs/memory"
    if not memory.is_dir():
        raise FileNotFoundError(f"memory root not found: {memory}")

    files: dict[str, dict[str, object]] = {}
    issues: list[str] = []

    for rel, threshold in RULES.items():
        path = memory / rel
        if not path.is_file():
            issues.append(f"missing required memory file: {rel}")
            continue
        metrics = file_metrics(path)
        metrics["status"] = threshold_status(metrics, threshold)
        metrics["threshold"] = asdict(threshold)
        files[rel] = metrics
        if metrics["status"] != "HEALTHY":
            issues.append(f"{rel} threshold status: {metrics['status']}")
        if metrics["duplicate_headings"]:
            issues.append(
                f"{rel} duplicate headings: {metrics['duplicate_headings']}"
            )

    current = memory / "CURRENT.md"
    if current.is_file():
        text = read_text(current)
        active_count = len(
            re.findall(
                r"^##\s+Active Objective\s*$",
                text,
                flags=re.MULTILINE,
            )
        )
        next_count = len(
            re.findall(
                r"^##\s+Exact Next Action\s*$",
                text,
                flags=re.MULTILINE,
            )
        )
        files.setdefault("CURRENT.md", {})["active_objectives"] = active_count
        files.setdefault("CURRENT.md", {})["exact_next_actions"] = next_count

        if active_count != 1:
            issues.append(
                f"CURRENT.md active objective count is {active_count}, expected 1"
            )
        if next_count != 1:
            issues.append(
                f"CURRENT.md exact next action count is {next_count}, expected 1"
            )

    for rel in ("CURRENT.md", "handoffs/CURRENT_HANDOFF.md"):
        path = memory / rel
        if path.is_file():
            markers = int(file_metrics(path)["checkpoint_markers"])
            if markers:
                issues.append(
                    f"{rel} contains {markers} append-style FANTASY marker(s)"
                )

    agents = memory / "AGENTS.md"
    if agents.is_file():
        text = read_text(agents)
        required = [
            "1. `AGENTS.md`",
            "2. `CURRENT.md`",
            "3. `MEMORY.md`",
            "4. `handoffs/CURRENT_HANDOFF.md`",
            "5. `USER.md`",
        ]
        positions = [text.find(item) for item in required]
        if any(pos < 0 for pos in positions) or positions != sorted(positions):
            issues.append(
                "AGENTS.md does not expose canonical startup order "
                "AGENTS -> CURRENT -> MEMORY -> CURRENT_HANDOFF -> USER"
            )

    bootstrap = {}
    total_bytes = 0
    total_lines = 0
    for rel in BOOTSTRAP:
        path = memory / rel
        if not path.is_file():
            issues.append(f"missing bootstrap file: {rel}")
            continue
        metrics = file_metrics(path)
        bootstrap[rel] = {
            "bytes": metrics["bytes"],
            "lines": metrics["lines"],
        }
        total_bytes += int(metrics["bytes"])
        total_lines += int(metrics["lines"])

    return {
        "schema": 2,
        "root": str(root),
        "files": files,
        "bootstrap": {
            "files": bootstrap,
            "total_bytes": total_bytes,
            "total_lines": total_lines,
        },
        "issues": issues,
        "healthy": not issues,
    }


def render(report: dict[str, object]) -> str:
    lines = ["MEMORY HEALTH", ""]
    files = report["files"]
    for rel in (
        "CURRENT.md",
        "handoffs/CURRENT_HANDOFF.md",
        "MEMORY.md",
    ):
        row = files.get(rel)
        if not row:
            continue
        lines.extend(
            [
                rel,
                f"  lines: {row['lines']}",
                f"  size: {row['bytes']} bytes",
                f"  threshold: {row['status']}",
            ]
        )
        if rel == "CURRENT.md":
            lines.append(
                f"  active objectives: {row.get('active_objectives', 'n/a')}"
            )
            lines.append(
                f"  exact next actions: {row.get('exact_next_actions', 'n/a')}"
            )
        lines.append(
            f"  checkpoint markers: {row.get('checkpoint_markers', 0)}"
        )
        lines.append("")

    boot = report["bootstrap"]
    lines.extend(
        [
            "Bootstrap",
            f"  files: {', '.join(BOOTSTRAP)}",
            f"  total lines: {boot['total_lines']}",
            f"  total size: {boot['total_bytes']} bytes",
            "",
            f"Status: {'HEALTHY' if report['healthy'] else 'ATTENTION'}",
        ]
    )

    if report["issues"]:
        lines.append("Issues:")
        for issue in report["issues"]:
            lines.append(f"  - {issue}")

    return "\n".join(lines)


def self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="memory_health_selftest_") as raw:
        root = Path(raw)
        memory = root / "docs/memory"
        (memory / "handoffs").mkdir(parents=True)

        (memory / "AGENTS.md").write_text(
            "# Agent Operating Rules\n\n"
            "1. `AGENTS.md`\n"
            "2. `CURRENT.md`\n"
            "3. `MEMORY.md`\n"
            "4. `handoffs/CURRENT_HANDOFF.md`\n"
            "5. `USER.md`\n",
            encoding="utf-8",
        )
        (memory / "CURRENT.md").write_text(
            "# Current Project State\n\n"
            "## Active Objective\n\nTest.\n\n"
            "## Exact Next Action\n\nDo one thing.\n",
            encoding="utf-8",
        )
        (memory / "USER.md").write_text(
            "# Collaboration Preferences\n",
            encoding="utf-8",
        )
        (memory / "MEMORY.md").write_text(
            "# Durable Memory\n",
            encoding="utf-8",
        )
        (memory / "handoffs/CURRENT_HANDOFF.md").write_text(
            "# Current Handoff\n",
            encoding="utf-8",
        )

        report = analyze(root)
        assert report["healthy"], report
        text = render(report)
        assert "Status: HEALTHY" in text
        assert "MEMORY.md" in text
        assert "handoffs/CURRENT_HANDOFF.md" in text

    print("SELF-TEST PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=".",
        help="repository root containing docs/memory",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    report = analyze(Path(args.root).resolve())

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render(report))

    if args.strict and not report["healthy"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
