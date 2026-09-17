from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(frozen=True)
class Player:
    player_id: str
    name: str
    position: str
    nfl_team: str
    espn_id: Optional[str] = None
    bye_week: Optional[int] = None
    rookie: bool = False
    age: Optional[float] = None
    years_experience: Optional[int] = None


@dataclass(frozen=True)
class DraftPick:
    overall: int
    round: int
    pick_in_round: int
    fantasy_team_slot: int
    player_id: str
    player_name: str
    position: Optional[str] = None
    nfl_team: Optional[str] = None

    def to_dict(self):
        return asdict(self)
