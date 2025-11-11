# Proxy & User-Agent Rotation Guide

## Overview

This web scraper now includes advanced proxy and user-agent rotation capabilities to prevent IP bans and blocking. The system automatically rotates between different user agents and proxy servers to avoid detection.

## Features

### 1. User-Agent Rotation
- **20+ Modern User Agents**: Includes Chrome, Firefox, Safari, and Edge on Windows, macOS, and Linux
- **Mobile Support**: iOS and Android user agents
- **Automatic Rotation**: Rotates on each request
- **Random Selection**: Can pick randomly or rotate sequentially

### 2. Proxy Rotation
- **Automatic Failover**: Failed proxies are automatically disabled
- **Retry Logic**: Automatically retries with different proxies
- **Cooldown System**: Failed proxies are temporarily disabled (5 minutes)
- **Success Tracking**: Tracks proxy performance
- **Multiple Formats**: Supports HTTP, HTTPS, and SOCKS5 proxies
- **Authentication**: Supports username/password authentication

### 3. Integration
- **Seamless**: Works with both static (requests) and dynamic (Selenium) scraping
- **Transparent**: No changes needed to existing scraper code
- **Centralized**: Single configuration for all scrapers

## Quick Start

### 1. Basic Setup (No Proxies)

The rotation system works immediately with user-agent rotation only:

```python
from scrapers.amazon_scraper import AmazonScraper

# User-agent rotation is automatic
scraper = AmazonScraper()
result = scraper.scrape("laptop")
```

### 2. With Proxies

```python
from scrapers.base_scraper import BaseScraper
from scrapers.amazon_scraper import AmazonScraper

# Configure proxies (one-time setup)
proxies = [
    'http://proxy1.example.com:8080',
    'http://user:pass@proxy2.example.com:3128',
]
BaseScraper.configure_proxies(proxies)

# Use scrapers normally
scraper = AmazonScraper()
result = scraper.scrape("laptop")
```

### 3. Check Status

```python
status = BaseScraper.get_rotation_status()
print(f"User Agents: {status['user_agents_count']}")
print(f"Proxies: {status['available_proxies']}/{status['total_proxies']}")
```

## Detailed Usage

### User-Agent Rotation

User agents are automatically rotated on every request. The system includes:

- **Desktop Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile Browsers**: Mobile Chrome, Mobile Safari
- **Operating Systems**: Windows, macOS, Linux, Android, iOS

You can add custom user agents:

```python
from scrapers.base_scraper import BaseScraper

# Access the rotation manager
rotation_manager = BaseScraper._rotation_manager
rotation_manager.user_agent_rotator.add_user_agent(
    "Mozilla/5.0 (Custom User Agent String)"
)
```

### Proxy Configuration

#### Proxy Formats

```python
# HTTP proxy
'http://host:port'

# HTTPS proxy  
'https://host:port'

# With authentication
'http://username:password@host:port'

# SOCKS5 (requires additional setup)
'socks5://host:port'
```

#### Adding Proxies

```python
# Single proxy
BaseScraper.configure_proxies(['http://proxy.com:8080'])

# Multiple proxies
BaseScraper.configure_proxies([
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    'http://user:pass@proxy3.com:3128',
])

# Add more at runtime
BaseScraper.configure_proxies(['http://proxy4.com:8080'])
```

#### Proxy Rotation Logic

1. **Sequential Rotation**: Proxies are used in order
2. **Failure Handling**: Failed proxy is marked and skipped
3. **Cooldown**: Failed proxy disabled for 5 minutes
4. **Max Failures**: After 3 failures, proxy is removed temporarily
5. **Automatic Recovery**: After cooldown, proxy is retried

### Advanced Usage

#### HybridScraper Integration

The `HybridScraper` class includes helper methods:

```python
from scrapers.amazon_scraper import AmazonScraper

scraper = AmazonScraper()

# Make request with automatic rotation
response = scraper.make_request('https://example.com', timeout=10)

# Create Selenium driver with rotation
driver = scraper.create_selenium_driver()
```

#### Manual Proxy Control

```python
from scrapers.base_scraper import BaseScraper

scraper = BaseScraper()

# Get next proxy
proxy = scraper.get_proxy()

# Get random proxy
proxy = scraper.get_random_proxy()

# Mark success/failure manually
scraper.mark_proxy_success(proxy)
scraper.mark_proxy_failure(proxy)
```

## Proxy Services

### Recommended Paid Services

For production use, we recommend paid proxy services:

1. **BrightData (Luminati)** - Premium residential proxies
   - Website: https://brightdata.com/
   - Best for: E-commerce, large-scale scraping
   
2. **Oxylabs** - Residential and datacenter proxies
   - Website: https://oxylabs.io/
   - Best for: Reliable, high-performance scraping

3. **ScraperAPI** - Proxy + scraping API
   - Website: https://www.scraperapi.com/
   - Best for: Easy integration, handles rotation

4. **Smartproxy** - Affordable residential proxies
   - Website: https://smartproxy.com/
   - Best for: Budget-conscious projects

5. **ProxyMesh** - Rotating proxy service
   - Website: https://proxymesh.com/
   - Best for: Simple rotation needs

### Service-Specific Configuration

#### BrightData Example

```python
proxies = [
    'http://username-session-random123:password@zproxy.lum-superproxy.io:22225',
]
BaseScraper.configure_proxies(proxies)
```

#### Oxylabs Example

```python
proxies = [
    'http://customer-username:password@pr.oxylabs.io:7777',
]
BaseScraper.configure_proxies(proxies)
```

#### ScraperAPI Example

```python
proxies = [
    'http://scraperapi:YOUR_API_KEY@proxy-server.scraperapi.com:8001',
]
BaseScraper.configure_proxies(proxies)
```

### Free Proxies (Not Recommended)

⚠️ **Warning**: Free proxies are unreliable, slow, and potentially insecure. Use only for testing.

Sources for free proxies:
- https://free-proxy-list.net/
- https://www.sslproxies.org/
- https://www.proxy-list.download/

## Environment Variables

For production, use environment variables:

```bash
# Single proxy
export SCRAPER_PROXY="http://user:pass@proxy.com:8080"

# Multiple proxies (comma-separated)
export SCRAPER_PROXIES="http://proxy1:8080,http://user:pass@proxy2:3128"
```

Python code:

```python
import os

def load_proxies():
    proxies_str = os.getenv('SCRAPER_PROXIES', '')
    if proxies_str:
        return [p.strip() for p in proxies_str.split(',') if p.strip()]
    return []

BaseScraper.configure_proxies(load_proxies())
```

## Best Practices

### 1. Choose Right Proxy Type

- **Residential Proxies**: Best for e-commerce (Amazon, Flipkart, etc.)
- **Datacenter Proxies**: Cheaper, good for less restrictive sites
- **Rotating Proxies**: Automatic rotation by provider
- **Sticky Sessions**: Maintain same IP for duration (for authenticated scraping)

### 2. Implement Rate Limiting

```python
import time

for product in products:
    result = scraper.scrape(product)
    time.sleep(2)  # 2 second delay between requests
```

### 3. Monitor Performance

```python
import logging

logging.basicConfig(level=logging.INFO)

# Logs will show:
# - Proxy failures
# - Proxy successes
# - Rotation events
```

### 4. Handle Errors Gracefully

```python
result = scraper.scrape(url)

if 'error' in result:
    # Handle error
    print(f"Scraping failed: {result['error']}")
    # System already rotated proxy, safe to retry
    result = scraper.scrape(url)
```

### 5. Test Before Production

