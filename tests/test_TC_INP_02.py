from utils.input_handler import validate_input


def test_TC_INP_02():
    # Test with empty string - should be invalid
    res = validate_input("")
    assert res["valid"] is False

    # Test with single character - should be invalid (less than 2 chars)
    res = validate_input("x")
    assert res["valid"] is False

    # Test with None - should be invalid
    res = validate_input(None)
    assert res["valid"] is False
