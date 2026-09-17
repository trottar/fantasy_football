from pathlib import Path


def test_v034_bootstrap_materialized_commissioned_v033_fixed2_tree():
    root = Path(__file__).parents[1]
    assert (root / "tests" / "test_market_manager_v030.py").exists()
    assert (root / "tests" / "test_specialist_temporal_v033.py").exists()
    assert (root / "tests" / "test_prospective_measurement_v034.py").exists()
    assert (root / "src" / "specialist_temporal_v033.py").exists()
    assert (root / "src" / "prospective_measurement_v034.py").exists()
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.35-fixed1"
