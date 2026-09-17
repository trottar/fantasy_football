from __future__ import annotations

from src.data_sources.nfl_official import parse_injuries_html, parse_transactions_html


def test_parse_nfl_transaction_table():
    html = """
    <table><thead><tr><th>From</th><th>To</th><th>Date</th><th>Name</th><th>Position</th><th>Transaction</th></tr></thead>
    <tbody><tr><td>Ravens</td><td>Giants</td><td>08/29</td><td>Test Player</td><td>RB</td><td>Traded</td></tr></tbody></table>
    """
    rows = parse_transactions_html(html)
    assert rows == [{
        "from": "Ravens", "to": "Giants", "date": "08/29", "name": "Test Player",
        "position": "RB", "transaction": "Traded"
    }]


def test_parse_nfl_injury_table_when_static_table_is_present():
    html = """
    <table><thead><tr><th>Player</th><th>Position</th><th>Injury</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Game Status</th></tr></thead>
    <tbody><tr><td>Player Q</td><td>WR</td><td>Hamstring</td><td>DNP</td><td>Limited</td><td>Full</td><td>Questionable</td></tr></tbody></table>
    """
    rows = parse_injuries_html(html)
    assert rows[0]["name"] == "Player Q"
    assert rows[0]["game_status"] == "Questionable"
    assert rows[0]["practice"]["Friday"] == "Full"


def test_dynamic_nfl_injury_page_without_table_is_supported():
    assert parse_injuries_html("<html><body><h1>Injuries</h1></body></html>") == []
