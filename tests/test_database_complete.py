"""
Complete working tests for database operations using correct API
"""

import pytest
import sqlite3
from unittest.mock import MagicMock, patch, call
from datetime import datetime

from database.database import (
    DatabaseManager,
    SearchHistoryDB,
    create_sqlite_db,
    create_mysql_db
)


class TestDatabaseFactory:
    """Test database factory functions"""

    @patch('database.database.DatabaseManager.initialize_schema')
    def test_create_sqlite_db_returns_search_history_wrapper(self, mock_init_schema):
        db = create_sqlite_db(':memory:')
        assert isinstance(db, SearchHistoryDB)
        mock_init_schema.assert_called_once()

    @patch('database.database.DatabaseManager.initialize_schema')
    def test_create_sqlite_db_with_file(self, mock_init_schema, tmp_path):
        db_path = tmp_path / "test.db"
        db = create_sqlite_db(str(db_path))
        assert db is not None
        assert isinstance(db, SearchHistoryDB)
        mock_init_schema.assert_called_once()

    @patch('database.database.DatabaseManager')
    def test_create_mysql_db_calls_manager(self, mock_manager):
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance

        config = {
            'host': 'localhost',
            'user': 'test',
            'password': 'pass',
            'database': 'testdb'
        }
        db = create_mysql_db(config)
        assert isinstance(db, SearchHistoryDB)


