from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROUND_LINE = re.compile(r"R(\d+),\s*P(\d+)\s*-\s*(.+?)\s*$", re.I)
LEADING_OVERALL = re.compile(r"^\s*\d+\.\s*")


def parse_espn_mock_markdown(text: str, num_teams: int = 12) -> pd.DataFrame:
    """Parse ESPN completed-draft markdown copied from the draft results page."""
    lines = str(text).splitlines()
    rows = []
    for i, line in enumerate(lines):
        m = ROUND_LINE.search(line.strip())
        if not m:
            continue
        rnd = int(m.group(1))
        round_pick = int(m.group(2))
        fantasy_team_name = m.group(3).strip()

        j = i - 1
        player_line = None
        while j >= 0:
            s = lines[j].strip()
            if not s or "[image]" in s:
                j -= 1
                continue
            player_line = s
            break
        if not player_line or " / " not in player_line:
            continue

        player_text, rhs = player_line.rsplit(" / ", 1)
        player_name = LEADING_OVERALL.sub("", player_text.strip())
        rhs = rhs.strip()
        if rhs.upper().endswith("D/ST"):
            position = "DST"
            nfl_team = rhs[:-4].strip()
        else:
            parts = rhs.split()
            nfl_team = parts[0] if parts else ""
            position = " ".join(parts[1:]) if len(parts) > 1 else ""
            # ESPN can display hybrid eligibility such as WR, CB. Fantasy
            # draft modeling uses the offensive fantasy position.
            if "," in position:
                position = position.split(",", 1)[0].strip()

        rows.append({
            "overall": (rnd - 1) * int(num_teams) + round_pick,
            "round": rnd,
            "round_pick": round_pick,
            "fantasy_team_name": fantasy_team_name,
            "player_name": player_name,
            "nfl_team": nfl_team,
            "position": position,
        })

    df = pd.DataFrame(rows)
    if len(df):
        df = df.sort_values("overall").drop_duplicates("overall", keep="first").reset_index(drop=True)
    return df


def mock_draft_summary(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {"picks": 0, "rounds": 0, "position_counts": {}, "round_position_counts": {}}
    pos_counts = df["position"].value_counts().to_dict()
    round_counts = (
        df.groupby(["round", "position"]).size().unstack(fill_value=0).to_dict(orient="index")
    )
    return {
        "picks": int(len(df)),
        "rounds": int(df["round"].max()),
        "position_counts": {str(k): int(v) for k, v in pos_counts.items()},
        "round_position_counts": {
            str(int(r)): {str(k): int(v) for k, v in row.items()}
            for r, row in round_counts.items()
        },
    }


def save_mock_draft(markdown_path: str | Path, out_dir: str | Path, num_teams: int = 12) -> tuple[Path, Path]:
    markdown_path = Path(markdown_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = parse_espn_mock_markdown(markdown_path.read_text(encoding="utf-8"), num_teams=num_teams)
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", markdown_path.stem)
    csv_path = out_dir / f"{stem}.csv"
    json_path = out_dir / f"{stem}_summary.json"
    df.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(mock_draft_summary(df), indent=2))
    return csv_path, json_path


def calibration_inventory(out_dir: str | Path) -> dict:
    out_dir = Path(out_dir)
    drafts = []
    for path in sorted(out_dir.glob("*.csv")):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        drafts.append({
            "file": path.name,
            "picks": int(len(df)),
            "rounds": int(pd.to_numeric(df.get("round"), errors="coerce").max()) if len(df) else 0,
        })
    return {"draft_count": len(drafts), "drafts": drafts}
