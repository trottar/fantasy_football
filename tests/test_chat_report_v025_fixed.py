import json
from pathlib import Path

from fantasy import build_parser
from test_season_gui_service_v024 import _build_runtime


def test_chat_report_uses_gui_service_state_and_is_paste_friendly(tmp_path: Path):
    service = _build_runtime(tmp_path)
    report = service.generate_chat_report(selection=service.default_lineup_selection())
    text = report["text"]
    payload = report["payload"]
    dashboard = service.dashboard_state()
    assert "FANTASY CHAT DIAGNOSIS v0.35-fixed1" in text
    assert "MATCHUP" in text
    assert "LINEUP" in text
    assert "CLOSURE" in text
    assert len(payload["lineup"]) == 9
    assert payload["matchup"]["policy_win"] == dashboard["weekly_win_probability"]
    assert payload["matchup"]["fixed_win"] == dashboard["fixed_planning_win_probability"]
    assert payload["hypothetical"]["changed"] is False


def test_chat_report_tracks_hypothetical_and_selected_action(tmp_path: Path):
    service = _build_runtime(tmp_path)
    selection = service.default_lineup_selection()
    rb1 = int(selection["RB1"])
    drop = next(r for r in service.legal_drop_players() if r["position"] == "WR")
    action = service.evaluate_single_add_drop(201, int(drop["espn_id"]))
    report = service.generate_chat_report(
        selection=selection,
        availability_modes={rb1: "OUT"},
        action_result=action,
    )
    assert report["payload"]["hypothetical"]["changed"] is True
    assert report["payload"]["action"]["add_espn_id"] == 201
    assert "HYPOTHETICAL" in report["text"]
    assert "SELECTED ADD/DROP" in report["text"]


def test_chat_report_writes_txt_and_json(tmp_path: Path):
    service = _build_runtime(tmp_path)
    result = service.write_chat_report(out_dir=tmp_path / "chat_reports")
    txt = Path(result["text_path"])
    js = Path(result["json_path"])
    assert txt.exists() and js.exists()
    assert txt.read_text(encoding="utf-8") == result["text"]
    loaded = json.loads(js.read_text(encoding="utf-8"))
    assert loaded["team_name"] == "Us"


def test_chat_report_cli_is_available():
    args = build_parser().parse_args(["chat-report"])
    assert args.out.endswith("chat_reports")
    assert args.add_id is None
    assert args.drop_id is None
