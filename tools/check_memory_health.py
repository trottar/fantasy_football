from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
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

REQUIRED_REPO_FILES = (
    "docs/memory/AGENTS.md",
    "docs/memory/CURRENT.md",
    "docs/memory/MEMORY.md",
    "docs/memory/MAINTENANCE.md",
    "docs/memory/README.md",
    "docs/memory/USER.md",
    "docs/memory/handoffs/CURRENT_HANDOFF.md",
    "docs/memory/roadmap/STATUS.md",
    "docs/KNOWN_ISSUES.md",
)

STARTUP_SURFACES = {
    "AGENTS.md": re.compile(r"^##[ \t]+Startup contract(?:[ \t]+.*)?$", re.IGNORECASE | re.MULTILINE),
    "MAINTENANCE.md": re.compile(r"^##[ \t]+Startup Contract Health[ \t]*$", re.MULTILINE),
    "README.md": re.compile(r"^##[ \t]+Startup Contract[ \t]*$", re.MULTILINE),
}

CURRENT_REQUIRED_HEADINGS = (
    "## Active Objective",
    "## Current Work Item",
    "## Verified State",
    "## Calendar / Evidence Gates",
    "## Scientific / Architectural Boundaries",
    "## Exact Next Action",
    "## Relevant References",
)

HANDOFF_REQUIRED_HEADINGS = (
    "# Current Handoff",
    "## Transfer State",
    "## Resume",
)

HANDOFF_FORBIDDEN_HEADINGS = (
    "## Active Objective",
    "## Current Work Item",
    "## Verified State",
    "## Calendar / Evidence Gates",
    "## Scientific / Architectural Boundaries",
    "## Exact Next Action",
    "## Relevant References",
    "## Canonical Pointers",
    "## Roadmap",
)

MEMORY_FORBIDDEN_ACTIVE_HEADINGS = (
    "## Active Objective",
    "## Current Work Item",
    "## Exact Next Action",
    "## Transfer State",
)

