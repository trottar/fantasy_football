from src.scoring import score_offense, score_kicker, score_dst


def test_full_ppr_receiver():
    stats = {"rec": 8, "rec_yds": 100, "rec_td": 1}
    assert score_offense(stats) == 24.0


def test_qb():
    stats = {"pass_yds": 300, "pass_td": 2, "pass_int": 1}
    assert score_offense(stats) == 18.0


def test_kicker():
    stats = {"pat_made": 3, "fg_0_39": 1, "fg_50_59": 1, "fg_missed": 1}
    assert score_kicker(stats) == 10.0


def test_dst_points_and_yards():
    stats = {
        "sacks": 4,
        "interceptions": 2,
        "fumble_recoveries": 1,
        "points_allowed": 10,
        "yards_allowed": 280,
    }
    # 4 sacks + 4 INT + 2 FR + 3 PA + 2 YA = 15
    assert score_dst(stats) == 15.0
