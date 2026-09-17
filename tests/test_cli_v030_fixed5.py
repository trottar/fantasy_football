from fantasy import _print_action_rows


def test_fixed5_action_printer_keeps_numbered_headers(capsys):
    rows = [
        {
            "add_name": "Alpha", "add_position": "WR", "add_team": "X",
            "drop_name": "Drop A", "drop_position": "RB", "fantasy_status": "FREEAGENT",
            "delta_utility": 0.01, "expected_delta_utility": 0.01,
            "mc_scenarios": 1024, "mc_stage": "SCREEN1", "mc_futility_stop": True,
        },
        {
            "add_name": "Beta", "add_position": "TE", "add_team": "Y",
            "drop_name": "Drop B", "drop_position": "WR", "fantasy_status": "FREEAGENT",
            "delta_utility": 0.02, "expected_delta_utility": 0.02,
            "mc_scenarios": 4096, "mc_stage": "SCREEN2", "mc_futility_stop": True,
        },
    ]
    _print_action_rows("TEST ACTIONS", rows, 10)
    out = capsys.readouterr().out
    assert " 1. ADD Alpha" in out
    assert " 2. ADD Beta" in out
    assert "stage=SCREEN1 FUTILITY_STOP" in out
    assert "stage=SCREEN2 FUTILITY_STOP" in out
