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
- [Advanced Features](#advanced-features)
  - [Selenium Integration](#selenium-integration)
  - [Proxy & User-Agent Rotation](#proxy--user-agent-rotation)
- [Testing](#testing)
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
├── .flake8                          # Flake8 linter configuration
├── .pylintrc                        # Pylint configuration
├── pyproject.toml                   # Black, isort, pytest config
│
├── .github/                         # GitHub configuration
│   └── workflows/                   # GitHub Actions workflows
│       ├── test.yml                 # Comprehensive test suite (multi-version)
│       ├── ci.yml                   # Quick CI check (all branches)
│       └── code-quality.yml         # Code quality & security checks
│
├── tests/                           # Test suite directory
│   ├── __init__.py                  # Test package initialization
│   ├── test_regression_suite.py    # Test runner for CI/CD
│   ├── test_TC_CMP_01.py           # Price comparison tests
│   ├── test_TC_ERR_01.py           # Error handling tests
│   ├── test_TC_EXP_01.py           # Export functionality tests
│   ├── test_TC_INP_01.py           # Valid input validation tests
│   ├── test_TC_INP_02.py           # Invalid input validation tests
│   ├── test_TC_NRM_01.py           # Price normalization tests
│   ├── test_TC_PERF_01.py          # Performance tests
│   ├── test_TC_SCR_01.py           # Scraper manager tests
│   ├── test_TC_SCR_02.py           # Scraper registry tests
│   └── test_TC_UI_01.py            # Flask UI tests
│
├── web/                             # Flask web application
│   ├── app.py                       # Main Flask routes and logic
│   └── __init__.py
│
├── scrapers/                        # Scraping modules
│   ├── scraper_manager.py          # Orchestrates all scrapers
│   ├── async_scraper_controller.py # Async concurrent scraping controller
│   ├── scraper_controller.py       # Legacy scraper controller
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
│   ├── schema_sqlite.sql           # SQLite database schema
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
│   ├── input_handler.py            # Input validation
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
- **Asynchronous concurrent scraping** - all 5 sites scraped in parallel
- **Fast response time** - typically under 15 seconds (vs 30+ seconds with sequential scraping)
- **Optimized timeouts** - 10 seconds per scraper, 15 seconds total (5s buffer for overhead)
- Results sorted by best price
- Shows product details: title, price, rating, availability
- **Graceful degradation** - returns partial results if some scrapers fail

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

## 🚀 Advanced Features

### Selenium Integration

The scraper includes advanced Selenium integration for handling JavaScript-rendered websites and avoiding bot detection.

#### Overview

- **Intelligent Fallback**: Tries static scraping first for speed, automatically falls back to Selenium for dynamic content
- **Anti-Detection Features**: User-agent rotation, WebDriver masking, browser fingerprint spoofing
- **Retry Mechanism**: Configurable retry attempts with delays for improved reliability
- **Advanced Wait Logic**: Smart waiting for page load, AJAX requests, and lazy-loaded content

#### Key Components

**1. SeleniumConfig** (`scrapers/selenium_config.py`)
- Manages WebDriver creation and configuration
- Implements anti-detection measures
- Headless mode support with optimized performance settings

**2. SeleniumHelper Class**
Provides utility methods for robust Selenium operations:

| Method | Purpose |
|--------|---------|
| `wait_for_element()` | Wait for specific element to appear |
| `wait_for_any_element()` | Wait for any element from a list |
| `wait_for_page_load()` | Wait for complete page load including dynamic content |
| `wait_for_ajax()` | Wait for AJAX/jQuery requests to complete |
| `safe_find_element()` | Find element without throwing exceptions |
| `safe_find_elements()` | Find multiple elements safely |
| `scroll_to_bottom()` | Scroll to trigger lazy loading |
| `handle_lazy_loading()` | Handle infinite scroll pages |
| `human_like_delay()` | Add random delays (0.5-2s) to simulate human behavior |
| `click_element_safe()` | Robust clicking with scroll and JS fallback |
| `take_screenshot()` | Capture screenshots for debugging |

**3. HybridScraper** (`scrapers/hybrid_scraper.py`)
Base class for scrapers with intelligent fallback logic:

```python
class HybridScraper(BaseScraper):
    def scrape(self, query: str) -> dict:
        # Try static scraping first
        result = self._scrape_static(query)
        
        # Fallback to Selenium if needed
        if self._should_fallback_to_selenium(result):
            result = self._scrape_selenium(query)
        
        return result
```

#### Anti-Detection Features

**User-Agent Rotation**
- Pool of 23 realistic user agents
- Randomly rotates on each request
- Mimics real browsers (Chrome, Firefox, Safari, Edge)
- Covers Windows, macOS, Linux, and iOS platforms

**WebDriver Property Masking**
```javascript
// Hides automation indicators
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
delete navigator.__proto__.webdriver;
```

**Browser Fingerprint Spoofing**
- Realistic plugin arrays
- Permission query handling
- Chrome runtime emulation
- Language and timezone settings

**Stealth Techniques**
- `--disable-blink-features=AutomationControlled`
- `--disable-infobars`
- `--disable-dev-shm-usage`
- Excludes "enable-automation" switch
- Sets realistic window sizes

#### Intelligent Fallback Detection

The scraper automatically detects when Selenium is needed:

1. **Missing Data Detection**: Checks if critical fields (title, price) are empty
2. **JavaScript Indicators**: Looks for "Loading...", "Please wait", skeleton loaders
3. **Bot Detection**: Detects CAPTCHA, "Access Denied", bot challenge messages
4. **Content Length Check**: Flags suspiciously short HTML responses

```python
def _should_fallback_to_selenium(self, result: dict) -> bool:
    # Check for missing/invalid data
    if not result.get('title') or not result.get('price'):
        return True
    
    # Check for JavaScript loading indicators
    html = result.get('raw_html', '')
    js_indicators = ['loading...', 'please wait', 'skeleton']
    if any(indicator in html.lower() for indicator in js_indicators):
        return True
    
    # Check for bot detection
    bot_messages = ['captcha', 'access denied', 'unusual traffic']
    if any(msg in html.lower() for msg in bot_messages):
        return True
    
    return False
```

#### Retry Mechanism

Configurable retry logic for improved reliability:

```python
def _scrape_with_retry(self, query: str, max_retries: int = 2) -> dict:
    for attempt in range(max_retries):
        try:
            result = self.scrape(query)
            if result and result.get('title'):
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Delay between retries
                continue
            raise
```

#### Usage Examples

**Basic Selenium Scraping**:
```python
from scrapers.selenium_config import SeleniumConfig, SeleniumHelper

# Create driver
config = SeleniumConfig(headless=True, window_size="1920,1080")
driver = config.create_driver()
helper = SeleniumHelper(driver)

# Navigate and wait
driver.get("https://example.com")
helper.wait_for_page_load()

# Find elements safely
element = helper.safe_find_element(By.CSS_SELECTOR, ".product-title")
if element:
    title = element.text

# Handle lazy loading
helper.handle_lazy_loading(scroll_pause=2, max_scrolls=5)

# Clean up
driver.quit()
```

**Using Demo Script**:
```bash
python tests/demo_selenium.py
```

The demo showcases:
- Anti-detection features in action
- User-agent rotation
- Wait mechanisms
- Lazy loading handling
- Screenshot capture
- Human-like interactions

#### Best Practices

1. **Use Static Scraping First**: Always try static scraping before Selenium for better performance
2. **Implement Timeouts**: Set reasonable timeouts to avoid hanging (default: 10s per site)
3. **Handle Errors Gracefully**: Use try-except blocks and return partial results
4. **Add Human-like Delays**: Use `human_like_delay()` between actions
5. **Monitor for Changes**: Websites update frequently; test scrapers regularly
6. **Use Headless Mode**: Run headless in production for better resource usage
7. **Clean Up Resources**: Always call `driver.quit()` to free resources

#### Performance Considerations

- **Static Scraping**: ~1-2 seconds per site
- **Selenium Scraping**: ~3-5 seconds per site
- **Memory Usage**: ~100-200 MB per Selenium instance
- **Concurrent Limit**: Recommend max 3-5 parallel Selenium instances

#### Troubleshooting

**ChromeDriver Issues**:
```bash
pip install --upgrade selenium webdriver-manager
```

**Selenium Timeout**:
- Increase timeout in SeleniumHelper methods
- Check internet connection
- Verify site is accessible

**Bot Detection**:
- Ensure anti-detection features are enabled
- Add more delays with `human_like_delay()`
- Rotate user agents more frequently
- Consider using proxy rotation (see next section)

### Proxy & User-Agent Rotation

The scraper includes built-in support for proxy and user-agent rotation to prevent IP bans and bot detection.

#### Quick Start

Proxy rotation is handled automatically when configured in environment variables or `scrapers/selenium_config.py`.

#### Features

- **23 User Agents**: Realistic browser user agents from Chrome, Firefox, Safari, Edge across Windows, macOS, Linux, and iOS
- **Automatic Rotation**: User agents rotate randomly on each request
- **Proxy Support**: Configure HTTP/HTTPS/SOCKS proxies
- **Failure Handling**: Automatic proxy rotation on failure
- **Success Tracking**: Monitors proxy success rates

#### Configuration

**Method 1: Environment Variables**
```bash
# Single proxy
export HTTP_PROXY="http://proxy-server:port"
export HTTPS_PROXY="http://proxy-server:port"

# With authentication
export HTTP_PROXY="http://user:pass@proxy-server:port"
```

**Method 2: Code Configuration**
```python
from scrapers.selenium_config import SeleniumConfig

# With proxy
config = SeleniumConfig(
    headless=True,
    proxy="http://proxy-server:port"
)
driver = config.create_driver()
```

#### User-Agent Pool

The scraper includes 23 realistic user agents:
- **Chrome** (10 agents): Windows, macOS, Linux - multiple versions
- **Firefox** (7 agents): Windows, macOS, Linux - multiple versions
- **Safari** (4 agents): macOS, iOS (iPhone/iPad)
- **Edge** (2 agents): Windows - multiple versions

User agents are randomly selected on each request to avoid detection patterns and simulate diverse traffic.

#### Proxy Services

**Free Proxies** (testing only):
- Free Proxy List: https://free-proxy-list.net/
- ProxyScrape: https://proxyscrape.com/

**Paid Proxies** (production):
- Bright Data: https://brightdata.com/
- Oxylabs: https://oxylabs.io/
- Smartproxy: https://smartproxy.com/

#### Best Practices

1. **Rotate Frequently**: Change user agents on each request
2. **Use Quality Proxies**: Free proxies are unreliable; invest in paid proxies for production
3. **Monitor Success Rates**: Track which proxies work best
4. **Add Delays**: Combine with human-like delays for better results
5. **Respect Robots.txt**: Check site policies before aggressive scraping
6. **Handle Failures**: Implement retry logic with different proxies

#### Testing Rotation

Run the rotation tests:
```bash
pytest tests/test_rotation.py -v
```

Tests verify:
- User-agent rotation works correctly
- Proxy configuration is applied
- Fallback mechanisms function
- Multiple requests use different agents

---

## 🧪 Testing

### Test Suite Overview

The project includes a comprehensive test suite for GitHub CI/CD integration, covering all critical functionality areas.

### Running Tests

**Install pytest (if not already installed):**
```bash
pip install pytest
```

**Run all tests:**
```bash
pytest tests/
```

**Run specific test:**
```bash
pytest tests/test_TC_CMP_01.py
```

**Run with verbose output:**
```bash
pytest tests/ -v
```

**Run regression suite (CI/CD):**
```bash
python tests/test_regression_suite.py
```

### Test Cases

#### 1. **TC_CMP_01** - Price Comparison Ranking
- **File:** `tests/test_TC_CMP_01.py`
- **Purpose:** Validates that `rank_offers()` correctly sorts products by price
- **Coverage:** Pricing comparison logic

#### 2. **TC_ERR_01** - Error Handling
- **File:** `tests/test_TC_ERR_01.py`
- **Purpose:** Tests error handling for invalid scraper responses
- **Coverage:** Error management

#### 3. **TC_EXP_01** - Export Functionality
- **File:** `tests/test_TC_EXP_01.py`
- **Purpose:** Validates CSV export functionality
- **Coverage:** Data export utilities

#### 4. **TC_INP_01** - Valid Input Validation
- **File:** `tests/test_TC_INP_01.py`
- **Purpose:** Tests input validation for product names
- **Coverage:** Input validation (valid cases)

#### 5. **TC_INP_02** - Invalid Input Validation
- **File:** `tests/test_TC_INP_02.py`
- **Purpose:** Tests rejection of invalid/empty inputs
- **Coverage:** Input validation (edge cases)

#### 6. **TC_NRM_01** - Price Normalization
- **File:** `tests/test_TC_NRM_01.py`
- **Purpose:** Validates price parsing and normalization
- **Coverage:** Price parsing utilities

#### 7. **TC_PERF_01** - Performance Testing
- **File:** `tests/test_TC_PERF_01.py`
- **Purpose:** Ensures scraping completes within performance threshold (<5s for single scraper)
- **Coverage:** Performance benchmarks

#### 8. **TC_SCR_01** - Scraper Manager
- **File:** `tests/test_TC_SCR_01.py`
- **Purpose:** Tests scraper manager orchestration
- **Coverage:** ScraperManager integration

#### 9. **TC_SCR_02** - Scraper Registry
- **File:** `tests/test_TC_SCR_02.py`
- **Purpose:** Validates dynamic scraper registration/unregistration
- **Coverage:** ScraperRegistry functionality

#### 10. **TC_UI_01** - Flask Routes
- **File:** `tests/test_TC_UI_01.py`
- **Purpose:** Tests Flask application routes and responses
- **Coverage:** Web application endpoints

### GitHub CI/CD Integration

The test suite is fully integrated with GitHub Actions for automated testing.

#### Workflow Files

Located in `.github/workflows/`:

1. **`test.yml`** - Comprehensive Test Suite
   - Runs on: push/PR to main, develop, feature/async-docs-cleanup
   - Tests on: Python 3.8, 3.9, 3.10, 3.11
   - Includes: Code quality checks, coverage reports
   - Checks: Black, isort, flake8, pylint, bandit
   - Duration: ~3-4 minutes

2. **`ci.yml`** - Quick CI Check
   - Runs on: push to main, develop, feature/async-docs-cleanup
   - Tests on: Python 3.11
   - Fast regression suite (fail-fast mode)
   - Duration: ~30-60 seconds

3. **`code-quality.yml`** - Code Quality & Security
   - Runs on: push/PR to main, develop, feature/async-docs-cleanup
   - Tools: Black, isort, flake8, pylint, bandit, safety
   - Generates security reports
   - Non-blocking (continues on errors)
   - Duration: ~2-3 minutes

#### Branch Strategy

**Development Workflow:**
```
feature/async-docs-cleanup → develop → main
```

1. **feature/async-docs-cleanup** - Active development branch
   - Complete all changes here
   - CI/CD runs on every push
   - Merge to develop when ready

2. **develop** - Integration branch
   - Receives merges from feature branches
   - CI/CD validates integration
   - Merge to main for teacher review

3. **main** - Production/Review branch
   - Teacher reviews and approves
   - Final merge happens here
   - Protected by CI/CD checks

#### How It Works

**On every push/pull request:**
1. GitHub Actions automatically triggers
2. Sets up Python environment
3. Installs dependencies (with caching)
4. Runs regression suite: `python test_regression_suite.py`
5. Runs full test suite: `pytest -v --cov`
6. Uploads coverage reports (Python 3.11 only)
7. Reports pass/fail status on commit

**Viewing Results:**
- Go to repository → "Actions" tab
- Click on any workflow run to see details
- Green ✓ = All tests passed
- Red ✗ = Tests failed (click for details)

**Manual Trigger:**
- Go to "Actions" tab → "Run Test Suite"
- Click "Run workflow" button
- Select branch and run

**Key Features:**
- Fast execution for CI/CD pipelines
- Isolated unit tests (no external dependencies)
- Pip package caching for faster builds
- Matrix testing across Python versions
- Exit codes for CI/CD pass/fail status

**Regression Suite:**
- **File:** `tests/test_regression_suite.py`
- **Usage:** `python tests/test_regression_suite.py`
- **Behavior:** Runs all tests, fails fast on first error
- **Exit Code:** 0 (pass) or non-zero (fail)

### Test Coverage Areas

| Area | Test Cases | Coverage |
|------|-----------|----------|
| Price Comparison | TC_CMP_01 | Ranking logic |
| Error Handling | TC_ERR_01 | Exception management |
| Data Export | TC_EXP_01 | CSV generation |
| Input Validation | TC_INP_01, TC_INP_02 | Input sanitization |
| Price Parsing | TC_NRM_01 | Normalization |
| Performance | TC_PERF_01 | Speed benchmarks |
| Scraping | TC_SCR_01, TC_SCR_02 | Core functionality |
| Web Interface | TC_UI_01 | Flask routes |

### Code Quality Tools

The project uses industry-standard tools for code quality and security:

#### Formatting & Style
- **Black** - Automatic code formatting (PEP 8 compliant)
- **isort** - Import statement sorting and organization
- **flake8** - Style guide enforcement and linting
- **pylint** - Comprehensive code analysis

#### Security & Safety
- **Bandit** - Security vulnerability scanning
- **Safety** - Dependency vulnerability checking

#### Running Locally

**Install quality tools:**
```bash
pip install black isort flake8 pylint bandit safety
```

**Format code:**
```bash
black .
isort .
```

**Check code quality:**
```bash
flake8 .
pylint **/*.py
```

**Security scan:**
```bash
bandit -r . -ll
safety check
```

#### Configuration Files

- `.flake8` - Flake8 configuration
- `.pylintrc` - Pylint settings
- `pyproject.toml` - Black, isort, pytest configuration

### Best Practices

- Tests use **mock scrapers** (no actual web requests)
- Fast execution (< 5 seconds total)
- Isolated from external dependencies
- Deterministic results for CI/CD
- Clear assertions for debugging
- Code formatted with Black before commits
- Security scanned with Bandit

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
- Timeout is set to 10 seconds per site (15 seconds total with 5s overhead buffer)
- Results from available sites will be shown
- **Async scraping** runs all sites concurrently for faster results

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