ACTIVE_TEXT_SURFACES = (
    "docs/memory/AGENTS.md",
    "docs/memory/CURRENT.md",
    "docs/memory/MEMORY.md",
    "docs/memory/MAINTENANCE.md",
    "docs/memory/README.md",
    "docs/memory/USER.md",
    "docs/memory/handoffs/CURRENT_HANDOFF.md",
    "docs/memory/roadmap/STATUS.md",
    "docs/KNOWN_ISSUES.md",
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


def exact_heading_positions(text: str, headings: tuple[str, ...]) -> dict[str, list[int]]:
    lines = text.splitlines()
    out: dict[str, list[int]] = {heading: [] for heading in headings}
    for index, line in enumerate(lines):
        if line in out:
            out[line].append(index)
    return out


def headings_once_in_order(text: str, headings: tuple[str, ...]) -> tuple[bool, dict[str, int]]:
    positions = exact_heading_positions(text, headings)
    counts = {heading: len(indexes) for heading, indexes in positions.items()}
    if any(count != 1 for count in counts.values()):
        return False, counts
    ordered = [positions[heading][0] for heading in headings]
    return ordered == sorted(ordered), counts


def extract_h2_section(text: str, heading_re: re.Pattern[str]) -> str | None:
    match = heading_re.search(text)
    if not match:
        return None
    start = match.end()
    next_match = re.search(r"^##[ \t]+", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end]


def extract_exact_section(text: str, heading: str, next_heading: str | None = None) -> str | None:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return None
    if next_heading is None:
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if lines[index].startswith("## "):
                end = index
                break
    else:
        try:
            end = lines.index(next_heading, start + 1)
        except ValueError:
            return None
    return "\n".join(lines[start + 1:end]).strip()


def startup_contract_report(memory: Path) -> tuple[dict[str, object], list[str]]:
    issues: list[str] = []
    surfaces: dict[str, object] = {}
    markers = tuple(f"{index}. `{rel}`" for index, rel in enumerate(BOOTSTRAP, start=1))

    for rel, section_re in STARTUP_SURFACES.items():
        path = memory / rel
        if not path.is_file():
            surfaces[rel] = {"present": False, "valid": False}
            issues.append(f"startup contract surface missing: {rel}")
            continue

        text = read_text(path)
        section = extract_h2_section(text, section_re)
        if section is None:
            surfaces[rel] = {"present": True, "valid": False, "section_found": False}
            issues.append(f"{rel} startup contract section missing")
            continue

        positions = [section.find(marker) for marker in markers]
        ordered = all(pos >= 0 for pos in positions) and positions == sorted(positions)
        full_read = "in full" in section.casefold()
        folded = section.casefold()
        post_core = any(
            marker in folded
            for marker in ("after the core", "after that core", "then expand")
        )
        explicit_selective = "select" in folded
        bounded_task_retrieval = (
            "task-relevant" in folded
            and "eager" in folded
        )
        selective = post_core and (explicit_selective or bounded_task_retrieval)
        valid = ordered and full_read and selective
        surfaces[rel] = {
            "present": True,
            "section_found": True,
            "canonical_order": ordered,
            "full_core_read": full_read,
            "selective_expansion": selective,
            "valid": valid,
        }
        if not ordered:
            issues.append(
                f"{rel} does not expose canonical startup order "
                "AGENTS -> CURRENT -> MEMORY -> CURRENT_HANDOFF -> USER"
            )
        if not full_read:
            issues.append(f"{rel} startup contract does not require reading the core in full")
        if not selective:
            issues.append(f"{rel} startup contract does not constrain post-core retrieval to selective/task-relevant expansion")

    overall = bool(surfaces) and all(bool(row.get("valid")) for row in surfaces.values())
    return {"surfaces": surfaces, "valid": overall}, issues


def current_contract_report(current: Path) -> tuple[dict[str, object], list[str]]:
    issues: list[str] = []
    if not current.is_file():
        return {"valid": False, "heading_counts": {}}, ["CURRENT.md missing"]

    text = read_text(current)
    valid, counts = headings_once_in_order(text, CURRENT_REQUIRED_HEADINGS)
    if any(count != 1 for count in counts.values()):
        for heading, count in counts.items():
            if count != 1:
                issues.append(f"CURRENT.md heading {heading!r} count is {count}, expected 1")
    elif not valid:
        issues.append("CURRENT.md required headings are not in canonical order")
    return {"valid": valid, "heading_counts": counts}, issues


def handoff_contract_report(handoff: Path) -> tuple[dict[str, object], list[str]]:
    issues: list[str] = []
    if not handoff.is_file():
        return {"valid": False}, ["CURRENT_HANDOFF.md missing"]

    text = read_text(handoff)
    structure_valid, counts = headings_once_in_order(text, HANDOFF_REQUIRED_HEADINGS)
    if any(count != 1 for count in counts.values()):
        for heading, count in counts.items():
            if count != 1:
                issues.append(f"CURRENT_HANDOFF.md heading {heading!r} count is {count}, expected 1")
    elif not structure_valid:
        issues.append("CURRENT_HANDOFF.md required headings are not in canonical order")

    authority_ok = (
        "`CURRENT.md` is the sole authoritative resumable state." in text
        and "cannot override `CURRENT.md`." in text
    )
    if not authority_ok:
        issues.append("CURRENT_HANDOFF.md does not preserve CURRENT authority/non-override language")

    transfer = extract_exact_section(text, "## Transfer State", "## Resume")
    transfer_nonempty = transfer is not None and bool(transfer.strip())
    if not transfer_nonempty:
        issues.append("CURRENT_HANDOFF.md Transfer State section is empty")

    resume = extract_exact_section(text, "## Resume")
    resume_points_current = resume is not None and "CURRENT.md" in resume
    if not resume_points_current:
        issues.append("CURRENT_HANDOFF.md Resume section does not point to CURRENT.md")

    routine_headings = [heading for heading in HANDOFF_FORBIDDEN_HEADINGS if heading in text.splitlines()]
    if routine_headings:
        issues.append(
            "CURRENT_HANDOFF.md contains routine active-state heading(s): "
            + ", ".join(routine_headings)
        )

    stable_state = "No exceptional transfer state is recorded." in text
    valid = (
        structure_valid
        and authority_ok
        and transfer_nonempty
        and resume_points_current
        and not routine_headings
    )
    return {
        "valid": valid,
        "heading_counts": counts,
        "authority_ok": authority_ok,
        "transfer_nonempty": transfer_nonempty,
        "resume_points_current": resume_points_current,
        "stable_state": stable_state,
        "routine_headings": routine_headings,
    }, issues


def role_separation_report(memory: Path) -> tuple[dict[str, object], list[str]]:
    issues: list[str] = []
    durable = memory / "MEMORY.md"
    forbidden: list[str] = []
    if durable.is_file():
        lines = set(read_text(durable).splitlines())
        forbidden = [heading for heading in MEMORY_FORBIDDEN_ACTIVE_HEADINGS if heading in lines]
        if forbidden:
            issues.append(
                "MEMORY.md contains active/transfer heading(s): " + ", ".join(forbidden)
            )
    return {"valid": not forbidden, "memory_forbidden_headings": forbidden}, issues


def rendered_text_report(root: Path) -> tuple[dict[str, object], list[str]]:
    issues: list[str] = []
    bad_paths: list[str] = []
    for rel in ACTIVE_TEXT_SURFACES:
        path = root / rel
        if not path.is_file():
            continue
        text = read_text(path)
        if "\\n-" in text or "\\r\\n" in text:
            bad_paths.append(rel)
            issues.append(f"{rel} contains literal escaped newline marker in active rendered text")
    return {"valid": not bad_paths, "literal_escape_paths": bad_paths}, issues


def analyze(root: Path) -> dict[str, object]:
    memory = root / "docs/memory"
    if not memory.is_dir():
        raise FileNotFoundError(f"memory root not found: {memory}")

    files: dict[str, dict[str, object]] = {}
    issues: list[str] = []

    for rel in REQUIRED_REPO_FILES:
        if not (root / rel).is_file():
            issues.append(f"missing required active-memory file: {rel}")

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
        active_count = len(re.findall(r"^##\s+Active Objective\s*$", text, flags=re.MULTILINE))
        next_count = len(re.findall(r"^##\s+Exact Next Action\s*$", text, flags=re.MULTILINE))
        files.setdefault("CURRENT.md", {})["active_objectives"] = active_count
        files.setdefault("CURRENT.md", {})["exact_next_actions"] = next_count
        if active_count != 1:
            issues.append(f"CURRENT.md active objective count is {active_count}, expected 1")
        if next_count != 1:
            issues.append(f"CURRENT.md exact next action count is {next_count}, expected 1")

    for rel in ("CURRENT.md", "handoffs/CURRENT_HANDOFF.md"):
        path = memory / rel
        if path.is_file():
            markers = int(file_metrics(path)["checkpoint_markers"])
            if markers:
                issues.append(f"{rel} contains {markers} append-style FANTASY marker(s)")

    bootstrap = {}
    total_bytes = 0
    total_lines = 0
    for rel in BOOTSTRAP:
        path = memory / rel
        if not path.is_file():
            issues.append(f"missing bootstrap file: {rel}")
            continue
        metrics = file_metrics(path)
        bootstrap[rel] = {"bytes": metrics["bytes"], "lines": metrics["lines"]}
        total_bytes += int(metrics["bytes"])
        total_lines += int(metrics["lines"])

    startup, startup_issues = startup_contract_report(memory)
    current_contract, current_issues = current_contract_report(current)
    handoff, handoff_issues = handoff_contract_report(memory / "handoffs/CURRENT_HANDOFF.md")
    roles, role_issues = role_separation_report(memory)
    rendered, rendered_issues = rendered_text_report(root)
    issues.extend(startup_issues)
    issues.extend(current_issues)
    issues.extend(handoff_issues)
    issues.extend(role_issues)
    issues.extend(rendered_issues)

    return {
        "schema": 3,
        "root": str(root),
        "files": files,
        "bootstrap": {
            "files": bootstrap,
            "total_bytes": total_bytes,
            "total_lines": total_lines,
        },
        "contracts": {
            "startup": startup,
            "current": current_contract,
            "handoff": handoff,
            "role_separation": roles,
            "rendered_text": rendered,
        },
        "issues": issues,
        "healthy": not issues,
    }


def render(report: dict[str, object]) -> str:
    lines = ["MEMORY HEALTH", ""]
    files = report["files"]
    for rel in ("CURRENT.md", "handoffs/CURRENT_HANDOFF.md", "MEMORY.md"):
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
            lines.append(f"  active objectives: {row.get('active_objectives', 'n/a')}")
            lines.append(f"  exact next actions: {row.get('exact_next_actions', 'n/a')}")
        lines.append(f"  checkpoint markers: {row.get('checkpoint_markers', 0)}")
        lines.append("")

    boot = report["bootstrap"]
    lines.extend(
        [
            "Bootstrap",
            f"  files: {', '.join(BOOTSTRAP)}",
            f"  total lines: {boot['total_lines']}",
            f"  total size: {boot['total_bytes']} bytes",
            "",
            "Contracts",
        ]
    )
    contracts = report["contracts"]
    for key, label in (
        ("startup", "startup core/order/selective expansion"),
        ("current", "CURRENT structural headings"),
        ("handoff", "handoff authority/structure/role"),
        ("role_separation", "durable-memory role separation"),
        ("rendered_text", "active rendered-text hygiene"),
    ):
        valid = bool(contracts.get(key, {}).get("valid"))
        lines.append(f"  {label}: {'PASS' if valid else 'FAIL'}")

    lines.extend(["", f"Status: {'HEALTHY' if report['healthy'] else 'ATTENTION'}"])
    if report["issues"]:
        lines.append("Issues:")
        for issue in report["issues"]:
            lines.append(f"  - {issue}")
    return "\n".join(lines)


def _write_self_test_fixture(root: Path) -> None:
    memory = root / "docs/memory"
    (memory / "handoffs").mkdir(parents=True, exist_ok=True)
    (memory / "roadmap").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)

    startup = (
        "1. `AGENTS.md`\n"
        "2. `CURRENT.md`\n"
        "3. `MEMORY.md`\n"
        "4. `handoffs/CURRENT_HANDOFF.md`\n"
        "5. `USER.md`\n"
    )
    (memory / "AGENTS.md").write_text(
        "# Agent Operating Rules\n\n"
        "## Startup contract\n\n"
        "Read this stable core in full before acting:\n\n"
        + startup
        + "\nAfter the core is read, load only task-relevant records and do not eagerly load the wider memory hierarchy.\n\n"
        "## Authority\n\nAuthority.\n",
        encoding="utf-8",
    )
    (memory / "CURRENT.md").write_text(
        "# Current Project State\n\n"
        "## Active Objective\n\nTest.\n\n"
        "## Current Work Item\n\nTest.\n\n"
        "## Verified State\n\nTest.\n\n"
        "## Calendar / Evidence Gates\n\nTest.\n\n"
        "## Scientific / Architectural Boundaries\n\nTest.\n\n"
        "## Exact Next Action\n\nDo one thing.\n\n"
        "## Relevant References\n\n- ref\n",
        encoding="utf-8",
    )
    (memory / "MEMORY.md").write_text("# Durable Memory\n\nDurable facts.\n", encoding="utf-8")
    (memory / "MAINTENANCE.md").write_text(
        "# Durable Memory Maintenance Policy\n\n"
        "## Startup Contract Health\n\n"
        "Read first, in full:\n\n"
        + startup
        + "\nOnly after that core is complete, expand selectively.\n\n"
        "## Health Tool\n\nObservational.\n",
        encoding="utf-8",
    )
    (memory / "README.md").write_text(
        "# Durable Project Memory\n\n"
        "## Startup Contract\n\n"
        + startup
        + "\nRead that core in full. Then expand selectively.\n\n"
        "## Authority\n\nAuthority.\n",
        encoding="utf-8",
    )
    (memory / "USER.md").write_text("# Collaboration Preferences\n", encoding="utf-8")
    (memory / "handoffs/CURRENT_HANDOFF.md").write_text(
        "# Current Handoff\n\n"
        "`CURRENT.md` is the sole authoritative resumable state. This file cannot override `CURRENT.md`.\n\n"
        "## Transfer State\n\n"
        "No exceptional transfer state is recorded.\n\n"
        "## Resume\n\n"
        "Follow `../CURRENT.md`.\n",
        encoding="utf-8",
    )
    (memory / "roadmap/STATUS.md").write_text("# Roadmap Status\n\nCurrent.\n", encoding="utf-8")
    (root / "docs/KNOWN_ISSUES.md").write_text("# Known Issues\n\nCurrent.\n", encoding="utf-8")


