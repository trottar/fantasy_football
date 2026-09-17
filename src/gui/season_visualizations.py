from __future__ import annotations

from typing import Any


def _hist_data(hist: list[dict[str, float]]) -> list[list[float]]:
    return [[round(float(r["x"]), 3), float(r["count"])] for r in hist]


def multi_distribution_options(
    series: list[tuple[str, list[dict[str, float]]]],
    *,
    title: str,
    x_name: str = "Fantasy points",
) -> dict[str, Any]:
    names = [name for name, _ in series]
    return {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "legend": {"top": 28, "data": names},
        "grid": {"left": 48, "right": 20, "top": 65, "bottom": 42},
        "xAxis": {"type": "value", "name": x_name, "nameLocation": "middle", "nameGap": 28},
        "yAxis": {"type": "value", "name": "MC count"},
        "series": [
            {
                "name": name,
                "type": "line",
                "smooth": True,
                "showSymbol": False,
                "data": _hist_data(hist),
            }
            for name, hist in series
        ],
    }


def distribution_overlay_options(
    user_hist: list[dict[str, float]],
    opponent_hist: list[dict[str, float]],
    *,
    title: str = "Projected weekly score distribution",
) -> dict[str, Any]:
    return multi_distribution_options(
        [("Us", user_hist), ("Opponent", opponent_hist)],
        title=title,
    )


def lineup_lab_distribution_options(
    selected_hist: list[dict[str, float]],
    fixed_baseline_hist: list[dict[str, float]],
    opponent_hist: list[dict[str, float]],
) -> dict[str, Any]:
    return multi_distribution_options(
        [("Selected", selected_hist), ("Default fixed", fixed_baseline_hist), ("Opponent", opponent_hist)],
        title="Selected lineup vs fixed baseline vs opponent",
    )


def margin_distribution_options(hist: list[dict[str, float]], *, title: str = "Matchup margin MC") -> dict[str, Any]:
    data = _hist_data(hist)
    return {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 48, "right": 20, "top": 45, "bottom": 42},
        "xAxis": {"type": "value", "name": "Us − opponent", "nameLocation": "middle", "nameGap": 28},
        "yAxis": {"type": "value", "name": "MC count"},
        "series": [{"type": "bar", "data": data, "barMaxWidth": 18}],
    }


