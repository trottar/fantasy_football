from fantasy import _print_specialist_channel


def test_specialist_cli_output_is_cp1252_safe(capsys):
    report = {
        "week": 1,
        "channel": "DEFENSE",
        "team_name": "Us",
        "position": "DST",
        "owned": [{"name": "Owned DST", "team": "DET"}],
        "mc_scenarios": 32,
        "baseline": {
            "weighted_mean_ppg": 5.75,
            "current_week_mean": 6.77,
            "current_week_sd": 4.81,
            "current_week_choice": "Owned DST",
        },
        "swap_actions": [{
            "action": "SWAP", "add_name": "Candidate DST", "add_team": "NO",
            "drop_name": "Owned DST", "fantasy_status": "FREEAGENT",
            "delta_channel_ppg": -0.321, "p_channel_better": 0.457,
            "current_week_delta": -2.07, "classification": "HOLD_CHANNEL",
            "weekly_plan": [],
        }],
        "carry_actions": [{
            "add_name": "Candidate DST", "add_team": "NO",
            "rotation_synergy_ppg": 0.608, "net_screen_ppg": 0.601,
            "classification": "CARRY_SYNERGY_SCREEN",
            "best_one_defense_state": "Owned DST", "best_one_defense_ppg": 5.75,
            "authoritative": False,
            "player_slot_release": {"name": "Bench RB", "position": "RB"},
            "player_slot_lineup_cost_ppg": 0.005,
            "player_slot_insurance_cost_ppg": 0.005,
            "player_slot_insurance_weight": 0.25,
            "player_slot_cost_ppg": 0.007,
            "player_slot_cost_method": "PLAYER_CHANNEL_SEASON_LINEUP_PLUS_WEIGHTED_INSURANCE_V031_FIXED2",
        }],
    }
    _print_specialist_channel(report, limit=8)
    out = capsys.readouterr().out
    out.encode("cp1252")
    assert all(ord(ch) < 128 for ch in out)
    assert "channel delta=-0.321" in out
    assert "current 6.77 +/- 4.81" in out
