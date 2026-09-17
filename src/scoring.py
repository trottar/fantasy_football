from __future__ import annotations


def _dst_points_allowed(points_allowed: float) -> float:
    if points_allowed == 0:
        return 5.0
    if points_allowed <= 6:
        return 4.0
    if points_allowed <= 13:
        return 3.0
    if points_allowed <= 17:
        return 1.0
    if points_allowed <= 27:
        return 0.0
    if points_allowed <= 34:
        return -1.0
    if points_allowed <= 45:
        return -3.0
    return -5.0


def _dst_yards_allowed(yards_allowed: float) -> float:
    if yards_allowed < 100:
        return 5.0
    if yards_allowed <= 199:
        return 3.0
    if yards_allowed <= 299:
        return 2.0
    if yards_allowed <= 349:
        return 0.0
    if yards_allowed <= 399:
        return -1.0
    if yards_allowed <= 449:
        return -3.0
    if yards_allowed <= 499:
        return -5.0
    if yards_allowed <= 549:
        return -6.0
    return -7.0


def score_offense(stats: dict) -> float:
    """Score QB/RB/WR/TE statistics using the league's ESPN rules.

    Expected keys are optional and default to zero:
      pass_yds, pass_td, pass_int, pass_2pt
      rush_yds, rush_td, rush_2pt
      rec, rec_yds, rec_td, rec_2pt
      fumbles_lost
      kickoff_return_td, punt_return_td, fumble_recovery_td
    """
    s = stats
    return (
        0.04 * s.get("pass_yds", 0)
        + 4.0 * s.get("pass_td", 0)
        - 2.0 * s.get("pass_int", 0)
        + 2.0 * s.get("pass_2pt", 0)
        + 0.1 * s.get("rush_yds", 0)
        + 6.0 * s.get("rush_td", 0)
        + 2.0 * s.get("rush_2pt", 0)
        + 1.0 * s.get("rec", 0)
        + 0.1 * s.get("rec_yds", 0)
        + 6.0 * s.get("rec_td", 0)
        + 2.0 * s.get("rec_2pt", 0)
        - 2.0 * s.get("fumbles_lost", 0)
        + 6.0 * s.get("kickoff_return_td", 0)
        + 6.0 * s.get("punt_return_td", 0)
        + 6.0 * s.get("fumble_recovery_td", 0)
    )


def score_kicker(stats: dict) -> float:
    s = stats
    return (
        1.0 * s.get("pat_made", 0)
        - 1.0 * s.get("fg_missed", 0)
        + 3.0 * s.get("fg_0_39", 0)
        + 4.0 * s.get("fg_40_49", 0)
        + 5.0 * s.get("fg_50_59", 0)
        + 5.0 * s.get("fg_60_plus", 0)
    )


def score_dst(stats: dict) -> float:
    s = stats
    score = (
        6.0 * s.get("kickoff_return_td", 0)
        + 6.0 * s.get("punt_return_td", 0)
        + 6.0 * s.get("interception_return_td", 0)
        + 6.0 * s.get("fumble_return_td", 0)
        + 6.0 * s.get("blocked_kick_return_td", 0)
        + 2.0 * s.get("two_point_return", 0)
        + 1.0 * s.get("one_point_safety", 0)
        + 1.0 * s.get("sacks", 0)
        + 2.0 * s.get("blocked_kicks", 0)
        + 2.0 * s.get("interceptions", 0)
        + 2.0 * s.get("fumble_recoveries", 0)
        + 2.0 * s.get("safeties", 0)
    )
    if "points_allowed" in s:
        score += _dst_points_allowed(float(s["points_allowed"]))
    if "yards_allowed" in s:
        score += _dst_yards_allowed(float(s["yards_allowed"]))
    return score
