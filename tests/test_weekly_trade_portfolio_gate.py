from pathlib import Path
import subprocess
import sys


def test_frozen_portfolio_gate_synthetic():
    directory = Path(__file__).resolve().parent
    # Published source test lives under tests/, module under src/. This
    # synthetic fixture is run through package extraction during local apply.
    source = directory.parent / 'src' / 'weekly_trade_portfolio_gate.py'
    assert source.is_file()
    assert 'approved_recommendation_count' in source.read_text(encoding='utf-8')
    assert 'espn_action_authority' in source.read_text(encoding='utf-8')
