"""
Main entry point for Web Scraper Price Comparison Tool
"""

import os
from web.app import app as web_app


def main():
    """Start the web application"""
    print("=" * 60)
    print("Web Scraper for Price Comparison")
    print("=" * 60)
    print("\nStarting web server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("\nPress CTRL+C to stop the server\n")

    # Use environment variable for debug mode (default False for production)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    web_app.run(debug=debug_mode, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