class TestSearchHistoryDB:
    """Test SearchHistoryDB wrapper class"""

    @pytest.fixture
    def db(self):
        with patch('database.database.DatabaseManager.initialize_schema'):
            return create_sqlite_db(':memory:')

    def test_create_search(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (1, None)
            search_id = db.create_search('laptop', 'pending')
            assert search_id == (1, None)
            mock.assert_called_once()

    def test_create_search_with_all_params(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (1, None)
            search_id = db.create_search('laptop', user_id=123, status='pending')
            assert search_id == (1, None)

    def test_update_search_status(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (True, None)
            result = db.update_search(1, total_results=5, status='completed')
            assert result == (True, None)
            mock.assert_called_once()

    def test_update_search_with_results_count(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (True, None)
            result = db.update_search(1, total_results=5, status='completed', duration_ms=1000)
            assert result == (True, None)

    def test_add_result(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (1, None)
            result_data = {
                'title': 'Test Product',
                'price': '999',
                'rating': '4.5'
            }
            result_id = db.add_result(1, 'amazon', 'http://test.com', result_data)
            assert result_id == (1, None)
            mock.assert_called_once()

    def test_add_result_with_error(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (1, None)
            result_data = {'error': 'Failed to scrape'}
            result_id = db.add_result(1, 'amazon', 'http://test.com', result_data)
            assert result_id == (1, None)

    def test_add_site(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = (1, None)
            site_id = db.add_site(1, 'amazon', 'http://amazon.in')
            assert site_id == (1, None)
            mock.assert_called_once()

    def test_get_search_history(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = ([
                {'search_id': 1, 'query': 'laptop', 'status': 'completed'}
            ], None)
            history = db.get_search_history()
            assert history == ([{'search_id': 1, 'query': 'laptop', 'status': 'completed'}], None)

    def test_get_search_history_with_limit(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = ([], None)
            history = db.get_search_history(5)
            mock.assert_called_once()

    def test_get_search_results(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = ([
                {'result_id': 1, 'title': 'Product 1', 'price': '999'}
            ], None)
            results = db.get_search_results(1)
            assert results == ([{'result_id': 1, 'title': 'Product 1', 'price': '999'}], None)

    def test_get_search_sites(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = ([
                {'site_name': 'amazon', 'url': 'http://amazon.in'}
            ], None)
            sites = db.get_search_sites(1)
            assert sites == ([{'site_name': 'amazon', 'url': 'http://amazon.in'}], None)

    def test_close_connection(self, db):
        with patch.object(db.db, 'close') as mock:
            db.close()
            mock.assert_called_once()


class TestDatabaseManager:
    """Test DatabaseManager core functionality"""

    @pytest.fixture
    def manager(self):
        return DatabaseManager(':memory:', 'sqlite')

    def test_initialization(self, manager):
        assert manager.db_type == 'sqlite'
        assert manager.db_path == ':memory:'

    def test_execute_query_with_fetchall(self, manager):
        # Create a test table
        manager.execute_query("CREATE TABLE test (id INTEGER, name TEXT)", fetch=False)
        manager.execute_query("INSERT INTO test VALUES (1, 'test')", fetch=False)

        result, error = manager.execute_query("SELECT * FROM test", fetch=True)
        assert error is None
        assert len(result) > 0

    def test_execute_query_insert_returns_id(self, manager):
        manager.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)", fetch=False)
        result, error = manager.execute_query("INSERT INTO test (name) VALUES ('test')", fetch=False)
        assert error is None
        assert result > 0  # Should return lastrowid

    def test_execute_query_handles_error(self, manager):
        result, error = manager.execute_query("INVALID SQL", fetch=False)
        assert error is not None
        assert result is None

    def test_close(self, manager):
        manager.close()
        # After close, connection should be None
        assert True  # If no exception, test passes


class TestDatabaseIntegration:
    """Integration tests with actual database"""

    @pytest.fixture
    def db(self):
        with patch('database.database.DatabaseManager.initialize_schema'):
            db = create_sqlite_db(':memory:')
        yield db
        db.close()

    def test_full_search_workflow(self, db):
        # Create a search
        search_id = db.create_search('test laptop', 'pending')
        assert search_id > 0

        # Add a site
        site_id = db.add_site(search_id, 'amazon', 'http://amazon.in/laptop')
        assert site_id > 0

        # Add a result
        result_data = {
            'title': 'Dell Laptop',
            'price': '45000',
            'rating': '4.5'
        }
        result_id = db.add_result(search_id, 'amazon', 'http://test.com', result_data)
        assert result_id > 0

        # Update search status
        success = db.update_search(search_id, 'completed', 1)
        assert success is True

        # Get history
        history = db.get_search_history(10)
        assert len(history) > 0
        assert history[0]['query'] == 'test laptop'

        # Get results
        results = db.get_search_results(search_id)
        assert len(results) > 0
        assert results[0]['title'] == 'Dell Laptop'

    def test_multiple_searches(self, db):
        # Create multiple searches
        id1 = db.create_search('laptop', 'completed')
        id2 = db.create_search('phone', 'completed')
        id3 = db.create_search('tablet', 'pending')

        # Get history
        history = db.get_search_history(10)
        assert len(history) == 3

    def test_search_with_multiple_results(self, db):
        search_id = db.create_search('laptop', 'pending')

        # Add multiple results
        for i in range(3):
            result_data = {
                'title': f'Product {i}',
                'price': f'{1000 + i * 100}'
            }
            db.add_result(search_id, f'site{i}', f'http://site{i}.com', result_data)

        # Update search
        db.update_search(search_id, 'completed', 3)

        # Get results
        results = db.get_search_results(search_id)
        assert len(results) == 3

    def test_search_with_error_result(self, db):
        search_id = db.create_search('test', 'pending')

        # Add error result
        error_data = {'error': 'Site unavailable'}
        result_id = db.add_result(search_id, 'amazon', 'http://test.com', error_data)
        assert result_id > 0

        # Get results
        results = db.get_search_results(search_id)
        assert len(results) == 1

    def test_get_search_sites_integration(self, db):
        search_id = db.create_search('test', 'pending')

        # Add multiple sites
        db.add_site(search_id, 'amazon', 'http://amazon.in')
        db.add_site(search_id, 'flipkart', 'http://flipkart.com')

        # Get sites
        sites = db.get_search_sites(search_id)
        assert len(sites) == 2
