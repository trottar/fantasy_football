from pathlib import Path

def test_roster_children_are_rendered_inside_clearable_container():
    app = Path(__file__).parents[1] / "src" / "gui" / "app.py"
    text = app.read_text()
    start = text.index("    def render_roster() -> None:")
    end = text.index("\n    def render_recent()", start)
    block = text[start:end]
    assert "roster_container.clear()" in block
    assert "with roster_container:" in block
