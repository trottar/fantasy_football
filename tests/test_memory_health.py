from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_memory_health.py"


def _load_tool():
    spec = importlib.util.spec_from_file_location("memory_health_under_test", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def tool():
    return _load_tool()


@pytest.fixture()
def repo(tmp_path: Path, tool):
    tool._write_self_test_fixture(tmp_path)
    return tmp_path


def test_healthy_fixture_passes(tool, repo):
    report = tool.analyze(repo)
    assert report["healthy"] is True
    assert report["schema"] == 3
    assert all(row["valid"] for row in report["contracts"].values())


def test_startup_order_drift_fails(tool, repo):
    path = repo / "docs/memory/README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "2. `CURRENT.md`\n3. `MEMORY.md`",
            "2. `MEMORY.md`\n3. `CURRENT.md`",
        ),
        encoding="utf-8",
    )
    report = tool.analyze(repo)
    assert report["healthy"] is False
    assert any("README.md does not expose canonical startup order" in issue for issue in report["issues"])


def test_current_heading_drift_fails(tool, repo):
    path = repo / "docs/memory/CURRENT.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("## Verified State", "## Verified Result"),
        encoding="utf-8",
    )
    report = tool.analyze(repo)
    assert any("CURRENT.md heading '## Verified State' count is 0" in issue for issue in report["issues"])


def test_handoff_second_current_heading_fails(tool, repo):
    path = repo / "docs/memory/handoffs/CURRENT_HANDOFF.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n## Verified State\n\nDuplicate.\n",
        encoding="utf-8",
    )
    report = tool.analyze(repo)
    assert any("routine active-state heading" in issue for issue in report["issues"])


def test_empty_transfer_state_fails(tool, repo):
    path = repo / "docs/memory/handoffs/CURRENT_HANDOFF.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "## Transfer State\n\nNo exceptional transfer state is recorded.\n\n## Resume",
            "## Transfer State\n\n## Resume",
        ),
        encoding="utf-8",
    )
    report = tool.analyze(repo)
    assert any("Transfer State section is empty" in issue for issue in report["issues"])


def test_memory_active_heading_fails(tool, repo):
    path = repo / "docs/memory/MEMORY.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n## Exact Next Action\n\nWrong role.\n",
        encoding="utf-8",
    )
    report = tool.analyze(repo)
    assert any("MEMORY.md contains active/transfer heading" in issue for issue in report["issues"])


def test_literal_escaped_newline_in_active_surface_fails(tool, repo):
    path = repo / "docs/memory/roadmap/STATUS.md"
    path.write_text("# Roadmap Status\n\nBad\\n- escaped\n", encoding="utf-8")
    report = tool.analyze(repo)
    assert any("literal escaped newline marker" in issue for issue in report["issues"])

def test_m5_agents_bounded_post_core_wording_without_select_passes(tool, repo):
    path = repo / "docs/memory/AGENTS.md"
    text = path.read_text(encoding="utf-8")
    section = tool.extract_h2_section(
        text,
        tool.STARTUP_SURFACES["AGENTS.md"],
    )
    assert section is not None
    assert "select" not in section.casefold()
    report = tool.analyze(repo)
    startup = report["contracts"]["startup"]
    assert startup["surfaces"]["AGENTS.md"]["selective_expansion"] is True
    assert startup["valid"] is True
    assert report["healthy"] is True
