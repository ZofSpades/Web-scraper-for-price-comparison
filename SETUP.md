# Web Scraper for Price Comparison - Setup Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Features](#features)
- [Supported E-commerce Sites](#supported-e-commerce-sites)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This is a real-time web scraping application that compares product prices across multiple Indian e-commerce websites. The application uses Flask for the web interface, Selenium for dynamic scraping, and SQLite for search history tracking.

**Key Features:**
- Real-time price comparison across 5 major e-commerce sites
- Search history with analytics dashboard
- CSV/PDF export functionality
- Advanced pricing utilities with multi-currency support
- Responsive modern UI design
- **Async scraping** for improved performance (~15s for 5 sites)
- **Selenium integration** with anti-detection for dynamic content
- **Proxy & User-Agent rotation** to prevent IP bans

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software
1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **Google Chrome Browser**
   - Required for Selenium web scraping
   - Download from: https://www.google.com/chrome/

3. **Git** (for cloning the repository)
   - Download from: https://git-scm.com/downloads/

### System Requirements
- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** At least 500MB free space
- **Internet Connection:** Required for scraping

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/pestechnology/PESU_EC_CSE_K_P60_Web_Scraper_for_Price_Comparison_Team-5.git
cd PESU_EC_CSE_K_P60_Web_Scraper_for_Price_Comparison_Team-5
```

### Step 2: Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages include:**
- Flask (web framework)
- BeautifulSoup4 (HTML parsing)
- Selenium (dynamic scraping)
- webdriver-manager (automatic ChromeDriver management)
- requests (HTTP requests)
- pandas (data processing)
- reportlab (PDF generation)

---

## ⚙️ Configuration

### Files Created Automatically

The application will automatically create the following files on first run:

1. **Database File:**
   - `scraper_history.db` - SQLite database for search history
   - Location: Project root directory
   - **No manual creation needed** - automatically initialized

2. **Export Directory:**
   - `exports/` folder - stores CSV/PDF exports
   - Created automatically when you export results

### No Manual Configuration Required!

The application uses:
- **Automatic ChromeDriver management** via `webdriver-manager`
- **Auto-initialized database** with proper schema
- **Default configuration** optimized for Indian e-commerce sites

---

## 🚀 Running the Application

### Start the Application

From the project root directory:

```bash
python main.py
```

You should see output like:
```
============================================================
Web Scraper for Price Comparison
============================================================

Starting web server...
Access the application at: http://127.0.0.1:5000

Press CTRL+C to stop the server

 * Running on http://127.0.0.1:5000
```

### Access the Application

Open your web browser and navigate to:
- **Local Access:** http://127.0.0.1:5000
- **Network Access:** http://192.168.x.x:5000 (shown in terminal output)

### Stop the Application

Press `CTRL+C` in the terminal to stop the server.

---

## 📁 Project Structure

```
PESU_EC_CSE_K_P60_Web_Scraper_for_Price_Comparison_Team-5/
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── SETUP.md                         # This documentation file
├── .gitignore                       # Git ignore rules
│
├── web/                             # Flask web application
│   ├── app.py                       # Main Flask routes and logic
│   └── __init__.py
│
├── scrapers/                        # Scraping modules
│   ├── scraper_manager.py          # Orchestrates all scrapers
│   ├── scraper_controller.py       # Handles concurrent scraping
│   ├── scraper_registry.py         # Dynamic scraper registration
│   ├── base_scraper.py             # Abstract base class
│   ├── hybrid_scraper.py           # Static + Selenium hybrid
│   ├── selenium_config.py          # Selenium configuration
│   ├── amazon_scraper.py           # Amazon scraper
│   ├── flipkart_scraper.py         # Flipkart scraper
│   ├── snapdeal_scraper.py         # Snapdeal scraper
│   ├── myntra_scraper.py           # Myntra scraper
│   ├── croma_scraper.py            # Croma scraper
│   └── __init__.py
│
├── database/                        # Database layer
│   ├── database.py                 # SQLite database manager
│   ├── schema.sql                  # Database schema
│   └── __init__.py
│
├── pricing/                         # Advanced pricing utilities
│   ├── parser.py                   # Price parsing
│   ├── currency.py                 # Currency conversion
│   ├── compare.py                  # Price comparison
│   ├── normalize.py                # Price normalization
│   ├── types.py                    # Type definitions
│   └── __init__.py
│
├── utils/                           # Utility modules
│   ├── export_utils.py             # CSV/PDF export
│   ├── input_validator.py          # Input validation
│   └── __init__.py
│
└── templates/                       # HTML templates
    ├── index.html                  # Home page
    ├── results.html                # Search results
    ├── history.html                # Search history
    ├── statistics.html             # Analytics dashboard
    └── search_detail.html          # Individual search details
```

---

## 🎨 Features

### 1. **Real-time Price Comparison**
- Search for any product by name
- Automatically scrapes 5 e-commerce sites in parallel
- Results sorted by best price
- Shows product details: title, price, rating, availability

### 2. **Search History**
- All searches automatically saved to database
- View past searches with timestamps
- Click on any search to see detailed results
- Export historical search results

### 3. **Analytics Dashboard**
- Total searches performed
- Unique queries tracked
- Average results per search
- Average search duration
- Popular queries list
- Site performance metrics

### 4. **Data Export**
- Export results to CSV format
- Track all exports in database
- Download from current results or history

### 5. **Modern UI**
- Responsive design (mobile-friendly)
- Clean, professional interface
- Real-time loading indicators
- Gradient backgrounds and smooth animations

---

## 🛒 Supported E-commerce Sites

The application currently scrapes the following Indian e-commerce websites:

1. **Amazon India** (amazon.in)
   - Most reliable, fast scraping
   - Full product details

2. **Flipkart** (flipkart.com)
   - Reliable, good coverage
   - Full product details

3. **Snapdeal** (snapdeal.com)
   - Basic scraping support
   - May have variable results

4. **Myntra** (myntra.com)
   - Fashion-focused products
   - Uses dynamic scraping (Selenium)

5. **Croma** (croma.com)
   - Electronics products
   - May encounter bot detection

**Note:** Some sites may block automated requests. The application handles errors gracefully and shows results from available sites.

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. **"ModuleNotFoundError" when running**
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

#### 2. **Chrome/ChromeDriver version mismatch**
**Solution:** The `webdriver-manager` package handles this automatically. If issues persist:
- Update Chrome to the latest version
- Clear the webdriver cache: Delete `~/.wdm` folder

#### 3. **"Address already in use" error**
**Solution:** Port 5000 is occupied
- Kill existing Flask process
- Or change port in `main.py`: `app.run(port=5001)`

#### 4. **Database locked error**
**Solution:** Close any other database connections
- Stop any running instances of the application
- Delete `scraper_history.db` to recreate (will lose history)

#### 5. **No results from any site**
**Solution:** Check internet connection and firewall
- Verify internet connectivity
- Check if firewall is blocking Python
- Some sites may be temporarily blocking requests

#### 6. **Only getting results from 1-2 sites**
**Solution:** This is normal behavior
- Some sites have bot detection
- Amazon and Flipkart are most reliable
- Timeout is set to 30 seconds per site
- Results from available sites will be shown

#### 7. **Selenium/ChromeDriver errors**
**Solution:** 
```bash
pip install --upgrade selenium webdriver-manager
```
- Ensure Chrome is installed
- Restart the application

---

## 📊 Database Schema

The SQLite database includes the following tables:

### Tables:
1. **searches** - Main search records
2. **sites** - E-commerce site information
3. **search_results** - Individual product results
4. **search_metadata** - Search timing and stats
5. **export_history** - Export tracking

### Views:
1. **recent_searches** - Recent searches with stats
2. **popular_queries** - Most searched terms
3. **site_performance** - Site reliability metrics

**Location:** `scraper_history.db` (created automatically)

---

## 🔐 Environment Variables & Security

### Development Environment
For development and testing, the application uses default values and no environment variables are required.

### Production Environment

**⚠️ IMPORTANT: Set a secure SECRET_KEY for production deployments**

The Flask application uses a session secret key for security. In production, you MUST set a secure random key:

#### Setting SECRET_KEY:

**On Windows (PowerShell):**
```powershell
$env:SECRET_KEY = "your-secure-random-key-here"
python main.py
```

**On Linux/macOS:**
```bash
export SECRET_KEY="your-secure-random-key-here"
python main.py
```

**Generate a secure random key:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Example Production Setup:

1. Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Output: a1b2c3d4e5f6...
```

2. Set as environment variable:
```bash
export SECRET_KEY="a1b2c3d4e5f6..."  # Use your generated key
```

3. Run the application:
```bash
python main.py
```

### Other Optional Configuration:

- **No other environment variables required** for basic operation
- All scraper configuration is handled automatically
- Database is auto-initialized with default settings

**⚠️ Security Best Practices:**
- Never commit `SECRET_KEY` to version control
- Use different keys for development and production
- Change keys periodically in production
- Keep keys confidential and secure

---

## 📝 Usage Examples

### Example 1: Search by Product Name
1. Open http://127.0.0.1:5000
2. Enter: "iPhone 15 Pro"
3. Click Submit
4. View price comparison results

### Example 2: View Search History
1. Click "📜 History" in navigation
2. See all past searches
3. Click on any search to view details

### Example 3: Export Results
1. After a search, click "📥 Export to CSV"
2. File downloads automatically
3. Export tracked in database

### Example 4: View Analytics
1. Click "📊 Statistics" in navigation
2. View search metrics and trends

---

## 👥 Development Team

**Team-5 - Web Scraper for Price Comparison**
- Course: CSE (K) Section P60
- Institution: PESU EC Campus

---

## 📄 License

This project is for educational purposes as part of the PESU coursework.

---

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error messages in terminal
3. Ensure all prerequisites are installed
4. Verify internet connectivity

---

## 🎉 Quick Start Summary

1. **Install Python 3.8+** and Google Chrome
2. **Clone repository** and navigate to folder
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Run application:** `python main.py` (for development)
5. **Open browser:** http://127.0.0.1:5000
6. **Start searching!** 🚀

**⚠️ For Production:** Set `SECRET_KEY` environment variable before running (see Security section above)

---

**Last Updated:** November 2025
**Version:** 1.0.0
