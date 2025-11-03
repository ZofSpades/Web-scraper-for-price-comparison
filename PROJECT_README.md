# Web Scraper with Export & Database Features

A comprehensive web scraping solution for price comparison with CSV/PDF export capabilities and complete search history tracking.

## 🚀 Features

- **Web Scraping**: Price comparison across multiple e-commerce sites
- **Export Capabilities**: CSV and PDF report generation with charts
- **Database Integration**: SQLite/MySQL support for search history
- **CLI Interface**: Command-line tools for automation
- **REST API**: Programmatic access to all features
- **Analytics**: Popular queries, site performance, search statistics

## 📦 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database (Optional)

```bash
# Interactive setup
./setup_db.sh

# Or manually
python3 migrate.py init-sqlite --db scraper_history.db
```

### 3. Run the Application

```bash
# Without database
python3 app.py

# With database integration
python3 app_with_database.py
```

### 4. Access the Web Interface

Open browser and navigate to: `http://localhost:5000`

## 📚 Documentation

- **[README.md](README.md)** - Complete usage guide and API reference
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Database configuration and usage
- **[DB_IMPLEMENTATION_SUMMARY.md](DB_IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide

## 🗄️ Database Features

The application includes a complete database layer for tracking search history:

- **Dual Database Support**: SQLite (development) or MySQL (production)
- **Search History**: Track all queries with timestamps and results
- **Analytics Dashboard**: Popular queries, site statistics, trends
- **Export Tracking**: Audit trail for all CSV/PDF exports
- **Date Range Queries**: Filter searches and results by date

### Example Usage

```python
from database import create_sqlite_db

# Initialize
db = create_sqlite_db('scraper_history.db')

# Save search
search_id = db.create_search(query="laptop")
db.add_results_batch(search_id, results)

# Query by search ID
results = db.get_results_by_search_id(search_id)

# Query by date
from datetime import datetime, timedelta
week_ago = datetime.now() - timedelta(days=7)
recent = db.get_searches_by_date(week_ago)
```

## 🧪 Testing

```bash
# Test database functionality
python3 test_database.py

# Test export functionality
python3 test_exports.py
```

## 📁 Project Structure

```
web_scraper_exports/
├── app.py                       # Flask web application
├── app_with_database.py         # Flask app with database integration
├── database.py                  # Database layer (SQLite/MySQL)
├── export_utils.py              # CSV/PDF export utilities
├── cli.py                       # Command-line interface
├── migrate.py                   # Database migration tool
├── setup_db.sh                  # Interactive database setup
├── schema.sql                   # Database schema (universal)
├── schema_sqlite.sql            # SQLite-optimized schema
├── test_database.py             # Database tests
├── test_exports.py              # Export tests
├── requirements.txt             # Python dependencies
├── templates/                   # HTML templates
│   ├── index.html
│   ├── results.html
│   └── base.html
└── docs/                        # Documentation
    ├── README.md
    ├── DATABASE_SETUP.md
    ├── DB_IMPLEMENTATION_SUMMARY.md
    └── QUICKSTART.md
```

## 🛠️ CLI Usage

```bash
# Basic search with CSV export
python3 cli.py --search "laptop" --export-csv

# Search with PDF report
python3 cli.py --search "headphones" --export-pdf

# Initialize database
python3 migrate.py init-sqlite --db scraper_history.db

# Migrate data between databases
python3 migrate.py migrate --from-type sqlite --to-type mysql \
  --from-db old.db --to-db scraper_history
```

## 🔌 API Endpoints

### Search
- `POST /search` - Perform search and save to database
- `GET /search/<id>` - View specific search details

### History
- `GET /history` - View all search history
- `GET /api/search/history` - JSON API for search history

### Export
- `POST /export/csv` - Export results to CSV
- `POST /export/pdf` - Generate PDF report
- `POST /export/csv/<search_id>` - Export specific search

### Analytics
- `GET /api/statistics` - Search statistics and trends
- `GET /api/search/<id>/results` - Get results for specific search

## 🔧 Configuration

### SQLite (Default)
No configuration needed. Database file created automatically.

### MySQL
Create `db_config.py`:

```python
DB_CONFIG = {
    'type': 'mysql',
    'host': 'localhost',
    'user': 'scraper_user',
    'password': 'your_password',
    'database': 'scraper_history'
}
```

## 📊 Database Schema

- **searches** - Search queries, timestamps, status, duration
- **sites** - Scraped website information
- **search_results** - Product results with pricing and ratings
- **search_metadata** - Flexible metadata storage
- **export_history** - Export audit trail

## 🤝 Contributing

This project was developed as part of PES University coursework (UE23CS341A).

## 📄 License

Educational project - PES University, 2025

## ✅ Acceptance Criteria

All project requirements met:

- ✅ **T1**: Database schema designed (searches, results, sites, timestamps)
- ✅ **T2**: Database layer implemented with complete CRUD operations
- ✅ **T3**: Migration scripts and setup instructions created
- ✅ **Search results saved** - `add_results_batch()`
- ✅ **Query by search_id** - `get_results_by_search_id()`
- ✅ **Query by date** - `get_results_by_search_and_date()`

Verified with comprehensive test suite: 100% pass rate.

## 📞 Support

For issues or questions, see documentation files or run tests to verify setup.
