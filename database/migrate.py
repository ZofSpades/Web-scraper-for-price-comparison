#!/usr/bin/env python3
"""
Database migration and initialization script
Supports both SQLite and MySQL databases
"""

import argparse
import sys
import os
from .database import DatabaseConfig, DatabaseManager, SearchHistoryDB


def init_sqlite(db_path='scraper_history.db', schema_file='schema.sql'):
    """
    Initialize SQLite database
    
    Args:
        db_path: Path to SQLite database file
        schema_file: Path to schema SQL file
    """
    print(f"Initializing SQLite database: {db_path}")
    
    # Check if database exists
    db_exists = os.path.exists(db_path)
    if db_exists:
        response = input(f"Database {db_path} already exists. Recreate? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        os.remove(db_path)
    
    # Create database
    try:
        config = DatabaseConfig('sqlite', database=db_path)
        db_manager = DatabaseManager(config)
        db_manager.initialize_schema(schema_file)
        print(f"✓ Database created successfully: {db_path}")
        
        # Add some default sites
        db = SearchHistoryDB(db_manager)
        default_sites = [
            ('Amazon', 'https://www.amazon.com'),
            ('eBay', 'https://www.ebay.com'),
            ('Walmart', 'https://www.walmart.com'),
            ('BestBuy', 'https://www.bestbuy.com'),
            ('Target', 'https://www.target.com'),
        ]
        
        print("\nAdding default sites...")
        for site_name, site_url in default_sites:
            try:
                db.add_site(site_name, site_url)
                print(f"  ✓ Added {site_name}")
            except Exception as e:
                print(f"  ⨯ Error adding {site_name}: {e}")
        
        print("\n✓ Database initialization complete!")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)


def init_mysql(host='localhost', user='root', password='', 
               database='scraper_history', schema_file='schema.sql'):
    """
    Initialize MySQL database
    
    Args:
        host: MySQL host
        user: MySQL user
        password: MySQL password
        database: Database name
        schema_file: Path to schema SQL file
    """
    print(f"Initializing MySQL database: {database} on {host}")
    
    try:
        import mysql.connector
        
        # Connect without database to create it
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{database}'")
        db_exists = cursor.fetchone() is not None
        
        if db_exists:
            response = input(f"Database {database} already exists. Drop and recreate? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
            cursor.execute(f"DROP DATABASE {database}")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {database}")
        print(f"✓ Database {database} created")
        
        cursor.close()
        conn.close()
        
        # Initialize schema
        config = DatabaseConfig('mysql', host=host, user=user, 
                              password=password, database=database)
        db_manager = DatabaseManager(config)
        db_manager.initialize_schema(schema_file)
        print(f"✓ Schema initialized")
        
        # Add default sites
        db = SearchHistoryDB(db_manager)
        default_sites = [
            ('Amazon', 'https://www.amazon.com'),
            ('eBay', 'https://www.ebay.com'),
            ('Walmart', 'https://www.walmart.com'),
            ('BestBuy', 'https://www.bestbuy.com'),
            ('Target', 'https://www.target.com'),
        ]
        
        print("\nAdding default sites...")
        for site_name, site_url in default_sites:
            try:
                db.add_site(site_name, site_url)
                print(f"  ✓ Added {site_name}")
            except Exception as e:
                print(f"  ⨯ Error adding {site_name}: {e}")
        
        print("\n✓ Database initialization complete!")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)


