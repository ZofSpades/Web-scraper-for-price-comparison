from utils.input_handler import validate_input


def test_TC_UI_01():
    res = validate_input("a")
    assert res["valid"] is False
