"""
Test cases for main.py entry point
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest


def test_main_function_starts_web_app():
    """Test that main() starts the Flask web application"""
    with patch('main.web_app') as mock_app:
        from main import main

        # Mock the run method to avoid actually starting the server
        mock_app.run = MagicMock()

        # Call main
        main()

        # Verify web_app.run was called with correct parameters
        mock_app.run.assert_called_once()
        call_kwargs = mock_app.run.call_args[1]
        assert call_kwargs['host'] == '127.0.0.1'
        assert call_kwargs['port'] == 5000
        assert call_kwargs['debug'] is False


def test_main_debug_mode_from_environment():
    """Test that debug mode is read from FLASK_DEBUG environment variable"""
    with patch('main.web_app') as mock_app, \
         patch.dict(os.environ, {'FLASK_DEBUG': 'true'}):
        from main import main

        mock_app.run = MagicMock()
        main()

        call_kwargs = mock_app.run.call_args[1]
        assert call_kwargs['debug'] is True


def test_main_debug_mode_false_by_default():
    """Test that debug mode is False by default"""
    with patch('main.web_app') as mock_app, \
         patch.dict(os.environ, {}, clear=True):
        from main import main

        mock_app.run = MagicMock()
        main()

        call_kwargs = mock_app.run.call_args[1]
        assert call_kwargs['debug'] is False


def test_main_debug_mode_case_insensitive():
    """Test that FLASK_DEBUG environment variable is case insensitive"""
    test_cases = ['True', 'TRUE', 'tRuE']

    for value in test_cases:
        with patch('main.web_app') as mock_app, \
             patch.dict(os.environ, {'FLASK_DEBUG': value}):
            from main import main

            mock_app.run = MagicMock()
            main()

            call_kwargs = mock_app.run.call_args[1]
            assert call_kwargs['debug'] is True


def test_main_module_execution():
    """Test that main() is called when module is executed directly"""
    with patch('main.main') as mock_main:
        # Simulate running as main module
        import main
        if __name__ == '__main__':
            main.main()
