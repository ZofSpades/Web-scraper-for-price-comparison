"""
Test cases for input_handler module
"""

import pytest

from utils.input_handler import (
    cli_input_prompt,
    get_cli_input,
    is_valid_url,
    validate_input,
)


class TestIsValidUrl:
    """Test is_valid_url function"""

    def test_valid_http_url(self):
        """Test valid HTTP URLs"""
        assert is_valid_url("http://example.com") is True
        assert is_valid_url("http://www.example.com") is True
        assert is_valid_url("http://example.com/product") is True

    def test_valid_https_url(self):
        """Test valid HTTPS URLs"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("https://www.amazon.in/product") is True
        assert is_valid_url("https://flipkart.com/item?id=123") is True

    def test_valid_url_with_port(self):
        """Test URLs with port numbers"""
        assert is_valid_url("http://localhost:5000") is True
        assert is_valid_url("https://example.com:8080/path") is True

    def test_valid_url_with_ip(self):
        """Test URLs with IP addresses"""
        assert is_valid_url("http://127.0.0.1") is True
        assert is_valid_url("http://192.168.1.1:8080") is True

    def test_valid_url_localhost(self):
        """Test localhost URLs"""
        assert is_valid_url("http://localhost") is True
        assert is_valid_url("http://localhost/path") is True

    def test_invalid_url_no_protocol(self):
        """Test invalid URLs without protocol"""
        assert is_valid_url("example.com") is False
        assert is_valid_url("www.example.com") is False

    def test_invalid_url_malformed(self):
        """Test malformed URLs"""
        assert is_valid_url("http://") is False
        assert is_valid_url("https://") is False
        assert is_valid_url("not a url") is False

    def test_invalid_url_empty_string(self):
        """Test empty string input"""
        assert is_valid_url("") is False
        assert is_valid_url("   ") is False

    def test_invalid_url_none(self):
        """Test None input"""
        assert is_valid_url(None) is False

    def test_invalid_url_wrong_type(self):
        """Test wrong input type"""
        assert is_valid_url(123) is False
        assert is_valid_url([]) is False
        assert is_valid_url({}) is False

    def test_url_with_whitespace(self):
        """Test URLs with leading/trailing whitespace"""
        assert is_valid_url("  http://example.com  ") is True
        assert is_valid_url("\thttps://example.com\n") is True


class TestValidateInput:
    """Test validate_input function"""

    def test_validate_url_input(self):
        """Test validation of URL input"""
        result = validate_input("https://example.com/product")
        assert result['type'] == 'url'
        assert result['value'] == "https://example.com/product"
        assert result['valid'] is True

    def test_validate_product_name(self):
        """Test validation of product name"""
        result = validate_input("iPhone 15 Pro")
        assert result['type'] == 'product_name'
        assert result['value'] == "iPhone 15 Pro"
        assert result['valid'] is True

    def test_validate_short_product_name(self):
        """Test validation of product names with minimum length"""
        result = validate_input("TV")
        assert result['type'] == 'product_name'
        assert result['valid'] is True

    def test_validate_too_short_product_name(self):
        """Test validation fails for single character"""
        result = validate_input("A")
        assert result['type'] == 'product_name'
        assert result['valid'] is False

    def test_validate_empty_string(self):
        """Test validation of empty string"""
        result = validate_input("")
        assert result['type'] is None
        assert result['value'] is None
        assert result['valid'] is False

    def test_validate_whitespace_only(self):
        """Test validation of whitespace-only string"""
        result = validate_input("   ")
        assert result['type'] is None
        assert result['value'] is None
        assert result['valid'] is False

    def test_validate_none_input(self):
        """Test validation of None input"""
        result = validate_input(None)
        assert result['type'] is None
        assert result['value'] is None
        assert result['valid'] is False

    def test_validate_wrong_type_input(self):
        """Test validation of wrong type input"""
        result = validate_input(123)
        assert result['valid'] is False

        result = validate_input([])
        assert result['valid'] is False

    def test_validate_input_strips_whitespace(self):
        """Test that validation strips whitespace"""
        result = validate_input("  laptop  ")
        assert result['value'] == "laptop"
        assert result['valid'] is True

    def test_validate_long_product_name(self):
        """Test validation of long product names"""
        long_name = "Apple MacBook Pro 16 inch M3 Max Chip with 16-Core CPU"
        result = validate_input(long_name)
        assert result['type'] == 'product_name'
        assert result['valid'] is True

    def test_validate_product_name_with_special_chars(self):
        """Test product names with special characters"""
        result = validate_input("Product @ $99.99!")
        assert result['type'] == 'product_name'
        assert result['valid'] is True


class TestCliInputPrompt:
    """Test cli_input_prompt function"""

    def test_cli_prompt_valid_product_name(self, monkeypatch):
        """Test CLI prompt with valid product name"""
        monkeypatch.setattr('builtins.input', lambda _: "laptop")
        result = cli_input_prompt()
        assert result['type'] == 'product_name'
        assert result['value'] == "laptop"
        assert result['valid'] is True

    def test_cli_prompt_valid_url(self, monkeypatch):
        """Test CLI prompt with valid URL"""
        monkeypatch.setattr('builtins.input', lambda _: "https://example.com/product")
        result = cli_input_prompt()
        assert result['type'] == 'url'
        assert result['valid'] is True

    def test_cli_prompt_exit_command_quit(self, monkeypatch):
        """Test CLI prompt with 'quit' command"""
        monkeypatch.setattr('builtins.input', lambda _: "quit")
        result = cli_input_prompt()
        assert result['type'] == 'exit'
        assert result['valid'] is True
        assert result['value'] is None

    def test_cli_prompt_exit_command_exit(self, monkeypatch):
        """Test CLI prompt with 'exit' command"""
        monkeypatch.setattr('builtins.input', lambda _: "exit")
        result = cli_input_prompt()
        assert result['type'] == 'exit'
        assert result['valid'] is True

    def test_cli_prompt_exit_case_insensitive(self, monkeypatch):
        """Test CLI prompt with case-insensitive exit commands"""
        for cmd in ['QUIT', 'EXIT', 'QuIt', 'ExIt']:
            monkeypatch.setattr('builtins.input', lambda _: cmd)
            result = cli_input_prompt()
            assert result['type'] == 'exit'

    def test_cli_prompt_invalid_then_valid(self, monkeypatch):
        """Test CLI prompt with invalid input followed by valid input"""
        inputs = iter(["x", "laptop"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        result = cli_input_prompt()
        assert result['type'] == 'product_name'
        assert result['value'] == "laptop"
        assert result['valid'] is True

    def test_cli_prompt_empty_then_valid(self, monkeypatch):
        """Test CLI prompt with empty input followed by valid input"""
        inputs = iter(["", "phone"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        result = cli_input_prompt()
        assert result['valid'] is True


class TestGetCliInput:
    """Test get_cli_input function"""

    def test_get_cli_input_returns_value(self, monkeypatch):
        """Test that get_cli_input returns the input value"""
        monkeypatch.setattr('builtins.input', lambda _: "laptop")
        result = get_cli_input()
        assert result == "laptop"

    def test_get_cli_input_returns_url(self, monkeypatch):
        """Test that get_cli_input returns URL value"""
        url = "https://example.com/product"
        monkeypatch.setattr('builtins.input', lambda _: url)
        result = get_cli_input()
        assert result == url

    def test_get_cli_input_exit_returns_none(self, monkeypatch):
        """Test that get_cli_input returns None on exit"""
        monkeypatch.setattr('builtins.input', lambda _: "quit")
        result = get_cli_input()
        assert result is None

    def test_get_cli_input_strips_whitespace(self, monkeypatch):
        """Test that get_cli_input strips whitespace"""
        monkeypatch.setattr('builtins.input', lambda _: "  laptop  ")
        result = get_cli_input()
        assert result == "laptop"
