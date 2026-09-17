from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable

import pandas as pd


_PICK_PREFIX = re.compile(
    r"^\s*(?:pick\s*)?(?P<label>(?:\d+\.\d+)|(?:\d+))\s*[\).:\-–—]*\s*",
    re.IGNORECASE,
)
_NOISE = re.compile(
    r"^\s*(round\s+\d+|draft|overall|pick|team|player|pos(?:ition)?|on the clock)\s*$",
    re.IGNORECASE,
)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


@dataclass
class PastePreviewRow:
    line_no: int
    raw_text: str
    overall: int | None
    espn_id: int | None
    name: str | None
    position: str | None
    nfl_team: str | None
    status: str
    message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _overall_from_label(label: str | None, num_teams: int) -> int | None:
    if not label:
        return None
    if "." in label:
        rnd_s, pick_s = label.split(".", 1)
        try:
            rnd = int(rnd_s)
            pick_in_round = int(pick_s)
        except ValueError:
            return None
        if rnd < 1 or pick_in_round < 1 or pick_in_round > num_teams:
            return None
        return (rnd - 1) * num_teams + pick_in_round
    try:
        return int(label)
    except ValueError:
        return None


def _canonical_matches(line: str, board: pd.DataFrame) -> pd.DataFrame:
    normalized = _norm(line)
    if not normalized:
        return board.iloc[0:0]

    names = board["name"].fillna("").astype(str)
    norm_names = names.map(_norm)
    mask = norm_names.map(lambda n: bool(n) and n in normalized)
    matches = board[mask].copy()
    if len(matches) <= 1:
        return matches

    # Prefer the longest canonical name found in the line. This is robust to
    # copied ESPN rows that contain team/position columns after the name.
    matches["_name_len"] = matches["name"].map(lambda n: len(_norm(n)))
    max_len = matches["_name_len"].max()
    return matches[matches["_name_len"].eq(max_len)].drop(columns=["_name_len"])


def preview_pasted_picks(
    text: str,
    board: pd.DataFrame,
    start_overall: int,
    num_teams: int,
    drafted_espn_ids: Iterable[int] = (),
    drafted_picks_by_espn_id: dict[int, int] | None = None,
) -> list[PastePreviewRow]:
    """Parse copied draft text into a canonical preview.

    The parser is deliberately conservative. Noise/header lines are ignored;
    any meaningful line that cannot be resolved becomes an error. Commit code
    can therefore remain all-or-nothing and preserve exact draft order.
    """
    drafted = {int(x) for x in drafted_espn_ids}
    drafted_pick_map = {
        int(k): int(v)
        for k, v in (drafted_picks_by_espn_id or {}).items()
    }
    work = board.copy()
    work["espn_id"] = pd.to_numeric(work["espn_id"], errors="coerce").astype("Int64")

    rows: list[PastePreviewRow] = []
    expected = int(start_overall)
    seen_batch: set[int] = set()

    for line_no, raw in enumerate(str(text).splitlines(), start=1):
        line = raw.strip()
        if not line or _NOISE.match(line):
            continue

        m = _PICK_PREFIX.match(line)
        label = m.group("label") if m else None
        explicit_overall = _overall_from_label(label, num_teams)
        payload = line[m.end():].strip() if m else line

        matches = _canonical_matches(payload, work)
        if len(matches) == 0:
            # A line without a pick marker and without any canonical player is
            # probably copied UI noise, not a missing selection.
            if label is None:
                continue
            rows.append(PastePreviewRow(
                line_no=line_no,
                raw_text=raw,
                overall=explicit_overall or expected,
                espn_id=None,
                name=None,
                position=None,
                nfl_team=None,
                status="error",
                message="No canonical ESPN player match",
            ))
            expected += 1
            continue

        # Resolve the canonical player before validating pick sequence. This
        # allows a pasted "recent picks" window to overlap the picks already
        # stored in DraftState without forcing the user to trim old lines.
        if len(matches) > 1:
            overall = explicit_overall or expected
            names = ", ".join(str(x) for x in matches["name"].tolist())
            rows.append(PastePreviewRow(
                line_no=line_no,
                raw_text=raw,
                overall=overall,
                espn_id=None,
                name=None,
                position=None,
                nfl_team=None,
                status="error",
                message=f"Ambiguous canonical match: {names}",
            ))
            expected += 1
            continue

        player = matches.iloc[0]
        espn_id = int(player["espn_id"])

        if espn_id in drafted:
            recorded_overall = drafted_pick_map.get(espn_id)
            # If we know the original pick, an explicit conflicting pick number
            # is a real data problem rather than a harmless overlap.
            if (
                explicit_overall is not None
                and recorded_overall is not None
                and explicit_overall != recorded_overall
            ):
                rows.append(PastePreviewRow(
                    line_no=line_no,
                    raw_text=raw,
                    overall=explicit_overall,
                    espn_id=espn_id,
                    name=str(player["name"]),
                    position=str(player.get("position") or ""),
                    nfl_team=str(player.get("nfl_team") or ""),
                    status="error",
                    message=(
                        f"Already recorded at pick {recorded_overall}; "
                        f"pasted line says {explicit_overall}"
                    ),
                ))
            else:
                rows.append(PastePreviewRow(
                    line_no=line_no,
                    raw_text=raw,
                    overall=recorded_overall or explicit_overall,
                    espn_id=espn_id,
                    name=str(player["name"]),
                    position=str(player.get("position") or ""),
                    nfl_team=str(player.get("nfl_team") or ""),
                    status="already_recorded",
                    message=(
                        f"Already recorded at pick {recorded_overall}"
                        if recorded_overall is not None
                        else "Already recorded"
                    ),
                ))
            # Crucially, an overlap does NOT consume the next expected new pick.
            continue

        overall = explicit_overall or expected
        if explicit_overall is not None and explicit_overall != expected:
            rows.append(PastePreviewRow(
                line_no=line_no,
                raw_text=raw,
                overall=explicit_overall,
                espn_id=None,
                name=None,
                position=None,
                nfl_team=None,
                status="error",
                message=f"Expected overall pick {expected}, pasted line says {explicit_overall}",
            ))
            expected += 1
            continue

        if espn_id in seen_batch:
            status = "error"
            message = "Player appears more than once in pasted batch"
        else:
            status = "resolved"
            message = ""
            seen_batch.add(espn_id)

        rows.append(PastePreviewRow(
            line_no=line_no,
            raw_text=raw,
            overall=overall,
            espn_id=espn_id,
            name=str(player["name"]),
            position=str(player.get("position") or ""),
            nfl_team=str(player.get("nfl_team") or ""),
            status=status,
            message=message,
        ))
        expected += 1

    return rows


def preview_is_committable(rows: Iterable[PastePreviewRow]) -> bool:
    """True when every row is either new/resolved or a harmless overlap.

    At least one genuinely new row is required; a preview containing only
    already-recorded picks is a no-op and therefore not committable.
    """
    rows = list(rows)
    allowed = {"resolved", "already_recorded"}
    return (
        bool(rows)
        and all(r.status in allowed for r in rows)
        and any(r.status == "resolved" for r in rows)
    )


def remove_already_recorded(
    rows: Iterable[PastePreviewRow],
) -> tuple[list[PastePreviewRow], int]:
    rows = list(rows)
    kept = [r for r in rows if r.status != "already_recorded"]
    return kept, len(rows) - len(kept)
