import json
from pathlib import Path


def load_league(path: str | Path):
    path = Path(path)
    with path.open() as f:
        return json.load(f)


def user_overall_picks(num_teams: int, rounds: int, draft_slot: int):
    picks = []
    for rnd in range(1, rounds + 1):
        if rnd % 2 == 1:
            overall = (rnd - 1) * num_teams + draft_slot
        else:
            overall = rnd * num_teams - draft_slot + 1
        picks.append(overall)
    return picks


def team_slot_for_overall_pick(overall: int, num_teams: int):
    rnd = (overall - 1) // num_teams + 1
    pick_in_round = (overall - 1) % num_teams + 1
    if rnd % 2 == 1:
        slot = pick_in_round
    else:
        slot = num_teams - pick_in_round + 1
    return rnd, pick_in_round, slot
