from __future__ import annotations

import json
from pathlib import Path

from .league import team_slot_for_overall_pick


class DraftState:
    def __init__(self, num_teams: int, rounds: int, user_draft_slot: int):
        self.num_teams = num_teams
        self.rounds = rounds
        self.user_draft_slot = user_draft_slot
        self.picks = []

    @property
    def total_picks(self):
        return self.num_teams * self.rounds

    @property
    def next_overall(self):
        return len(self.picks) + 1

    @property
    def complete(self):
        return len(self.picks) >= self.total_picks

    def expected_slot_for_pick(self, overall: int):
        return team_slot_for_overall_pick(overall, self.num_teams)

    def record_pick(self, player_id: str, player_name: str,
                    position: str | None = None, nfl_team: str | None = None,
                    espn_id: int | None = None):
        if self.complete:
            raise ValueError("Draft is already complete.")

        overall = self.next_overall
        rnd, pick_in_round, team_slot = self.expected_slot_for_pick(overall)

        if any(p["player_id"] == player_id for p in self.picks):
            raise ValueError(f"Player already drafted: {player_id}")

        pick = {
            "overall": overall,
            "round": rnd,
            "pick_in_round": pick_in_round,
            "fantasy_team_slot": team_slot,
            "player_id": player_id,
            "player_name": player_name,
            "position": position,
            "nfl_team": nfl_team,
            "espn_id": espn_id,
        }
        self.picks.append(pick)
        return pick

    def undo_last_pick(self):
        if not self.picks:
            return None
        return self.picks.pop()

    def roster_for_slot(self, fantasy_team_slot: int):
        return [p for p in self.picks if p["fantasy_team_slot"] == fantasy_team_slot]

    def drafted_player_ids(self):
        return {p["player_id"] for p in self.picks}

    def to_dict(self):
        return {
            "num_teams": self.num_teams,
            "rounds": self.rounds,
            "user_draft_slot": self.user_draft_slot,
            "picks": self.picks,
        }

    @classmethod
    def from_dict(cls, d):
        state = cls(d["num_teams"], d["rounds"], d["user_draft_slot"])
        state.picks = list(d.get("picks", []))
        return state

    def save(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path):
        path = Path(path)
        return cls.from_dict(json.loads(path.read_text()))
