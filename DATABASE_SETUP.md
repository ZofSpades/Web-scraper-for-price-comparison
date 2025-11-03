# Database Setup Guide

## Overview

This guide covers setting up the search history database for the Web Scraper Price Comparison application. The database stores search queries, results, and provides historical tracking capabilities.

## Supported Databases

- **SQLite** (recommended for local development)
- **MySQL** (recommended for production)

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
./setup_db.sh
```

Follow the prompts to choose your database type and configure settings.

### Option 2: Manual Setup

#### SQLite Setup

1. **Install dependencies:**
   ```bash
   pip install mysql-connector-python
   ```

2. **Initialize database:**
   ```bash
   python3 migrate.py init-sqlite --db scraper_history.db
   ```

3. **Verify setup:**
   ```bash
   ls -lh scraper_history.db
   ```

#### MySQL Setup

1. **Install dependencies:**
   ```bash
   pip install mysql-connector-python
   ```

2. **Create MySQL database (if not exists):**
   ```sql
   CREATE DATABASE scraper_history CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Initialize schema:**
   ```bash
   python3 migrate.py init-mysql \
       --host localhost \
       --user root \
       --password YOUR_PASSWORD \
       --database scraper_history
   ```

## Database Schema

The database includes the following tables:

### Core Tables

#### `searches`
Stores search query metadata
- `search_id` - Unique identifier
- `query` - Search query string
- `search_timestamp` - When the search was performed
- `total_results` - Number of results found
- `status` - Search status (completed, failed, in_progress)
- `search_duration_ms` - Execution time in milliseconds
- `user_id` - Optional user identifier

#### `sites`
Information about scraped websites
- `site_id` - Unique identifier
- `site_name` - Name of the site (e.g., "Amazon")
- `site_url` - Base URL of the site
- `is_active` - Whether the site is currently being scraped
- `last_scraped` - Last scraping timestamp

#### `search_results`
Individual product results for each search
- `result_id` - Unique identifier
- `search_id` - Foreign key to searches
- `site_id` - Foreign key to sites
- `product_name` - Product name/title
- `price` - Current price
- `original_price` - Original/list price
- `discount_percentage` - Discount percentage
- `rating` - Product rating
- `reviews_count` - Number of reviews
- `availability` - Stock status
- `seller` - Seller/vendor name
- `product_url` - Link to product
- `image_url` - Product image URL
- `scraped_at` - When this result was scraped

#### `search_metadata`
Additional metadata for searches
- `metadata_id` - Unique identifier
- `search_id` - Foreign key to searches
- `metadata_key` - Metadata key name
- `metadata_value` - Metadata value (JSON encoded)

#### `export_history`
Tracks export operations
- `export_id` - Unique identifier
- `search_id` - Foreign key to searches
- `export_format` - Format (csv, pdf, json)
- `export_timestamp` - When export was performed
- `result_count` - Number of results exported
- `file_path` - Path to exported file

### Views

#### `recent_searches`
Shows recent searches with result counts

#### `popular_queries`
Most frequently searched queries

#### `site_statistics`
Performance statistics for each site

## Using the Database in Your Application

### Basic Usage

```python
from database import create_sqlite_db

# Create database connection
db = create_sqlite_db('scraper_history.db')

# Create a new search
search_id = db.create_search(query="laptop", user_id=1)

# Add results
results = [
    {
        'product_name': 'Dell Laptop',
        'price': 799.99,
        'rating': 4.5,
        'site': 'Amazon',
        'url': 'https://amazon.com/...'
    },
    # ... more results
]
db.add_results_batch(search_id, results)

# Update search with final count
db.update_search(search_id, total_results=len(results), 
                status='completed', duration_ms=1500)

# Query results by search ID
search_results = db.get_results_by_search_id(search_id)

# Query results by date range
from datetime import datetime, timedelta
start_date = datetime.now() - timedelta(days=7)
recent_searches = db.get_searches_by_date(start_date)
```

### MySQL Usage

```python
from database import create_mysql_db

# Create MySQL database connection
db = create_mysql_db(
    host='localhost',
    user='root',
    password='your_password',
    database='scraper_history'
)

# Use the same API as SQLite
search_id = db.create_search(query="laptop")
# ... rest is identical
```

### Advanced Queries

