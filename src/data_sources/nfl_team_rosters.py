from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import requests

NFL_TEAM_SLUGS = {
    "ARI": "arizona-cardinals",
    "ATL": "atlanta-falcons",
    "BAL": "baltimore-ravens",
    "BUF": "buffalo-bills",
    "CAR": "carolina-panthers",
    "CHI": "chicago-bears",
    "CIN": "cincinnati-bengals",
    "CLE": "cleveland-browns",
    "DAL": "dallas-cowboys",
    "DEN": "denver-broncos",
    "DET": "detroit-lions",
    "GB": "green-bay-packers",
    "HOU": "houston-texans",
    "IND": "indianapolis-colts",
    "JAX": "jacksonville-jaguars",
    "KC": "kansas-city-chiefs",
    "LV": "las-vegas-raiders",
    "LAC": "los-angeles-chargers",
    "LAR": "los-angeles-rams",
    "MIA": "miami-dolphins",
    "MIN": "minnesota-vikings",
    "NE": "new-england-patriots",
    "NO": "new-orleans-saints",
    "NYG": "new-york-giants",
    "NYJ": "new-york-jets",
    "PHI": "philadelphia-eagles",
    "PIT": "pittsburgh-steelers",
    "SEA": "seattle-seahawks",
    "SF": "san-francisco-49ers",
    "TB": "tampa-bay-buccaneers",
    "TEN": "tennessee-titans",
    "WAS": "washington-commanders",
}


def _headers() -> dict[str, str]:
    return {
        "Accept": "text/html,application/xhtml+xml",
        "User-Agent": "Mozilla/5.0 fantasy-season-manager/0.22 (personal analytics project)",
    }


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _flat_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = [" ".join(str(x) for x in col if str(x) != "nan").strip() for col in out.columns]
    else:
        out.columns = [str(x).strip() for x in out.columns]
    return out


def _column(columns: list[str], *terms: str) -> str | None:
    for col in columns:
        low = col.casefold()
        if all(term.casefold() in low for term in terms):
            return col
    return None


def parse_team_roster_html(html: str, team_abbr: str) -> list[dict[str, Any]]:
    """Parse the public NFL.com team roster table.

    The page is undocumented HTML, so this parser is deliberately narrow: a table
    must contain player/name plus position and status. A failed parse returns zero
    rows and never overrides lower-priority sources.
    """
    try:
        tables = pd.read_html(StringIO(html), flavor="lxml")
    except ValueError:
        return []

    rows: list[dict[str, Any]] = []
    for table in tables:
        df = _flat_columns(table)
        cols = list(df.columns)
        player_col = _column(cols, "player") or _column(cols, "name")
        pos_col = _column(cols, "pos") or _column(cols, "position")
        status_col = _column(cols, "status")
        if not player_col or not pos_col or not status_col:
            continue
        no_col = _column(cols, "no") or _column(cols, "number")
        for record in df.to_dict("records"):
            name = _clean(record.get(player_col))
            if not name:
                continue
            rows.append({
                "name": name,
                "team": str(team_abbr).upper(),
                "position": _clean(record.get(pos_col)),
                "status": (_clean(record.get(status_col)) or "").upper() or None,
                "number": _clean(record.get(no_col)) if no_col else None,
            })
    # Responsive/mobile markup can duplicate the same table.
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = (row.get("team"), row.get("name"), row.get("position"), row.get("status"))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _fetch_one(team: str, slug: str, timeout: int) -> tuple[str, str, str, list[dict[str, Any]]]:
    url = f"https://www.nfl.com/teams/{slug}/roster"
    response = requests.get(url, headers=_headers(), timeout=timeout)
    response.raise_for_status()
    html = response.text
    return team, url, html, parse_team_roster_html(html, team)


def sync_nfl_team_rosters(
    out_dir: str | Path,
    timeout: int = 45,
    max_workers: int = 8,
) -> dict[str, Any]:
    """Fetch all 32 public NFL.com team roster pages once per season sync.

    This is intentionally low-frequency (normally once/day). Team roster pages are
    used as the highest-priority current NFL roster-status observation because they
    expose states such as ACT/CUT/RLS that can lag in fantasy metadata.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    status: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=max(1, int(max_workers))) as pool:
        futures = {
            pool.submit(_fetch_one, team, slug, int(timeout)): team
            for team, slug in NFL_TEAM_SLUGS.items()
        }
        for future in as_completed(futures):
            team = futures[future]
            slug = NFL_TEAM_SLUGS[team]
            url = f"https://www.nfl.com/teams/{slug}/roster"
            try:
                team2, url2, html, rows = future.result()
                (out_dir / f"{team2}.html").write_text(html, encoding="utf-8")
                for row in rows:
                    row["source_url"] = url2
                all_rows.extend(rows)
                status[team2] = {"ok": True, "url": url2, "rows": len(rows)}
            except Exception as exc:
                status[team] = {
                    "ok": False,
                    "url": url,
                    "rows": 0,
                    "error": f"{type(exc).__name__}: {exc}",
                }

    all_rows.sort(key=lambda r: (str(r.get("team")), str(r.get("name"))))
    (out_dir / "team_rosters.json").write_text(json.dumps(all_rows, indent=2), encoding="utf-8")
    ok = sum(1 for x in status.values() if x.get("ok"))
    parsed = sum(1 for x in status.values() if x.get("ok") and int(x.get("rows") or 0) > 0)
    return {
        "rows": all_rows,
        "team_status": status,
        "fetches_ok": ok,
        "fetches_total": len(NFL_TEAM_SLUGS),
        "parsed_teams": parsed,
        "total_rows": len(all_rows),
        "complete": ok == len(NFL_TEAM_SLUGS) and parsed == len(NFL_TEAM_SLUGS),
    }
