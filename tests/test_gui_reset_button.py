from pathlib import Path


def test_gui_has_confirmed_new_mock_reset_control():
    app = Path(__file__).parents[1] / "src" / "gui" / "app.py"
    text = app.read_text()
    assert "New Mock / Reset Draft" in text
    assert "Reset current mock draft?" in text
    assert "reset_confirm_button.on_click(reset_current_draft)" in text
    assert "controller.reset_draft()" in text
