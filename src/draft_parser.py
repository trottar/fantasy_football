from __future__ import annotations

import csv
import io
import re


def parse_simple_picks(text: str):
    """Parse a deliberately simple fallback format.

    Accepted examples:
        12,Player Name,WR,PIT
        13 Player Name
        Player Name

    This is *not* the final ESPN parser. Mock-draft copy/paste samples will be
    used to harden this module without changing the optimizer interface.
    """
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if "," in line:
            row = next(csv.reader(io.StringIO(line)))
            row = [x.strip() for x in row]
            if row[0].isdigit():
                row = row[1:]
            if not row:
                continue
            item = {"name": row[0]}
            if len(row) > 1:
                item["position"] = row[1] or None
            if len(row) > 2:
                item["nfl_team"] = row[2] or None
            out.append(item)
            continue

        m = re.match(r"^\s*\d+[.)]?\s+(.*)$", line)
        if m:
            line = m.group(1).strip()

        out.append({"name": line})

    return out
