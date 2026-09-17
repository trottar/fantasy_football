from __future__ import annotations

import json
import re
from io import StringIO
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import pandas as pd
import requests

TRANSACTIONS_URL = "https://www.nfl.com/transactions/"
INJURIES_URL = "https://www.nfl.com/injuries/"
TRANSACTION_CATEGORIES = ("trades", "signings", "reserve-list", "waivers", "terminations")


def _headers() -> dict[str, str]:
    return {
        "Accept": "text/html,application/xhtml+xml",
        "User-Agent": "Mozilla/5.0 fantasy-season-manager/0.22 (personal analytics project)",
    }


def fetch_html(url: str, timeout: int = 45) -> str:
    response = requests.get(url, headers=_headers(), timeout=timeout)
    response.raise_for_status()
    return response.text


def _flat_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = [" ".join(str(x) for x in col if str(x) != "nan").strip() for col in out.columns]
    else:
        out.columns = [str(x).strip() for x in out.columns]
    return out


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def parse_transactions_html(html: str) -> list[dict[str, Any]]:
    try:
        tables = pd.read_html(StringIO(html), flavor="lxml")
    except ValueError:
        return []
    rows: list[dict[str, Any]] = []
    for table in tables:
        df = _flat_columns(table)
        lower = {c.casefold(): c for c in df.columns}
        if "name" not in lower or "transaction" not in lower or "date" not in lower:
            continue
        for record in df.to_dict("records"):
            rows.append({
                "from": _clean_text(record.get(lower.get("from"))) if lower.get("from") else None,
                "to": _clean_text(record.get(lower.get("to"))) if lower.get("to") else None,
                "date": _clean_text(record.get(lower["date"])),
                "name": _clean_text(record.get(lower["name"])),
                "position": _clean_text(record.get(lower.get("position"))) if lower.get("position") else None,
                "transaction": _clean_text(record.get(lower["transaction"])),
            })
    # De-duplicate if responsive/mobile tables both appear in the HTML.
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = tuple(row.get(k) for k in ("date", "name", "from", "to", "transaction"))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _find_col(columns: list[str], *terms: str) -> str | None:
    for col in columns:
        low = col.casefold()
        if all(term.casefold() in low for term in terms):
            return col
    return None


def parse_injuries_html(html: str) -> list[dict[str, Any]]:
    """Best-effort parser for public NFL.com injury tables.

    NFL.com renders this page dynamically in some layouts. Zero parsed rows is a
    supported outcome and never overrides ESPN/Sleeper status. Raw HTML is retained
    so the parser can be adapted once a live weekly table is visible.
    """
    try:
        tables = pd.read_html(StringIO(html), flavor="lxml")
    except ValueError:
        return []
    out: list[dict[str, Any]] = []
    for table in tables:
        df = _flat_columns(table)
        cols = list(df.columns)
        player_col = _find_col(cols, "player") or _find_col(cols, "name")
        injury_col = _find_col(cols, "injury")
        if not player_col or not injury_col:
            continue
        # Only a true Game Status column is authoritative for availability. A generic
        # "Status" column can mean practice participation or roster status.
        status_col = _find_col(cols, "game", "status")
        team_col = _find_col(cols, "team")
        pos_col = _find_col(cols, "position") or _find_col(cols, "pos")
        practice_cols = [c for c in cols if any(day in c.casefold() for day in ("wed", "thu", "fri", "sat"))]
        for record in df.to_dict("records"):
            name = _clean_text(record.get(player_col))
            if not name:
                continue
            practice = {
                c: _clean_text(record.get(c)) for c in practice_cols if _clean_text(record.get(c))
            }
            out.append({
                "name": name,
                "team": _clean_text(record.get(team_col)) if team_col else None,
                "position": _clean_text(record.get(pos_col)) if pos_col else None,
                "injury": _clean_text(record.get(injury_col)),
                "game_status": _clean_text(record.get(status_col)) if status_col else None,
                "practice": practice,
            })
    return out


def sync_nfl_official(out_dir: str | Path) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    all_transactions: list[dict[str, Any]] = []
    category_status: dict[str, Any] = {}
    for category in TRANSACTION_CATEGORIES:
        url = f"https://www.nfl.com/transactions/league/{category}/{now.year}/{now.month}"
        try:
            html = fetch_html(url)
            (out_dir / f"transactions_{category}.html").write_text(html, encoding="utf-8")
            rows = parse_transactions_html(html)
            for row in rows:
                row["category"] = category
                row["source_url"] = url
            all_transactions.extend(rows)
            category_status[category] = {"ok": True, "url": url, "rows": len(rows)}
        except Exception as exc:
            category_status[category] = {
                "ok": False, "url": url, "rows": 0, "error": f"{type(exc).__name__}: {exc}"
            }

    seen: set[tuple[Any, ...]] = set()
    transactions: list[dict[str, Any]] = []
    for row in all_transactions:
        key = tuple(row.get(k) for k in ("date", "name", "from", "to", "transaction"))
        if key in seen:
            continue
        seen.add(key)
        transactions.append(row)
    (out_dir / "transactions.json").write_text(json.dumps(transactions, indent=2), encoding="utf-8")

    injuries: list[dict[str, Any]] = []
    injury_status: dict[str, Any]
    try:
        injury_html = fetch_html(INJURIES_URL)
        (out_dir / "injuries.html").write_text(injury_html, encoding="utf-8")
        injuries = parse_injuries_html(injury_html)
        injury_status = {"ok": True, "url": INJURIES_URL, "rows": len(injuries), "parser_active": bool(injuries)}
    except Exception as exc:
        injury_status = {
            "ok": False, "url": INJURIES_URL, "rows": 0, "parser_active": False,
            "error": f"{type(exc).__name__}: {exc}"
        }
    (out_dir / "injuries.json").write_text(json.dumps(injuries, indent=2), encoding="utf-8")

    return {
        "transactions": transactions,
        "transaction_categories": category_status,
        "injuries": injuries,
        "injury_status": injury_status,
        "transactions_url": TRANSACTIONS_URL,
        "injuries_url": INJURIES_URL,
        "notes": [
            "NFL.com transaction category pages are public HTML; raw pages are retained because the layout is undocumented.",
            "The injury page is dynamically rendered in some layouts. Zero parsed injury rows is explicitly non-authoritative and does not override ESPN/Sleeper."
        ],
    }