```python
# Search by query pattern
laptop_searches = db.search_by_query('%laptop%')

# Get results within date range
from datetime import datetime, timedelta

search_id = 123
start_date = datetime(2025, 11, 1)
end_date = datetime(2025, 11, 3)
results = db.get_results_by_search_and_date(search_id, start_date, end_date)

# Add metadata to a search
db.add_metadata(search_id, 'filters', {'price_min': 500, 'price_max': 1000})
db.add_metadata(search_id, 'source', 'web_ui')

# Get metadata
metadata = db.get_metadata(search_id)

# Record export
export_id = db.record_export(
    search_id=search_id,
    export_format='csv',
    result_count=50,
    file_path='/exports/search_123.csv'
)

# Get statistics
stats = db.get_search_statistics(days=30)
print(f"Total searches: {stats['total_searches']}")
print(f"Average results: {stats['avg_results_per_search']}")

# Get popular queries
popular = db.get_popular_queries(limit=10)
for query in popular:
    print(f"{query['query']}: {query['search_count']} searches")

# Get site performance
site_stats = db.get_site_performance()
for site in site_stats:
    print(f"{site['site_name']}: {site['total_results']} products")
```

## Integrating with Flask App

Update your `app.py` to use the database:

```python
from flask import Flask, render_template, request, jsonify
from database import create_sqlite_db
from datetime import datetime
import time

app = Flask(__name__)

# Initialize database
db = create_sqlite_db('scraper_history.db')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '')
    
    # Create search record
    search_id = db.create_search(query=query, status='in_progress')
    start_time = time.time()
    
    try:
        # Perform actual scraping
        results = perform_scraping(query)  # Your scraping function
        
        # Save results to database
        db.add_results_batch(search_id, results)
        
        # Update search with completion
        duration_ms = int((time.time() - start_time) * 1000)
        db.update_search(
            search_id=search_id,
            total_results=len(results),
            status='completed',
            duration_ms=duration_ms
        )
        
        return render_template('results.html', 
                             results=results, 
                             search_id=search_id)
    
    except Exception as e:
        # Update search with error status
        db.update_search(search_id, total_results=0, status='failed')
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    """View search history"""
    recent = db.get_recent_searches(limit=50)
    return render_template('history.html', searches=recent)

@app.route('/search/<int:search_id>')
def view_search(search_id):
    """View a specific search and its results"""
    search = db.get_search_by_id(search_id)
    results = db.get_results_by_search_id(search_id)
    return render_template('search_detail.html', 
                         search=search, 
                         results=results)

@app.route('/export/csv/<int:search_id>', methods=['POST'])
def export_search_csv(search_id):
    """Export search results to CSV"""
    results = db.get_results_by_search_id(search_id)
    
    # Generate CSV (using your existing export_utils)
    csv_string = csv_exporter.export_to_csv_string(results)
    
    # Record export
    db.record_export(
        search_id=search_id,
        export_format='csv',
        result_count=len(results)
    )
    
    # Return CSV file
    # ... your existing export code
```

## Data Migration

### SQLite to MySQL

```bash
python3 migrate.py migrate \
    --from-type sqlite \
    --to-type mysql \
    --from-db scraper_history.db \
    --to-db scraper_history \
    --to-host localhost \
    --to-user root \
    --to-password YOUR_PASSWORD
```

### MySQL to SQLite

```bash
python3 migrate.py migrate \
    --from-type mysql \
    --to-type sqlite \
    --from-db scraper_history \
    --to-db scraper_history_backup.db \
    --from-host localhost \
    --from-user root \
    --from-password YOUR_PASSWORD
```

## Configuration

### SQLite Configuration

SQLite requires no additional configuration. The database file is created automatically.

**Pros:**
- Zero configuration
- No separate server required
- Perfect for development and testing
- Easy to backup (just copy the .db file)

**Cons:**
- Not suitable for high concurrency
- Limited to single server

### MySQL Configuration

Create a configuration file `db_config.py`:

```python
# db_config.py
DB_CONFIG = {
    'type': 'mysql',
    'host': 'localhost',
    'user': 'scraper_user',
    'password': 'secure_password',
    'database': 'scraper_history'
}
```

Then use it in your app:

```python
from database import DatabaseConfig, DatabaseManager, SearchHistoryDB
from db_config import DB_CONFIG

config = DatabaseConfig(**DB_CONFIG)
db_manager = DatabaseManager(config)
db = SearchHistoryDB(db_manager)
```

**Pros:**
- Better performance for concurrent access
- Scalable for production
- Better transaction support
- Advanced query optimization

**Cons:**
- Requires MySQL server setup
- More configuration needed
- Additional resource requirements

## Maintenance

### Backup SQLite Database

```bash
# Simple file copy
cp scraper_history.db scraper_history_backup_$(date +%Y%m%d).db

# Or use SQLite's backup command
sqlite3 scraper_history.db ".backup scraper_history_backup.db"
```

### Backup MySQL Database

```bash
mysqldump -u root -p scraper_history > scraper_history_backup_$(date +%Y%m%d).sql
```

### Clean Old Data

