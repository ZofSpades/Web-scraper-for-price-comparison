from utils.input_handler import validate_input


def test_TC_INP_02():
    res = validate_input("htt://bad-url")
    assert res["valid"] is False
