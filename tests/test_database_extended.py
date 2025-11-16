"""Extended database tests to increase coverage"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from database.database import (
    DatabaseConfig, DatabaseManager, SearchHistoryDB
)


class TestDatabaseExtended:
    """Extended tests for database operations to increase coverage"""

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
        
        # Create tables directly
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sites (
                    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_name TEXT UNIQUE NOT NULL,
                    site_url TEXT,
                    last_scraped DATETIME
                )
            ''')
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_metadata (
                    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    metadata_key TEXT NOT NULL,
                    metadata_value TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (search_id) REFERENCES searches (search_id)
                )
            ''')
            conn.commit()
        
        from database.database import SearchHistoryDB
        db = SearchHistoryDB(db_manager)
        yield db
        
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass

    def test_get_search_by_id(self, db):
        """Test retrieving a specific search by ID"""
        search_id = db.create_search('test laptop')
        result = db.get_search_by_id(search_id)
        assert result is not None
        assert result['query'] == 'test laptop'
        assert result['search_id'] == search_id

    def test_get_search_by_id_not_found(self, db):
        """Test retrieving non-existent search returns None"""
        result = db.get_search_by_id(99999)
        assert result is None

    def test_get_searches_by_date(self, db):
        """Test retrieving searches within a date range"""
        # Create searches at different times
        search_id1 = db.create_search('laptop')
        search_id2 = db.create_search('phone')
        
        # Get searches from last hour to now
        start_date = datetime.now() - timedelta(hours=1)
        results = db.get_searches_by_date(start_date)
        
        assert len(results) >= 2
        queries = [r['query'] for r in results]
        assert 'laptop' in queries
        assert 'phone' in queries

    def test_get_searches_by_date_with_end_date(self, db):
        """Test date range search with explicit end date"""
        db.create_search('laptop')
        
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        
        results = db.get_searches_by_date(start_date, end_date)
        assert len(results) > 0

    def test_search_by_query_pattern(self, db):
        """Test searching with LIKE pattern"""
        db.create_search('laptop dell')
        db.create_search('laptop hp')
        db.create_search('phone samsung')
        
        # Search for laptop queries
        results = db.search_by_query('laptop%')
        assert len(results) == 2
        
        # Search for phone queries
        results = db.search_by_query('%phone%')
        assert len(results) == 1

    def test_get_all_sites(self, db):
        """Test retrieving all sites"""
        db.add_site('amazon', 'http://amazon.in')
        db.add_site('flipkart', 'http://flipkart.com')
        
        sites = db.get_all_sites()
        assert len(sites) == 2
        site_names = [s['site_name'] for s in sites]
        assert 'amazon' in site_names
        assert 'flipkart' in site_names

    def test_get_results_by_search_and_date(self, db):
        """Test retrieving results within date range"""
        search_id = db.create_search('laptop')
        site_id = db.add_site('amazon', 'http://amazon.in')
        
        db.add_result(search_id, site_id, {'product_name': 'Dell Laptop', 'price': '45000'})
        
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        
        results = db.get_results_by_search_and_date(search_id, start_date, end_date)
        assert len(results) == 1
        assert results[0]['product_name'] == 'Dell Laptop'
