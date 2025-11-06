"""
Database layer for Web Scraper Search History
Provides CRUD operations for searches, results, and related entities
Supports both SQLite (default) and MySQL
"""

import sqlite3
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import os
import json


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(self, db_type='sqlite', **kwargs):
        """
        Initialize database configuration
        
        Args:
            db_type (str): Database type - 'sqlite' or 'mysql'
            **kwargs: Additional database configuration parameters
                
                For SQLite:
                    database (str): Path to SQLite database file
                        Default: 'scraper_history.db'
                
                For MySQL:
                    host (str): MySQL server hostname or IP address
                        Default: 'localhost'
                    user (str): MySQL username for authentication
                        Default: 'root'
                    password (str): MySQL password for authentication
                        Default: '' (empty string)
                    database (str): MySQL database name
                        Default: 'scraper_history'
                    port (int): MySQL server port number
                        Default: 3306
        
        Raises:
            ImportError: If MySQL is selected but mysql-connector-python is not installed
            ValueError: If an unsupported database type is specified
        
        Example:
            # SQLite configuration
            config = DatabaseConfig(db_type='sqlite', database='my_data.db')
            
            # MySQL configuration
            config = DatabaseConfig(
                db_type='mysql',
                host='localhost',
                user='admin',
                password='secret',
                database='scraper_db',
                port=3306
            )
        """
        self.db_type = db_type.lower()
        
        if self.db_type == 'sqlite':
            self.database = kwargs.get('database', 'scraper_history.db')
        elif self.db_type == 'mysql':
            if not MYSQL_AVAILABLE:
                raise ImportError("mysql-connector-python is required for MySQL support. Install it with: pip install mysql-connector-python")
            self.host = kwargs.get('host', 'localhost')
            self.user = kwargs.get('user', 'root')
            self.password = kwargs.get('password', '')
            self.database = kwargs.get('database', 'scraper_history')
            self.port = kwargs.get('port', 3306)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize database manager
        
        Args:
            config: DatabaseConfig instance
        """
        self.config = config
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        
        Yields:
            Database connection object
        """
        conn = None
        try:
            if self.config.db_type == 'sqlite':
                conn = sqlite3.connect(self.config.database)
                conn.row_factory = sqlite3.Row
            elif self.config.db_type == 'mysql':
                conn = mysql.connector.connect(
                    host=self.config.host,
                    user=self.config.user,
                    password=self.config.password,
                    database=self.config.database,
                    port=self.config.port
                )
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False) -> Optional[List]:
        """
        Execute a database query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, otherwise None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                if self.config.db_type == 'sqlite':
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return results
            
            return cursor.lastrowid if cursor.lastrowid else None
    
    def initialize_schema(self, schema_file: str = 'schema.sql'):
        """
        Initialize database schema from SQL file
        
        Args:
            schema_file: Path to schema SQL file
        """
        # Try SQLite-specific schema first
        if self.config.db_type == 'sqlite':
            sqlite_schema = schema_file.replace('.sql', '_sqlite.sql')
            if os.path.exists(sqlite_schema):
                schema_file = sqlite_schema
        
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema based on database type
        if self.config.db_type == 'sqlite':
            # Use executescript for SQLite - handles multiple statements
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.executescript(schema_sql)
                except Exception as e:
                    raise Exception(f"Error initializing SQLite schema: {e}")
        
        elif self.config.db_type == 'mysql':
            # Adjust schema for MySQL
            schema_sql = schema_sql.replace('AUTOINCREMENT', 'AUTO_INCREMENT')
            schema_sql = schema_sql.replace('BOOLEAN', 'TINYINT(1)')
            
            # Split and execute statements
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            print(f"Warning executing statement: {e}")
                            # Continue with other statements


class SearchHistoryDB:
    """High-level interface for search history operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize search history database interface
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
    
    # ========== SEARCH OPERATIONS ==========
    
    def create_search(self, query: str, user_id: Optional[int] = None, 
                     status: str = 'in_progress') -> int:
        """
        Create a new search record
        
        Args:
            query: Search query string
            user_id: Optional user ID
            status: Search status (in_progress, completed, failed)
            
        Returns:
            search_id of the created search
        """
        sql = """
            INSERT INTO searches (query, user_id, status, search_timestamp)
            VALUES (?, ?, ?, ?)
        """
        params = (query, user_id, status, datetime.now())
        
        search_id = self.db.execute_query(sql, params, fetch=False)
        return search_id
    
    def update_search(self, search_id: int, total_results: int, 
                     status: str = 'completed', duration_ms: Optional[int] = None):
        """
        Update search record with results
        
        Args:
            search_id: ID of the search to update
            total_results: Number of results found
            status: Final status (completed, failed)
            duration_ms: Search duration in milliseconds
        """
        sql = """
            UPDATE searches 
            SET total_results = ?, status = ?, search_duration_ms = ?
            WHERE search_id = ?
        """
        params = (total_results, status, duration_ms, search_id)
        self.db.execute_query(sql, params)
    
    def get_search_by_id(self, search_id: int) -> Optional[Dict]:
        """
        Get search by ID
        
        Args:
            search_id: ID of the search
            
        Returns:
            Search record as dictionary or None
        """
        sql = "SELECT * FROM searches WHERE search_id = ?"
        results = self.db.execute_query(sql, (search_id,), fetch=True)
        return results[0] if results else None
    
    def get_searches_by_date(self, start_date: datetime, 
                            end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get searches within a date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range (default: now)
            
        Returns:
            List of search records
        """
        if end_date is None:
            end_date = datetime.now()
        
        sql = """
            SELECT * FROM searches 
            WHERE search_timestamp BETWEEN ? AND ?
            ORDER BY search_timestamp DESC
        """
        return self.db.execute_query(sql, (start_date, end_date), fetch=True)
    
    def search_by_query(self, query_pattern: str) -> List[Dict]:
        """
        Search for searches matching a query pattern
        
        Args:
            query_pattern: SQL LIKE pattern (use % for wildcards)
            
        Returns:
            List of matching search records
        """
        sql = """
            SELECT * FROM searches 
            WHERE query LIKE ?
            ORDER BY search_timestamp DESC
        """
        return self.db.execute_query(sql, (query_pattern,), fetch=True)
    
    def get_recent_searches(self, limit: int = 20) -> List[Dict]:
        """
        Get most recent searches
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of recent search records
        """
        sql = """
            SELECT * FROM searches 
            ORDER BY search_timestamp DESC 
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,), fetch=True)
    
    # ========== SITE OPERATIONS ==========
    
    def add_site(self, site_name: str, site_url: str) -> int:
        """
        Add a new site to the database
        
        Args:
            site_name: Name of the site
            site_url: URL of the site
            
        Returns:
            site_id of the created site
        """
        sql = """
            INSERT INTO sites (site_name, site_url)
            VALUES (?, ?)
        """
        try:
            site_id = self.db.execute_query(sql, (site_name, site_url), fetch=False)
            return site_id
        except Exception as e:
            # Site might already exist, get its ID
            existing_site = self.get_site_by_name(site_name)
            if existing_site:
                return existing_site['site_id']
            else:
                # Re-raise the original exception if site doesn't exist
                raise
    
    def get_site_by_name(self, site_name: str) -> Optional[Dict]:
        """
        Get site by name
        
        Args:
            site_name: Name of the site
            
        Returns:
            Site record or None
        """
        sql = "SELECT * FROM sites WHERE site_name = ?"
        results = self.db.execute_query(sql, (site_name,), fetch=True)
        return results[0] if results else None
    
    def update_site_last_scraped(self, site_id: int):
        """
        Update the last_scraped timestamp for a site
        
        Args:
            site_id: ID of the site
        """
        sql = "UPDATE sites SET last_scraped = ? WHERE site_id = ?"
        self.db.execute_query(sql, (datetime.now(), site_id))
    
    def get_all_sites(self) -> List[Dict]:
        """
        Get all sites
        
        Returns:
            List of all site records
        """
        sql = "SELECT * FROM sites ORDER BY site_name"
        return self.db.execute_query(sql, fetch=True)
    
    # ========== SEARCH RESULTS OPERATIONS ==========
    
    def add_result(self, search_id: int, site_id: int, result_data: Dict) -> int:
        """
        Add a search result
        
        Args:
            search_id: ID of the search
            site_id: ID of the site
            result_data: Dictionary containing result fields
            
        Returns:
            result_id of the created result
        """
        sql = """
            INSERT INTO search_results (
                search_id, site_id, product_name, price, original_price,
                discount_percentage, rating, reviews_count, availability,
                seller, product_url, image_url, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            search_id,
            site_id,
            result_data.get('product_name'),
            result_data.get('price'),
            result_data.get('original_price'),
            result_data.get('discount_percentage'),
            result_data.get('rating'),
            result_data.get('reviews_count'),
            result_data.get('availability'),
            result_data.get('seller'),
            result_data.get('url') or result_data.get('product_url'),
            result_data.get('image_url'),
            datetime.now()
        )
        
        result_id = self.db.execute_query(sql, params, fetch=False)
        return result_id
    
    def add_results_batch(self, search_id: int, results: List[Dict]):
        """
        Add multiple results for a search
        
        Args:
            search_id: ID of the search
            results: List of result dictionaries (each must have 'site' or 'site_id')
        """
        for result in results:
            # Get or create site
            site_name = result.get('site', result.get('seller', 'Unknown'))
            site_url = result.get('site_url', result.get('url', ''))
            
            if 'site_id' in result:
                site_id = result['site_id']
            else:
                site = self.get_site_by_name(site_name)
                if site:
                    site_id = site['site_id']
                else:
                    site_id = self.add_site(site_name, site_url)
            
            # Add result
            self.add_result(search_id, site_id, result)
    
    def get_results_by_search_id(self, search_id: int) -> List[Dict]:
        """
        Get all results for a search
        
        Args:
            search_id: ID of the search
            
        Returns:
            List of result records with site information
        """
        sql = """
            SELECT sr.*, s.site_name, s.site_url
            FROM search_results sr
            JOIN sites s ON sr.site_id = s.site_id
            WHERE sr.search_id = ?
            ORDER BY sr.price ASC
        """
        return self.db.execute_query(sql, (search_id,), fetch=True)
    
    def get_results_by_search_and_date(self, search_id: int, 
                                      start_date: datetime,
                                      end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get results for a search within a date range
        
        Args:
            search_id: ID of the search
            start_date: Start of date range
            end_date: End of date range (default: now)
            
        Returns:
            List of result records
        """
        if end_date is None:
            end_date = datetime.now()
        
        sql = """
            SELECT sr.*, s.site_name, s.site_url
            FROM search_results sr
            JOIN sites s ON sr.site_id = s.site_id
            WHERE sr.search_id = ? AND sr.scraped_at BETWEEN ? AND ?
            ORDER BY sr.price ASC
        """
        return self.db.execute_query(sql, (search_id, start_date, end_date), fetch=True)
    
    # ========== METADATA OPERATIONS ==========
    
    def add_metadata(self, search_id: int, key: str, value: Any):
        """
        Add metadata to a search
        
        Args:
            search_id: ID of the search
            key: Metadata key
            value: Metadata value (will be JSON encoded if not string)
        """
        if not isinstance(value, str):
            value = json.dumps(value)
        
        sql = """
            INSERT INTO search_metadata (search_id, metadata_key, metadata_value)
            VALUES (?, ?, ?)
        """
        self.db.execute_query(sql, (search_id, key, value))
    
    def get_metadata(self, search_id: int, key: Optional[str] = None) -> List[Dict]:
        """
        Get metadata for a search
        
        Args:
            search_id: ID of the search
            key: Optional specific metadata key
            
        Returns:
            List of metadata records
        """
        if key:
            sql = """
                SELECT * FROM search_metadata 
                WHERE search_id = ? AND metadata_key = ?
            """
            params = (search_id, key)
        else:
            sql = "SELECT * FROM search_metadata WHERE search_id = ?"
            params = (search_id,)
        
        return self.db.execute_query(sql, params, fetch=True)
    
    # ========== EXPORT HISTORY OPERATIONS ==========
    
    def record_export(self, search_id: int, export_format: str, 
                     result_count: int, file_path: Optional[str] = None) -> int:
        """
        Record an export operation
        
        Args:
            search_id: ID of the search
            export_format: Format (csv, pdf, json)
            result_count: Number of results exported
            file_path: Optional path to exported file
            
        Returns:
            export_id of the created record
        """
        sql = """
            INSERT INTO export_history (search_id, export_format, result_count, file_path)
            VALUES (?, ?, ?, ?)
        """
        params = (search_id, export_format, result_count, file_path)
        export_id = self.db.execute_query(sql, params, fetch=False)
        return export_id
    
    def get_export_history(self, search_id: Optional[int] = None, 
                          limit: int = 50) -> List[Dict]:
        """
        Get export history
        
        Args:
            search_id: Optional search ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of export records
        """
        if search_id:
            sql = """
                SELECT * FROM export_history 
                WHERE search_id = ?
                ORDER BY export_timestamp DESC
                LIMIT ?
            """
            params = (search_id, limit)
        else:
            sql = """
                SELECT * FROM export_history 
                ORDER BY export_timestamp DESC
                LIMIT ?
            """
            params = (limit,)
        
        return self.db.execute_query(sql, params, fetch=True)
    
    # ========== ANALYTICS OPERATIONS ==========
    
    def get_search_statistics(self, days: int = 30) -> Dict:
        """
        Get search statistics for the past N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        sql = """
            SELECT 
                COUNT(*) as total_searches,
                AVG(total_results) as avg_results_per_search,
                AVG(search_duration_ms) as avg_duration_ms,
                COUNT(DISTINCT query) as unique_queries
            FROM searches
            WHERE search_timestamp >= ?
        """
        result = self.db.execute_query(sql, (cutoff_date,), fetch=True)
        return result[0] if result else {}
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular queries
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of popular queries with counts
        """
        sql = """
            SELECT 
                query,
                COUNT(*) as search_count,
                MAX(search_timestamp) as last_searched,
                AVG(total_results) as avg_results
            FROM searches
            GROUP BY query
            ORDER BY search_count DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,), fetch=True)
    
    def get_site_performance(self) -> List[Dict]:
        """
        Get performance statistics for each site
        
        Returns:
            List of site statistics
        """
        sql = """
            SELECT 
                s.site_id,
                s.site_name,
                COUNT(DISTINCT sr.search_id) as total_searches,
                COUNT(sr.result_id) as total_results,
                AVG(sr.price) as avg_price,
                MIN(sr.price) as min_price,
                MAX(sr.price) as max_price,
                s.last_scraped
            FROM sites s
            LEFT JOIN search_results sr ON s.site_id = sr.site_id
            GROUP BY s.site_id, s.site_name, s.last_scraped
            ORDER BY total_results DESC
        """
        return self.db.execute_query(sql, fetch=True)


# Convenience functions for quick setup

def create_sqlite_db(db_path: str = 'scraper_history.db', 
                     schema_file: str = 'schema.sql') -> SearchHistoryDB:
    """
    Create and initialize SQLite database
    
    Args:
        db_path: Path to SQLite database file
        schema_file: Path to schema SQL file
        
    Returns:
        SearchHistoryDB instance
    """
    config = DatabaseConfig('sqlite', database=db_path)
    db_manager = DatabaseManager(config)
    db_manager.initialize_schema(schema_file)
    return SearchHistoryDB(db_manager)


def create_mysql_db(host: str = 'localhost', user: str = 'root', 
                   password: str = '', database: str = 'scraper_history',
                   schema_file: str = 'schema.sql') -> SearchHistoryDB:
    """
    Create and initialize MySQL database
    
    Args:
        host: MySQL host
        user: MySQL user
        password: MySQL password
        database: MySQL database name
        schema_file: Path to schema SQL file
        
    Returns:
        SearchHistoryDB instance
    """
    config = DatabaseConfig('mysql', host=host, user=user, 
                          password=password, database=database)
    db_manager = DatabaseManager(config)
    db_manager.initialize_schema(schema_file)
    return SearchHistoryDB(db_manager)