```python
# Test your proxies
from scrapers.rotation_manager import ProxyRotator

rotator = ProxyRotator(your_proxies)
for proxy in your_proxies:
    try:
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=rotator._format_proxy(proxy),
            timeout=10
        )
        print(f"✓ {proxy}: {response.json()}")
    except Exception as e:
        print(f"✗ {proxy}: {e}")
```

### 6. Respect Website Terms

- Check `robots.txt`
- Don't overload servers
- Use appropriate delays
- Follow terms of service

### 7. Secure Credentials

```python
# ✗ BAD: Hardcoded credentials
proxies = ['http://user:password@proxy.com:8080']

# ✓ GOOD: Environment variables
import os
proxy = os.getenv('SCRAPER_PROXY')
```

## Troubleshooting

### No Proxies Working

```python
status = BaseScraper.get_rotation_status()
if status['available_proxies'] == 0:
    print("All proxies failed!")
    # 1. Check proxy credentials
    # 2. Verify proxy service is active
    # 3. Test proxies manually
    # 4. Check firewall/network settings
```

### Proxies Too Slow

```python
# Increase timeout
scraper.timeout = 30  # seconds

# Or use faster proxies
# Consider datacenter proxies instead of residential
```

### Getting Blocked Despite Proxies

1. **Add More Delays**: Requests too frequent
2. **Check User-Agent**: May need more variety
3. **Try Different Proxy Type**: Switch to residential
4. **Verify Proxy Location**: Some sites block certain countries
5. **Check Headers**: Add more realistic headers

### Proxy Authentication Errors

```python
# Ensure format is correct:
'http://username:password@host:port'

# URL encode special characters in password
import urllib.parse
password = urllib.parse.quote('p@ssw0rd!')
proxy = f'http://user:{password}@host:port'
```

## Architecture

### Class Hierarchy

```
RotationManager
├── UserAgentRotator
│   ├── get_random()
│   ├── get_next()
│   └── add_user_agent()
└── ProxyRotator
    ├── get_random()
    ├── get_next()
    ├── mark_failure()
    └── mark_success()

BaseScraper
├── _rotation_manager (class-level)
├── get_headers() → rotated user-agent
├── get_proxy() → next available proxy
└── configure_proxies() → setup

HybridScraper (extends BaseScraper)
├── make_request() → requests with rotation
└── create_selenium_driver() → Selenium with rotation
```

### Request Flow

```
1. Scraper.scrape(url)
   ↓
2. get_headers() → rotated User-Agent
   ↓
3. get_proxy() → next available proxy
   ↓
4. Make request
   ↓
5. Success? → mark_proxy_success()
   Failure? → mark_proxy_failure() → retry with new proxy
```

## API Reference

### BaseScraper

```python
# Class methods
BaseScraper.configure_proxies(proxy_list: List[str])
BaseScraper.get_rotation_status() -> Dict

# Instance methods
scraper.get_headers() -> Dict[str, str]
scraper.get_proxy() -> Optional[Dict[str, str]]
scraper.get_random_proxy() -> Optional[Dict[str, str]]
scraper.mark_proxy_failure(proxy: Optional[Dict])
scraper.mark_proxy_success(proxy: Optional[Dict])
```

### HybridScraper

```python
scraper.make_request(url: str, **kwargs) -> requests.Response
scraper.create_selenium_driver() -> webdriver.Chrome
```

### RotationManager

```python
manager.get_random_config() -> Tuple[str, Optional[Dict]]
manager.get_next_config() -> Tuple[str, Optional[Dict]]
manager.get_headers_with_rotation(base: Dict) -> Dict
manager.add_proxies(proxy_list: List[str])
manager.has_proxies() -> bool
manager.get_status() -> Dict
```

## Examples

See `rotation_config_example.py` for complete working examples.

## Support

For issues or questions:
1. Check logs for error messages
2. Verify proxy credentials and format
3. Test proxies independently
4. Review best practices section
5. Contact proxy service support if provider-specific issue

## License

Same as main project.
