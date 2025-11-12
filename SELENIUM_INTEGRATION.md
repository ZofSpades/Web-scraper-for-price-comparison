# Selenium Integration for Dynamic Pages

## Overview

This document describes the enhanced Selenium integration for handling JavaScript-rendered websites. The scraper now intelligently falls back to Selenium when static scraping fails or detects dynamic content.

## Features

### 1. **Intelligent Fallback Mechanism**
- **Static-First Approach**: Attempts static scraping first for better performance
- **Automatic Detection**: Detects when a page requires JavaScript rendering
- **Seamless Fallback**: Automatically switches to Selenium when needed
- **Retry Logic**: Multiple retry attempts for improved reliability

### 2. **Enhanced Anti-Detection**
The Selenium configuration includes advanced stealth features:
- **Random User-Agent Rotation**: Pool of realistic user agents
- **WebDriver Property Masking**: Hides automation indicators
- **Browser Fingerprint Spoofing**: Mimics real browser behavior
- **Plugin & Permission Simulation**: Appears as normal browser
- **Chrome Runtime Emulation**: Full Chrome environment simulation

### 3. **Advanced Wait Mechanisms**
- **Page Load Detection**: Waits for complete page load
- **AJAX Completion**: Detects when dynamic requests finish
- **Element Presence**: Waits for specific elements to appear
- **Lazy Loading Support**: Handles infinite scroll and lazy-loaded content
- **Human-like Delays**: Random delays to avoid detection

### 4. **Robust Error Handling**
- **Multiple Retry Attempts**: Configurable retry count
- **Graceful Degradation**: Falls back through multiple strategies
- **Comprehensive Logging**: Detailed logs for debugging
- **Safe Element Access**: Never crashes on missing elements

## Architecture

### Class Hierarchy

```
BaseScraper (Abstract)
    ↓
HybridScraper (Abstract)
    ↓
├── AmazonScraper
├── FlipkartScraper
├── MyntraScraper
├── CromaScraper
└── SnapdealScraper
```

### Key Components

#### 1. **SeleniumConfig**
Manages WebDriver creation and configuration.

```python
config = SeleniumConfig(headless=True, window_size="1920,1080")
driver = config.create_driver()
```

**Features:**
- Headless mode support
- Anti-detection measures
- Stealth JavaScript injection
- Optimized performance settings

#### 2. **SeleniumHelper**
Provides utility methods for Selenium operations.

**Key Methods:**
- `wait_for_element()` - Wait for element to appear
- `wait_for_page_load()` - Wait for page to fully load
- `wait_for_ajax()` - Wait for AJAX requests
- `handle_lazy_loading()` - Scroll and load dynamic content
- `safe_find_element()` - Find element without exceptions
- `human_like_delay()` - Add random delays
- `click_element_safe()` - Safely click with retries

#### 3. **HybridScraper**
Base class for scrapers with fallback logic.

**Scraping Flow:**
```
1. Check if forced Selenium mode
   ↓
2. Try static scraping
   ↓
3. Validate result
   ↓
4. If invalid/incomplete → Fallback to Selenium
   ↓
5. Retry on failure
   ↓
6. Return result or error
```

## Usage Examples

### Basic Usage

```python
from scrapers.amazon_scraper import AmazonScraper

scraper = AmazonScraper()
result = scraper.scrape("https://www.amazon.in/product/...")
print(result)
```

### Force Selenium Mode

```python
scraper = AmazonScraper()
scraper.set_selenium_mode(True)  # Always use Selenium
result = scraper.scrape("laptop")
```

### Configure Retry Attempts

```python
scraper = AmazonScraper()
scraper.set_retry_attempts(3)  # Try up to 3 times
result = scraper.scrape("smartphone")
```

### Non-Headless Mode (for Debugging)

```python
scraper = AmazonScraper()
scraper.set_headless(False)  # Show browser window
result = scraper.scrape("headphones")
```

### Get Scraping Statistics

```python
scraper = AmazonScraper()
result = scraper.scrape("gaming mouse")
stats = scraper.get_scraping_stats()
print(f"Method used: {stats['method_used']}")  # 'static' or 'selenium'
```

## Fallback Triggers

The scraper automatically falls back to Selenium when it detects:

### 1. **Missing or Invalid Data**
- Title is missing, "N/A", or error
- Price is missing, "N/A", or error
- Title is suspiciously short (< 5 characters)

### 2. **JavaScript Loading Indicators**
- "loading", "please wait", "redirecting"
- "enable javascript"

### 3. **Bot Detection**
- "access denied", "blocked"
- "captcha", "verify", "robot"

### 4. **Scraping Errors**
- Network errors
- Timeout errors
- Parsing errors

## Site-Specific Implementations

### Amazon
- **Static**: Fast for most product pages
- **Selenium**: Used when search results require JS or anti-bot triggered
- **Selectors**: Multiple fallback selectors for title, price, rating

### Flipkart
- **Static**: Works for direct product links
- **Selenium**: Used for search results and new layout
- **Selectors**: Comprehensive class-based selectors

### Myntra
- **Selenium Preferred**: Heavy JavaScript usage
- **Dynamic Content**: Product listings are JS-rendered
- **Wait Strategy**: 4-second delay for full content load

### Croma
- **Hybrid**: Static works for most pages
- **Selenium**: Used for lazy-loaded content
- **Search**: Dynamic search results handling