def migrate_data(source_db, dest_db, source_type='sqlite', dest_type='mysql'):
    """
    Migrate data from one database to another
    
    Args:
        source_db: Source database configuration
        dest_db: Destination database configuration
        source_type: Source database type
        dest_type: Destination database type
    """
    print(f"Migrating data from {source_type} to {dest_type}...")
    
    try:
        # Create source connection
        if source_type == 'sqlite':
            source_config = DatabaseConfig('sqlite', database=source_db)
        else:
            source_config = DatabaseConfig('mysql', **source_db)
        
        source_manager = DatabaseManager(source_config)
        source = SearchHistoryDB(source_manager)
        
        # Create destination connection
        if dest_type == 'sqlite':
            dest_config = DatabaseConfig('sqlite', database=dest_db)
        else:
            dest_config = DatabaseConfig('mysql', **dest_db)
        
        dest_manager = DatabaseManager(dest_config)
        dest = SearchHistoryDB(dest_manager)
        
        # Migrate sites
        print("\nMigrating sites...")
        sites = source.get_all_sites()
        site_mapping = {}  # Map old site_id to new site_id
        
        for site in sites:
            new_site_id = dest.add_site(site['site_name'], site['site_url'])
            site_mapping[site['site_id']] = new_site_id
            print(f"  ✓ Migrated site: {site['site_name']}")
        
        # Migrate searches and results
        print("\nMigrating searches...")
        searches = source.get_recent_searches(limit=10000)  # Get all searches
        
        for search in searches:
            # Create search in destination
            new_search_id = dest.create_search(
                query=search['query'],
                user_id=search.get('user_id'),
                status=search['status']
            )
            
            # Update search details
            dest.update_search(
                search_id=new_search_id,
                total_results=search['total_results'],
                status=search['status'],
                duration_ms=search.get('search_duration_ms')
            )
            
            # Migrate results for this search
            results = source.get_results_by_search_id(search['search_id'])
            for result in results:
                new_site_id = site_mapping.get(result['site_id'])
                if new_site_id:
                    dest.add_result(new_search_id, new_site_id, result)
            
            print(f"  ✓ Migrated search: {search['query']} ({len(results)} results)")
        
        print(f"\n✓ Migration complete! Migrated {len(searches)} searches")
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Database migration and initialization tool for Web Scraper'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Init SQLite command
    sqlite_parser = subparsers.add_parser('init-sqlite', help='Initialize SQLite database')
    sqlite_parser.add_argument('--db', default='scraper_history.db', 
                              help='Database file path')
    sqlite_parser.add_argument('--schema', default='schema.sql',
                              help='Schema SQL file')
    
    # Init MySQL command
    mysql_parser = subparsers.add_parser('init-mysql', help='Initialize MySQL database')
    mysql_parser.add_argument('--host', default='localhost', help='MySQL host')
    mysql_parser.add_argument('--user', default='root', help='MySQL user')
    mysql_parser.add_argument('--password', default='', help='MySQL password')
    mysql_parser.add_argument('--database', default='scraper_history', 
                             help='Database name')
    mysql_parser.add_argument('--schema', default='schema.sql',
                             help='Schema SQL file')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', 
                                          help='Migrate data between databases')
    migrate_parser.add_argument('--from-type', choices=['sqlite', 'mysql'],
                               required=True, help='Source database type')
    migrate_parser.add_argument('--to-type', choices=['sqlite', 'mysql'],
                               required=True, help='Destination database type')
    migrate_parser.add_argument('--from-db', required=True,
                               help='Source database (path for SQLite, name for MySQL)')
    migrate_parser.add_argument('--to-db', required=True,
                               help='Destination database (path for SQLite, name for MySQL)')
    migrate_parser.add_argument('--from-host', default='localhost',
                               help='Source MySQL host')
    migrate_parser.add_argument('--to-host', default='localhost',
                               help='Destination MySQL host')
    migrate_parser.add_argument('--from-user', default='root',
                               help='Source MySQL user')
    migrate_parser.add_argument('--to-user', default='root',
                               help='Destination MySQL user')
    migrate_parser.add_argument('--from-password', default='',
                               help='Source MySQL password')
    migrate_parser.add_argument('--to-password', default='',
                               help='Destination MySQL password')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'init-sqlite':
        init_sqlite(args.db, args.schema)
    
    elif args.command == 'init-mysql':
        init_mysql(args.host, args.user, args.password, args.database, args.schema)
    
    elif args.command == 'migrate':
        # Prepare source and destination configs
        if args.from_type == 'sqlite':
            source = args.from_db
        else:
            source = {
                'host': args.from_host,
                'user': args.from_user,
                'password': args.from_password,
                'database': args.from_db
            }
        
        if args.to_type == 'sqlite':
            dest = args.to_db
        else:
            dest = {
                'host': args.to_host,
                'user': args.to_user,
                'password': args.to_password,
                'database': args.to_db
            }
        
        migrate_data(source, dest, args.from_type, args.to_type)


if __name__ == '__main__':
    main()
