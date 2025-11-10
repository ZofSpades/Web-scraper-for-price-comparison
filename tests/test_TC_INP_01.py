from utils.input_handler import validate_input


def test_TC_INP_01():
    res = validate_input("iPhone 15 Pro")
    assert res["valid"] is True and res["type"] == "product_name"
