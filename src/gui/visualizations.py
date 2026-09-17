from __future__ import annotations

import math
import pandas as pd


_POSITION_COLORS = {
    "RB": "#5470c6",
    "WR": "#91cc75",
    "TE": "#fac858",
    "QB": "#ee6666",
}


def _finite(x, default=0.0):
    try:
        x = float(x)
        return x if math.isfinite(x) else default
    except (TypeError, ValueError):
        return default


def value_survival_options(df: pd.DataFrame, target_pick: int | None) -> dict:
    series = []
    for pos in ["RB", "WR", "TE", "QB"]:
        g = df[df["position"].eq(pos)]
        data = []
        for _, r in g.iterrows():
            p = _finite(r.get("p_survive"), 0.0) * 100.0
            value = _finite(r.get("dynamic_draft_value"), 0.0)
            tier = int(r.get("tier")) if pd.notna(r.get("tier")) else "?"
            data.append({
                "value": [p, value],
                "name": f'{r.get("name", "")} · T{tier} · ADP {_finite(r.get("espn_adp"), 0.0):.1f}',
            })
        series.append({
            "name": pos,
            "type": "scatter",
            "symbolSize": 13,
            "itemStyle": {"color": _POSITION_COLORS[pos]},
            "data": data,
        })

    return {
        "animation": False,
        "tooltip": {"trigger": "item"},
        "legend": {"top": 0},
        "grid": {"left": 55, "right": 25, "top": 45, "bottom": 55},
        "xAxis": {
            "type": "value",
            "min": 0,
            "max": 100,
            "name": f"P(available at pick {target_pick})" if target_pick else "Survival probability",
            "nameLocation": "middle",
            "nameGap": 34,
            "axisLabel": {"formatter": "{value}%"},
        },
        "yAxis": {
            "type": "value",
            "name": "Dynamic draft value",
            "nameLocation": "middle",
            "nameGap": 42,
        },
        "series": series,
    }


def tier_heatmap_options(df: pd.DataFrame) -> dict:
    positions = ["RB", "WR", "TE", "QB"]
    max_rank = int(df["visual_rank"].max()) if len(df) else 1
    data = []
    values = []

    for _, r in df.iterrows():
        x = int(r["visual_rank"]) - 1
        y = positions.index(str(r["position"]))
        val = _finite(r.get("dynamic_draft_value"), 0.0)
        values.append(val)
        tier = int(r.get("tier")) if pd.notna(r.get("tier")) else "?"
        data.append({
            "value": [x, y, val],
            "name": f'{r.get("name", "")} · T{tier} · ADP {_finite(r.get("espn_adp"), 0.0):.1f}',
        })

    vmax = max(values) if values else 1.0
    vmin = min(values) if values else 0.0
    return {
        "animation": False,
        "tooltip": {"trigger": "item"},
        "grid": {"left": 50, "right": 20, "top": 10, "bottom": 45},
        "xAxis": {
            "type": "category",
            "data": [str(i) for i in range(1, max_rank + 1)],
            "name": "Available positional rank",
            "nameLocation": "middle",
            "nameGap": 28,
            "splitArea": {"show": True},
        },
        "yAxis": {
            "type": "category",
            "data": positions,
            "splitArea": {"show": True},
        },
        "visualMap": {
            "min": vmin,
            "max": vmax,
            "calculable": False,
            "orient": "horizontal",
            "left": "center",
            "bottom": 0,
            "show": False,
        },
        "series": [{
            "name": "Draft value",
            "type": "heatmap",
            "data": data,
            "label": {"show": False},
            "emphasis": {"itemStyle": {"shadowBlur": 6}},
        }],
    }
