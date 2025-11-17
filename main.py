"""
Main entry point for Web Scraper Price Comparison Tool
"""

import os
from web.app import app as web_app
from scrapers.base_scraper import BaseScraper


def configure_rotation():
    """
    Configure proxy and user-agent rotation.
    Loads proxies from environment variables if available.
    """
    # Load proxies from environment variables
    proxies = []
    
    # Single proxy
    single_proxy = os.getenv('SCRAPER_PROXY')
    if single_proxy:
        proxies.append(single_proxy)
    
    # Multiple proxies (comma-separated)
    proxies_str = os.getenv('SCRAPER_PROXIES', '')
    if proxies_str:
        proxy_list = [p.strip() for p in proxies_str.split(',') if p.strip()]
        proxies.extend(proxy_list)
    
    # Configure proxies if any are provided
    if proxies:
        BaseScraper.configure_proxies(proxies)
        print(f"✓ Configured {len(proxies)} proxy/proxies")
    else:
        print("⚠ No proxies configured - using direct connection")
        print("  Set SCRAPER_PROXY or SCRAPER_PROXIES environment variable to use proxies")
    
    # Display rotation status
    status = BaseScraper.get_rotation_status()
    print(f"✓ User-agent rotation: {status['user_agents_count']} agents available")
    if status['proxies_enabled']:
        print(f"✓ Proxy rotation: {status['available_proxies']}/{status['total_proxies']} proxies available")
    
    return status


def main():
    """Start the web application"""
    print("=" * 60)
    print("Web Scraper for Price Comparison")
    print("=" * 60)
    print("\nInitializing rotation system...")
    
    # Configure rotation
    configure_rotation()
    
    print("\nStarting web server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("\nPress CTRL+C to stop the server\n")

    # Use environment variable for debug mode (default False for production)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    web_app.run(debug=debug_mode, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
