from pathlib import Path

def test_fixed5_bootstrap_materialized_full_inherited_tree():
    root = Path(__file__).parents[1]
    assert (root / "tests" / "test_market_manager_v030.py").exists()
    assert (root / "tests" / "test_interaction_grid_v028.py").exists()
    assert (root / "src" / "specialist_policy_v032.py").exists()
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.35-fixed1"