### Snapdeal
- **Hybrid**: Balanced approach
- **Selenium**: Used when static fails
- **Robust Logging**: Detailed error tracking

## Configuration Options

### Selenium Settings

```python
# In SeleniumConfig
config = SeleniumConfig(
    headless=True,              # Run without GUI
    window_size="1920,1080"     # Browser window size
)

# Modify timeouts
config.page_load_timeout = 30    # Page load timeout
config.implicit_wait = 10        # Element wait timeout
config.script_timeout = 30       # Script execution timeout
```

### Scraper Settings

```python
scraper = AmazonScraper()

# Selenium mode
scraper.set_selenium_mode(False)  # Fallback mode (default)
scraper.set_selenium_mode(True)   # Always use Selenium

# Headless mode
scraper.set_headless(True)   # Run without GUI (default)
scraper.set_headless(False)  # Show browser window

# Retry attempts
scraper.set_retry_attempts(2)  # Number of retry attempts
scraper.retry_delay = 1        # Delay between retries (seconds)
```

## Performance Considerations

### Static Scraping
- **Speed**: ~0.5-2 seconds per page
- **Resource Usage**: Minimal (HTTP requests only)
- **Reliability**: 70-80% success rate

### Selenium Scraping
- **Speed**: ~3-5 seconds per page (includes page load + wait)
- **Resource Usage**: Higher (full browser instance)
- **Reliability**: 90-95% success rate

### Recommendations
1. **Default**: Use fallback mode (static first)
2. **Known Dynamic Sites**: Force Selenium mode
3. **Batch Scraping**: Use static mode with retry
4. **Development**: Use non-headless mode for debugging

## Debugging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('scrapers')
logger.setLevel(logging.DEBUG)
```

### Take Screenshots

```python
from scrapers.selenium_config import SeleniumConfig, SeleniumHelper

config = SeleniumConfig(headless=False)
driver = config.create_driver()
driver.get("https://example.com")

SeleniumHelper.take_screenshot(driver, 'debug.png')
driver.quit()
```

### Check Scraping Method Used

```python
scraper = AmazonScraper()
result = scraper.scrape("laptop")
method = scraper.get_scraping_method()
print(f"Used method: {method}")  # 'static' or 'selenium'
```

## Best Practices

### 1. **Start with Fallback Mode**
Let the scraper decide when to use Selenium:
```python
scraper = AmazonScraper()  # Default fallback mode
```

### 2. **Use Selenium Mode for Known Dynamic Sites**
If you know a site requires JavaScript:
```python
scraper = MyntraScraper()
scraper.set_selenium_mode(True)
```

### 3. **Add Appropriate Delays**
For sites with anti-scraping measures:
```python
from scrapers.selenium_config import SeleniumHelper

driver = config.create_driver()
driver.get(url)
SeleniumHelper.human_like_delay(1, 3)  # Random 1-3s delay
```

### 4. **Handle Lazy Loading**
For infinite scroll or lazy-loaded content:
```python
SeleniumHelper.handle_lazy_loading(driver, scroll_pause_time=2, max_scrolls=5)
```

### 5. **Always Close Drivers**
Use try-finally or context managers:
```python
driver = None
try:
    driver = config.create_driver()
    # ... scraping logic ...
finally:
    if driver:
        driver.quit()
```

## Troubleshooting

### Issue: "ChromeDriver not found"
**Solution**: The webdriver-manager will auto-download. Ensure internet connection.

### Issue: Selenium hangs or times out
**Solution**: 
- Increase timeouts: `config.page_load_timeout = 60`
- Check network connectivity
- Use non-headless mode to debug: `scraper.set_headless(False)`

### Issue: Bot detection / CAPTCHA
**Solution**:
- Increase delays: `SeleniumHelper.human_like_delay(2, 5)`
- Rotate user agents (already implemented)
- Check site's robots.txt and terms of service

### Issue: Elements not found
**Solution**:
- Use wait methods: `SeleniumHelper.wait_for_element(driver, By.ID, 'element-id')`
- Check if selectors are correct
- Wait for page load: `SeleniumHelper.wait_for_page_load(driver)`

### Issue: High resource usage
**Solution**:
- Use headless mode: `scraper.set_headless(True)`
- Close drivers properly
- Use static scraping when possible
- Limit concurrent Selenium instances

## Future Enhancements

### Planned Features
1. **Proxy Support**: Rotate proxies for large-scale scraping
2. **Cookie Management**: Persist sessions across requests
3. **Screenshot Capture**: Auto-capture on errors
4. **Performance Metrics**: Track scraping speed and success rates
5. **Browser Pool**: Reuse browser instances for efficiency
6. **Async Selenium**: Parallel Selenium execution

### Contribution Guidelines
When adding new scrapers:
1. Extend `HybridScraper` class
2. Implement both `_scrape_static()` and `_scrape_with_selenium()`
3. Use multiple selector fallbacks
4. Add proper error handling
5. Test with both static and Selenium modes

## Dependencies

```
selenium==4.15.2
webdriver-manager==4.0.1
beautifulsoup4==4.12.2
requests==2.31.0
lxml==4.9.3
```

Install with:
```bash
pip install -r requirements.txt
```

## License

This project uses Selenium WebDriver, which is licensed under Apache 2.0.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Selenium documentation: https://www.selenium.dev/documentation/
3. Open an issue on the project repository