```python
from database import create_sqlite_db
from datetime import datetime, timedelta

db = create_sqlite_db('scraper_history.db')

# Delete searches older than 90 days
cutoff_date = datetime.now() - timedelta(days=90)

# Get old search IDs
old_searches = db.get_searches_by_date(
    start_date=datetime(2000, 1, 1),
    end_date=cutoff_date
)

# Delete them (CASCADE will delete related results)
with db.db.get_connection() as conn:
    cursor = conn.cursor()
    for search in old_searches:
        cursor.execute("DELETE FROM searches WHERE search_id = ?", 
                      (search['search_id'],))
```

## Troubleshooting

### SQLite: "Database is locked" Error

This occurs with high concurrent access. Solutions:
1. Use connection pooling
2. Enable WAL mode: `PRAGMA journal_mode=WAL;`
3. Switch to MySQL for production

### MySQL: Connection Refused

Check that MySQL server is running:
```bash
sudo systemctl status mysql
sudo systemctl start mysql
```

### Schema Already Exists

If re-initializing, drop existing tables first or use the migration script's prompts.

## Testing the Database

Create a test script:

```python
# test_db.py
from database import create_sqlite_db
from datetime import datetime

# Initialize database
db = create_sqlite_db('test_scraper.db')

# Test 1: Create search
print("Test 1: Creating search...")
search_id = db.create_search(query="test laptop", user_id=1)
print(f"✓ Created search with ID: {search_id}")

# Test 2: Add results
print("\nTest 2: Adding results...")
test_results = [
    {
        'product_name': 'Test Laptop 1',
        'price': 999.99,
        'rating': 4.5,
        'site': 'Amazon',
        'url': 'https://example.com/1'
    },
    {
        'product_name': 'Test Laptop 2',
        'price': 1299.99,
        'rating': 4.8,
        'site': 'BestBuy',
        'url': 'https://example.com/2'
    }
]
db.add_results_batch(search_id, test_results)
db.update_search(search_id, total_results=len(test_results), status='completed')
print(f"✓ Added {len(test_results)} results")

# Test 3: Query by search ID
print("\nTest 3: Querying results by search ID...")
results = db.get_results_by_search_id(search_id)
print(f"✓ Retrieved {len(results)} results")
for r in results:
    print(f"  - {r['product_name']}: ${r['price']}")

# Test 4: Query by date
print("\nTest 4: Querying searches by date...")
from datetime import timedelta
start_date = datetime.now() - timedelta(days=1)
recent = db.get_searches_by_date(start_date)
print(f"✓ Found {len(recent)} recent searches")
for s in recent:
    print(f"  - {s['query']} ({s['total_results']} results)")

# Test 5: Record export
print("\nTest 5: Recording export...")
export_id = db.record_export(search_id, 'csv', len(results), '/tmp/test.csv')
print(f"✓ Recorded export with ID: {export_id}")

# Test 6: Get statistics
print("\nTest 6: Getting statistics...")
stats = db.get_search_statistics(days=30)
print(f"✓ Statistics:")
print(f"  - Total searches: {stats['total_searches']}")
print(f"  - Avg results: {stats['avg_results_per_search']}")
print(f"  - Unique queries: {stats['unique_queries']}")

print("\n✓ All tests passed!")
```

Run the test:
```bash
python3 test_db.py
```

## Performance Tips

1. **Index Usage**: The schema includes indexes on frequently queried columns
2. **Batch Operations**: Use `add_results_batch()` instead of individual `add_result()` calls
3. **Connection Pooling**: For production, implement connection pooling
4. **Regular Cleanup**: Archive or delete old data periodically
5. **Query Optimization**: Use views for complex queries

## Security Considerations

1. **Credentials**: Never commit database credentials to version control
2. **SQL Injection**: The provided code uses parameterized queries to prevent SQL injection
3. **Access Control**: Implement user authentication and authorization
4. **Encryption**: Consider encrypting sensitive data in the database
5. **Backups**: Regular automated backups are essential

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the schema.sql file for table structure
3. Examine the database.py file for available methods
4. Run test_db.py to verify setup

## Acceptance Criteria Verification

✅ **Search results are saved**: Use `add_results_batch()` to save all search results
✅ **Query by search_id**: Use `get_results_by_search_id(search_id)`
✅ **Query by date**: Use `get_results_by_search_and_date(search_id, start_date, end_date)`

Example verification:
```python
# Save results
search_id = db.create_search(query="laptop")
db.add_results_batch(search_id, results)

# Query by search_id
results = db.get_results_by_search_id(search_id)
assert len(results) > 0

# Query by date
from datetime import datetime, timedelta
start_date = datetime.now() - timedelta(days=1)
recent_results = db.get_results_by_search_and_date(search_id, start_date)
assert len(recent_results) > 0
```
