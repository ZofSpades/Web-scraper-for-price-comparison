"""
Example Configuration for Proxy and User-Agent Rotation
Copy this to your main application file or configuration module.
"""

from scrapers.base_scraper import BaseScraper

# ============================================================
# PROXY CONFIGURATION
# ============================================================

# Example proxy list - replace with your actual proxies
# Formats supported:
#   - http://host:port
#   - http://username:password@host:port
#   - https://host:port
#   - socks5://host:port

PROXY_LIST = [
    # Free proxies (not recommended for production)
    # 'http://proxy1.example.com:8080',
    # 'http://proxy2.example.com:3128',
    
    # Authenticated proxies (recommended)
    # 'http://username:password@premium-proxy1.com:8080',
    # 'http://username:password@premium-proxy2.com:8080',
    
    # Leave empty to use no proxies
]

# Popular paid proxy services (examples):
# - BrightData (formerly Luminati): https://brightdata.com/
# - Oxylabs: https://oxylabs.io/
# - ScraperAPI: https://www.scraperapi.com/
# - Smartproxy: https://smartproxy.com/
# - ProxyMesh: https://proxymesh.com/

# ============================================================
# INITIALIZATION
# ============================================================

def configure_rotation():
    """
    Initialize proxy and user-agent rotation.
    Call this before starting any scraping operations.
    """
    if PROXY_LIST:
        BaseScraper.configure_proxies(PROXY_LIST)
        print(f"✓ Configured {len(PROXY_LIST)} proxies")
    else:
        print("⚠ No proxies configured - using direct connection")
    
    # Check rotation status
    status = BaseScraper.get_rotation_status()
    print(f"✓ User agents available: {status['user_agents_count']}")
    print(f"✓ Proxies: {status['available_proxies']}/{status['total_proxies']}")
    print(f"✓ Proxy rotation: {'enabled' if status['proxies_enabled'] else 'disabled'}")

# ============================================================
# USAGE EXAMPLES
# ============================================================

def example_basic_usage():
    """Example: Basic usage with rotation"""
    from scrapers.amazon_scraper import AmazonScraper
    
    # Configure rotation first
    configure_rotation()
    
    # Use scraper normally - rotation happens automatically
    scraper = AmazonScraper()
    result = scraper.scrape("laptop")
    print(result)


def example_custom_proxies():
    """Example: Add proxies dynamically"""
    # Add more proxies at runtime
    additional_proxies = [
        'http://proxy3.example.com:8080',
        'http://user:pass@proxy4.example.com:3128',
    ]
    BaseScraper.configure_proxies(additional_proxies)


def example_check_status():
    """Example: Check rotation status"""
    status = BaseScraper.get_rotation_status()
    
    print("Rotation Status:")
    print(f"  User Agents: {status['user_agents_count']}")
    print(f"  Total Proxies: {status['total_proxies']}")
    print(f"  Available Proxies: {status['available_proxies']}")
    print(f"  Proxies Enabled: {status['proxies_enabled']}")


# ============================================================
# PROXY SERVICES SETUP EXAMPLES
# ============================================================

# Example 1: BrightData (Luminati)
BRIGHTDATA_PROXIES = [
    'http://username-session-random123:password@zproxy.lum-superproxy.io:22225',
]

# Example 2: Oxylabs
OXYLABS_PROXIES = [
    'http://customer-username:password@pr.oxylabs.io:7777',
]

# Example 3: ScraperAPI (HTTP proxy mode)
SCRAPERAPI_PROXIES = [
    'http://scraperapi:YOUR_API_KEY@proxy-server.scraperapi.com:8001',
]

# Example 4: Rotating residential proxies
ROTATING_PROXIES = [
    'http://username:password@rotating-proxy.provider.com:12345',
]

# ============================================================
# FREE PROXY WARNING
# ============================================================

# WARNING: Free public proxies are:
#   - Unreliable (high failure rate)
#   - Slow (poor performance)
#   - Insecure (potential data interception)
#   - Short-lived (frequently go offline)
#
# For production use, invest in paid proxy services.
# Free proxy lists can be found at:
#   - https://free-proxy-list.net/
#   - https://www.sslproxies.org/
#   - https://www.proxy-list.download/
#
# Use free proxies only for testing!

# ============================================================
# BEST PRACTICES
# ============================================================

"""
1. Use Residential Proxies for E-commerce Sites
   - More reliable than datacenter proxies
   - Less likely to be blocked
   - Higher success rate

2. Rotate Proxies Regularly
   - The system automatically rotates on failure
   - Consider rotating even on success for better distribution

3. Monitor Proxy Performance
   - Check rotation status regularly
   - Remove consistently failing proxies
   - Add new proxies as needed

4. Implement Rate Limiting
   - Don't make too many requests too quickly
   - Add delays between requests
   - Respect robots.txt

5. Use Session-Based Proxies for Login
   - Some sites track sessions
   - Sticky sessions maintain state
   - Better for authenticated scraping

6. Test Your Proxies First
   - Verify proxies work before adding to pool
   - Check for geographic restrictions
   - Ensure proxy supports your target sites

7. Handle Proxy Errors Gracefully
   - The system automatically retries with different proxies
   - Failed proxies are temporarily disabled
   - Monitor logs for persistent issues

8. Secure Your Credentials
   - Don't commit proxy credentials to git
   - Use environment variables
   - Encrypt sensitive proxy configurations
"""

# ============================================================
# ENVIRONMENT VARIABLE CONFIGURATION
# ============================================================

import os

def load_proxies_from_env():
    """
    Load proxies from environment variables.
    Recommended for production deployments.
    """
    # Single proxy
    single_proxy = os.getenv('SCRAPER_PROXY')
    if single_proxy:
        return [single_proxy]
    
    # Multiple proxies (comma-separated)
    proxies_str = os.getenv('SCRAPER_PROXIES', '')
    if proxies_str:
        return [p.strip() for p in proxies_str.split(',') if p.strip()]
    
    return []

# Usage in production:
# export SCRAPER_PROXY="http://user:pass@proxy.com:8080"
# or
# export SCRAPER_PROXIES="http://proxy1.com:8080,http://user:pass@proxy2.com:3128"

if __name__ == "__main__":
    # Run examples
    configure_rotation()
    example_check_status()
