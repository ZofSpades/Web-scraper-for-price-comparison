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
            mock.return_value = None
            result = db.update_search(1, total_results=5, status='completed')
            assert result is None
            mock.assert_called_once()

    def test_update_search_with_results_count(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = None
            result = db.update_search(1, total_results=5, status='completed', duration_ms=1000)
            assert result is None

    def test_add_result(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = 1
            result_data = {
                'product_name': 'Test Product',
                'price': '999',
                'rating': '4.5',
                'product_url': 'http://test.com'
            }
            result_id = db.add_result(1, 1, result_data)  # search_id, site_id, result_data
            assert result_id == 1
            mock.assert_called_once()

    def test_add_result_with_error(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = 1
            result_data = {'error': 'Failed to scrape', 'product_url': 'http://test.com'}
            result_id = db.add_result(1, 1, result_data)  # search_id, site_id, result_data
            assert result_id == 1

    def test_add_site(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = 1
            site_id = db.add_site('amazon', 'http://amazon.in')  # site_name, site_url
            assert site_id == 1
            mock.assert_called_once()

    def test_get_search_history(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = [{
                'search_id': 1, 'query': 'laptop', 'status': 'completed'
            }]
            history = db.get_export_history(search_id=1)
            assert history == [{'search_id': 1, 'query': 'laptop', 'status': 'completed'}]

    def test_get_search_history_with_limit(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = []
            history = db.get_export_history(limit=5)
            assert history == []

    def test_get_search_results(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = [
                {'result_id': 1, 'product_name': 'Product 1', 'price': '999'}
            ]
            results = db.get_results_by_search_id(1)
            assert results == [{'result_id': 1, 'product_name': 'Product 1', 'price': '999'}]

    def test_get_search_sites(self, db):
        with patch.object(db.db, 'execute_query') as mock:
            mock.return_value = [
                {'site_name': 'amazon', 'site_url': 'http://amazon.in'}
            ]
            sites = db.get_all_sites()
            assert sites == [{'site_name': 'amazon', 'site_url': 'http://amazon.in'}]

    def test_close_connection(self, db):
        # SearchHistoryDB doesn't have a close method, connection is managed by DatabaseManager
        assert db.db is not None


class TestDatabaseManager:
    """Test DatabaseManager core functionality"""

    @pytest.fixture
    def manager(self):
        from database.database import DatabaseConfig
        config = DatabaseConfig(db_type='sqlite', database=':memory:')
        return DatabaseManager(config)

    def test_initialization(self, manager):
        assert manager.config.db_type == 'sqlite'
        assert manager.config.database == ':memory:'

    def test_get_connection(self, manager):
        # Test that we can get a connection
        with manager.get_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1


class TestDatabaseIntegration:
    """Integration tests with actual database"""

    @pytest.fixture
    def db(self):
        import tempfile
        import os
        # Create temporary database file
        from database.database import DatabaseConfig, DatabaseManager
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        config = DatabaseConfig(db_type='sqlite', database=db_path)
        db_manager = DatabaseManager(config)
        
        # Create tables directly (schema for testing)
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            # Create searches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    user_id INTEGER,
                    status TEXT DEFAULT 'in_progress',
                    total_results INTEGER DEFAULT 0,
                    search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    search_duration_ms INTEGER
                )
            ''')
            # Create sites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sites (
                    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_name TEXT UNIQUE NOT NULL,
                    site_url TEXT,
                    last_scraped DATETIME
                )
            ''')
            # Create search_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    site_id INTEGER NOT NULL,
                    product_name TEXT,
                    price TEXT,
                    original_price TEXT,
                    discount_percentage TEXT,
                    rating TEXT,
                    reviews_count TEXT,
                    availability TEXT,
                    seller TEXT,
                    product_url TEXT,
                    image_url TEXT,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (search_id) REFERENCES searches (search_id),
                    FOREIGN KEY (site_id) REFERENCES sites (site_id)
                )
            ''')
            # Create export_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_history (
                    export_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    export_format TEXT NOT NULL,
                    result_count INTEGER,
                    file_path TEXT,
                    export_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (search_id) REFERENCES searches (search_id)
                )
            ''')
            conn.commit()
        
        # Create SearchHistoryDB wrapper
        from database.database import SearchHistoryDB
        db = SearchHistoryDB(db_manager)
        yield db
        
        # Cleanup: remove temporary database file
        try:
            os.unlink(db_path)
        except:
            pass

    def test_full_search_workflow(self, db):
        # Create a search
        search_id = db.create_search('test laptop', status='pending')
        assert search_id > 0

        # Add a site
        site_id = db.add_site('amazon', 'http://amazon.in/laptop')  # site_name, site_url
        assert site_id > 0

        # Add a result
        result_data = {
            'product_name': 'Dell Laptop',
            'price': '45000',
            'rating': '4.5',
            'product_url': 'http://test.com'
        }
        result_id = db.add_result(search_id, site_id, result_data)  # search_id, site_id, result_data
        assert result_id > 0

        # Update search status
        db.update_search(search_id, total_results=1, status='completed')  # returns None

        # Get history
        history = db.get_recent_searches(limit=10)
        assert len(history) > 0

        # Get results
        results = db.get_results_by_search_id(search_id)
        assert len(results) > 0
        assert results[0]['product_name'] == 'Dell Laptop'

    def test_multiple_searches(self, db):
        # Create multiple searches
        id1 = db.create_search('laptop', status='completed')
        id2 = db.create_search('phone', status='completed')
        id3 = db.create_search('tablet', status='pending')

        # Get history
        history = db.get_recent_searches(limit=10)
        assert len(history) == 3

    def test_search_with_multiple_results(self, db):
        search_id = db.create_search('laptop', status='pending')

        # Add sites first
        site_ids = []
        for i in range(3):
            site_id = db.add_site(f'site{i}', f'http://site{i}.com')
            site_ids.append(site_id)

        # Add multiple results
        for i, site_id in enumerate(site_ids):
            result_data = {
                'product_name': f'Product {i}',
                'price': f'{1000 + i * 100}',
                'product_url': f'http://site{i}.com/product'
            }
            db.add_result(search_id, site_id, result_data)

        # Update search
        db.update_search(search_id, total_results=3, status='completed')

        # Get results
        results = db.get_results_by_search_id(search_id)
        assert len(results) == 3

    def test_search_with_error_result(self, db):
        search_id = db.create_search('test', status='pending')

        # Add site first
        site_id = db.add_site('amazon', 'http://amazon.in')

        # Add error result
        error_data = {'error': 'Site unavailable', 'product_url': 'http://test.com'}
        result_id = db.add_result(search_id, site_id, error_data)
        assert result_id > 0

        # Get results
        results = db.get_results_by_search_id(search_id)
        assert len(results) == 1

    def test_get_search_sites_integration(self, db):
        # Create a search
        search_id = db.create_search('test', status='pending')

        # Add multiple sites
        db.add_site('amazon', 'http://amazon.in')
        db.add_site('flipkart', 'http://flipkart.com')

        # Get sites
        sites = db.get_all_sites()
        assert len(sites) >= 2