def self_test() -> None:
    import tempfile

    def fresh() -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory(prefix="memory_health_selftest_")
        root = Path(td.name)
        _write_self_test_fixture(root)
        return td, root

    td, root = fresh()
    try:
        report = analyze(root)
        assert report["healthy"], report
        assert "Status: HEALTHY" in render(report)
    finally:
        td.cleanup()

    td, root = fresh()
    try:
        readme = root / "docs/memory/README.md"
        text = readme.read_text(encoding="utf-8")
        text = text.replace("2. `CURRENT.md`\n3. `MEMORY.md`", "2. `MEMORY.md`\n3. `CURRENT.md`")
        readme.write_text(text, encoding="utf-8")
        report = analyze(root)
        assert not report["healthy"]
        assert any("README.md does not expose canonical startup order" in x for x in report["issues"])
    finally:
        td.cleanup()

    td, root = fresh()
    try:
        current = root / "docs/memory/CURRENT.md"
        current.write_text(
            current.read_text(encoding="utf-8").replace("## Verified State", "## Verified Result"),
            encoding="utf-8",
        )
        report = analyze(root)
        assert any("CURRENT.md heading '## Verified State' count is 0" in x for x in report["issues"])
    finally:
        td.cleanup()

    td, root = fresh()
    try:
        handoff = root / "docs/memory/handoffs/CURRENT_HANDOFF.md"
        handoff.write_text(handoff.read_text(encoding="utf-8") + "\n## Verified State\n\nDuplicate.\n", encoding="utf-8")
        report = analyze(root)
        assert any("routine active-state heading" in x for x in report["issues"])
    finally:
        td.cleanup()

    td, root = fresh()
    try:
        status = root / "docs/memory/roadmap/STATUS.md"
        status.write_text("# Roadmap Status\n\nBad\\n- escaped\n", encoding="utf-8")
        report = analyze(root)
        assert any("literal escaped newline marker" in x for x in report["issues"])
    finally:
        td.cleanup()

    td, root = fresh()
    try:
        memory = root / "docs/memory/MEMORY.md"
        memory.write_text(memory.read_text(encoding="utf-8") + "\n## Exact Next Action\n\nWrong role.\n", encoding="utf-8")
        report = analyze(root)
        assert any("MEMORY.md contains active/transfer heading" in x for x in report["issues"])
    finally:
        td.cleanup()

    td, root = fresh()
    try:
        handoff = root / "docs/memory/handoffs/CURRENT_HANDOFF.md"
        text = handoff.read_text(encoding="utf-8")
        text = text.replace("## Transfer State\n\nNo exceptional transfer state is recorded.\n\n## Resume", "## Transfer State\n\n## Resume")
        handoff.write_text(text, encoding="utf-8")
        report = analyze(root)
        assert any("Transfer State section is empty" in x for x in report["issues"])
    finally:
        td.cleanup()

    print("SELF-TEST PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root containing docs/memory")
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
