"""
Real-time scraping integration
Coordinates scraping across multiple e-commerce sites
"""

from scrapers.scraper_registry import ScraperRegistry
from scrapers.scraper_controller import ScraperController
from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from typing import List, Dict
import concurrent.futures


class ScraperManager:
    """
    Manages real-time scraping from multiple e-commerce sites
    """
    
    def __init__(self):
        """Initialize scraper registry and register all scrapers"""
        self.registry = ScraperRegistry()
        self.controller = ScraperController(self.registry)
        
        # Register scrapers
        self.registry.register(AmazonScraper())
        self.registry.register(FlipkartScraper())
    
    def search_product(self, query: str, sites: List[str] = None) -> List[Dict]:
        """
        Search for product across multiple sites
        
        Args:
            query: Product name or search query
            sites: List of site names to search (None = all sites)
            
        Returns:
            List of product results from all sites
        """
        if sites is None or 'all' in sites:
            # Search all registered sites
            results = self.controller.scrape_all(query)
        else:
            # Search specific sites
            results = []
            for site in sites:
                scraper = self.registry.get_scraper(site.lower())
                if scraper:
                    try:
                        result = scraper.scrape(query)
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'site': site,
                            'title': 'Error',
                            'price': 'N/A',
                            'rating': 'N/A',
                            'availability': 'Error',
                            'link': '#',
                            'error': str(e)
                        })
        
        return self._format_results(results)
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """
        Format results to match frontend expectations
        """
        formatted = []
        
        for result in results:
            # Skip if error occurred
            if 'error' in result and result['title'] == 'Error':
                continue
            
            # Extract price value for sorting
            price_value = self._extract_price_value(result.get('price', '0'))
            
            formatted.append({
                'product_name': result.get('title', 'N/A'),
                'price': price_value,
                'price_display': result.get('price', 'N/A'),
                'rating': result.get('rating', 'N/A'),
                'reviews_count': 0,  # Not available from basic scraping
                'availability': result.get('availability', 'Unknown'),
                'seller': result.get('site', 'Unknown'),
                'url': result.get('link', '#'),
                'scraped_at': self._get_timestamp()
            })
        
        # Sort by price (lowest first)
        formatted.sort(key=lambda x: x['price'] if x['price'] > 0 else float('inf'))
        
        return formatted
    
    def _extract_price_value(self, price_str: str) -> float:
        """Extract numeric price value from string"""
        import re
        
        if not price_str or price_str == 'N/A' or price_str == 'Price not available':
            return 0.0
        
        # Remove currency symbols and commas
        clean_price = re.sub(r'[₹$,]', '', price_str)
        
        # Extract first number
        match = re.search(r'(\d+\.?\d*)', clean_price)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_available_sites(self) -> List[str]:
        """Get list of available scraper sites"""
        return [name.capitalize() for name in self.registry.list_scrapers()]


# Create global instance
scraper_manager = ScraperManager()