def matchup_slot_delta_options(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [str(r.get("slot") or "?") for r in rows]
    values = [round(float(r.get("delta") or 0.0), 3) for r in rows]
    names = [
        f"{r.get('us_name') or '-'} vs {r.get('opponent_name') or '-'}"
        for r in rows
    ]
    return {
        "title": {"text": "Starter-by-starter projection edge", "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
        },
        "grid": {"left": 62, "right": 24, "top": 45, "bottom": 30},
        "xAxis": {"type": "value", "name": "Our projection − opponent (pts)"},
        "yAxis": {"type": "category", "data": labels},
        "series": [{"type": "bar", "data": values, "name": "Projection edge"}],
        "dataset_meta": {"matchups": names},
    }


def player_prediction_options(diag: dict[str, Any]) -> dict[str, Any]:
    operational = diag.get("operational_mean")
    interaction_delta = float(diag.get("interaction_delta_ppg") or 0.0)
    base_mc = None if operational is None else float(operational) - interaction_delta
    labels = ["Base model", "K-adjusted", "ESPN anchor", "Base MC", "Interaction-corrected"]
    values = [
        diag.get("model_mean"),
        diag.get("matchup_model_mean"),
        diag.get("espn_anchor"),
        base_mc,
        operational,
    ]
    data = [0.0 if v is None else float(v) for v in values]
    return {
        "title": {"text": "Prediction chain", "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 95, "right": 24, "top": 45, "bottom": 30},
        "xAxis": {"type": "value", "name": "Fantasy points"},
        "yAxis": {"type": "category", "data": labels},
        "series": [{"type": "bar", "data": data, "label": {"show": True, "position": "right", "formatter": "{c}"}}],
    }


def uncertainty_breakdown_options(diag: dict[str, Any]) -> dict[str, Any]:
    labels = ["Game", "Model", "Kinematics", "Interaction grid"]
    values = [
        float(diag.get("game_sd") or 0.0),
        float(diag.get("model_sd") or 0.0),
        float(diag.get("kinematic_sd") or 0.0),
        float(diag.get("interaction_sd_ppg") or 0.0),
    ]
    return {
        "title": {"text": "Predictive uncertainty components", "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 100, "right": 24, "top": 45, "bottom": 30},
        "xAxis": {"type": "value", "name": "SD (fantasy points)"},
        "yAxis": {"type": "category", "data": labels},
        "series": [{"type": "bar", "data": values, "label": {"show": True, "position": "right"}}],
    }


def component_bar_options(diag: dict[str, Any]) -> dict[str, Any]:
    components = diag.get("kinematic_components") or {}
    items = sorted(((str(k), float(v)) for k, v in components.items()), key=lambda kv: abs(kv[1]), reverse=True)
    if not items:
        items = [("neutral", 0.0)]
    return {
        "title": {"text": "Matchup contribution coordinates", "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 135, "right": 24, "top": 45, "bottom": 30},
        "xAxis": {"type": "value", "name": "log-adjustment"},
        "yAxis": {"type": "category", "data": [k for k, _ in items]},
        "series": [{"type": "bar", "data": [v for _, v in items], "label": {"show": True, "position": "right", "formatter": "{c}"}}],
    }


def action_delta_options(hist: list[dict[str, float]]) -> dict[str, Any]:
    data = _hist_data(hist)
    return {
        "title": {"text": "Paired action Δutility", "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 48, "right": 20, "top": 45, "bottom": 42},
        "xAxis": {"type": "value", "name": "Δ H2H utility (pp)", "nameLocation": "middle", "nameGap": 28},
        "yAxis": {"type": "value", "name": "MC count"},
        "series": [{"type": "bar", "data": data, "barMaxWidth": 18}],
    }


def action_week_overlay_options(
    baseline_hist: list[dict[str, float]],
    action_hist: list[dict[str, float]],
) -> dict[str, Any]:
    return multi_distribution_options(
        [("HOLD", baseline_hist), ("Action", action_hist)],
        title="Current-week HOLD vs action",
    )


def model_espn_scatter_options(rows: list[dict[str, Any]]) -> dict[str, Any]:
    points = []
    for r in rows:
        model = r.get("model")
        espn = r.get("espn")
        if model is None or espn is None:
            continue
        points.append([float(espn), float(model), str(r.get("name") or "")])
    if points:
        vals = [p[0] for p in points] + [p[1] for p in points]
        lo = min(vals)
        hi = max(vals)
        pad = max((hi - lo) * 0.08, 0.5)
        lo -= pad
        hi += pad
    else:
        lo, hi = 0.0, 1.0
    return {
        "title": {"text": "Base model vs ESPN anchor", "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "item"},
        "grid": {"left": 55, "right": 24, "top": 45, "bottom": 50},
        "xAxis": {"type": "value", "name": "ESPN projection", "min": lo, "max": hi, "nameLocation": "middle", "nameGap": 30},
        "yAxis": {"type": "value", "name": "Our base model", "min": lo, "max": hi},
        "series": [
            {
                "name": "Players",
                "type": "scatter",
                "data": points,
                "symbolSize": 10,
            },
            {
                "name": "1:1",
                "type": "line",
                "showSymbol": False,
                "silent": True,
                "data": [[lo, lo], [hi, hi]],
            },
        ],
    }


def closure_residual_options(rows: list[dict[str, Any]]) -> dict[str, Any]:
    observed = [r for r in rows if r.get("observed") is not None and r.get("operational") is not None]
    if observed:
        title = "Observed − operational MC residuals"
        pairs = [(str(r.get("name") or ""), float(r["observed"]) - float(r["operational"])) for r in observed]
    else:
        title = "Largest base-model − ESPN residuals"
        pairs = [
            (str(r.get("name") or ""), float(r["model_minus_espn"]))
            for r in rows
            if r.get("model_minus_espn") is not None
        ]
    pairs.sort(key=lambda kv: abs(kv[1]), reverse=True)
    pairs = pairs[:16]
    if not pairs:
        pairs = [("No comparable rows", 0.0)]
    # reverse so the largest appears at the top of a horizontal chart
    pairs = list(reversed(pairs))
    return {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 150, "right": 24, "top": 45, "bottom": 30},
        "xAxis": {"type": "value", "name": "Fantasy points"},
        "yAxis": {"type": "category", "data": [name for name, _ in pairs]},
        "series": [{"type": "bar", "data": [value for _, value in pairs]}],
    }
