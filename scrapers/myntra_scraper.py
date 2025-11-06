"""
Myntra Scraper
Scrapes product data from Myntra.com
"""

from scrapers.hybrid_scraper import HybridScraper
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict
import urllib.parse


class MyntraScraper(HybridScraper):
    """
    Scraper for Myntra (myntra.com)
    """
    
    def __init__(self):
        super().__init__()
        self.site_name = "Myntra"
        self.base_url = "https://www.myntra.com"
        self.search_url = "https://www.myntra.com/{}"
    
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape Myntra for product - handles both search query and direct URL
        """
        # Check if input is URL or search query
        if input_data.startswith('http'):
            if 'myntra.com' in input_data.lower():
                return super().scrape(input_data)
            else:
                return self._search_and_scrape(input_data)
        else:
            return self._search_and_scrape(input_data)
    
    def _search_and_scrape(self, query: str) -> Dict:
        """
        Search for product and scrape first result
        Note: Myntra uses dynamic JavaScript, so we'll use Selenium
        """
        try:
            # Myntra search format
            encoded_query = urllib.parse.quote(query.replace(' ', '-'))
            search_url = f"https://www.myntra.com/{encoded_query}"
            
            # Use dynamic scraping since Myntra is JS-heavy
            return self._scrape_with_selenium(search_url)
            
        except Exception as e:
            return self.create_error_result(f"Search failed: {str(e)}")
    
    def _scrape_static(self, input_data: str) -> Dict:
        """
        Scrape using static requests (limited for Myntra)
        """
        try:
            response = requests.get(input_data, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"[MYNTRA DEBUG] Scraping: {input_data}")
            
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            rating = self._extract_rating(soup)
            availability = self._extract_availability(soup)
            
            return {
                'site': self.site_name,
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'link': input_data
            }
            
        except Exception as e:
            return self.create_error_result(f"Static scraping failed: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title"""
        try:
            # Try product title
            title_tag = soup.find('h1', {'class': 'pdp-title'})
            if title_tag:
                return title_tag.get_text(strip=True)
            
            # Try alternative
            title_tag = soup.find('h1', {'class': 'pdp-name'})
            if title_tag:
                return title_tag.get_text(strip=True)
            
            return "Title not available"
        except Exception:
            return "Title not available"
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract product price"""
        try:
            # Try discounted price
            price_tag = soup.find('span', {'class': 'pdp-price'})
            if price_tag:
                return f"₹{price_tag.get_text(strip=True)}"
            
            # Try alternative
            price_tag = soup.find('strong', {'class': 'pdp-price'})
            if price_tag:
                return f"₹{price_tag.get_text(strip=True)}"
            
            return "Price not available"
        except Exception:
            return "Price not available"
    
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """Extract product rating"""
        try:
            rating_tag = soup.find('div', {'class': 'index-overallRating'})
            if rating_tag:
                rating_text = rating_tag.get_text(strip=True)
                match = re.search(r'([\d.]+)', rating_text)
                if match:
                    return match.group(1)
            
            return "N/A"
        except Exception:
            return "N/A"
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract availability status"""
        try:
            # Check for out of stock
            oos_tag = soup.find('p', {'class': 'size-buttons-unavailable-product-message'})
            if oos_tag:
                return "Out of Stock"
            
            # Check for in stock
            available_tag = soup.find('div', {'class': 'pdp-add-to-bag'})
            if available_tag:
                return "In Stock"
            
            return "In Stock"
        except Exception:
            return "In Stock"
    
    def _scrape_with_selenium(self, input_data: str) -> Dict:
        """
        Scrape using Selenium for dynamic content
        """
        try:
            from scrapers.selenium_config import SeleniumConfig
            
            config = SeleniumConfig(headless=True)
            driver = config.create_driver()
            driver.get(input_data)
            
            # Wait for content to load
            import time
            time.sleep(4)
            
            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            rating = self._extract_rating(soup)
            availability = self._extract_availability(soup)
            
            return {
                'site': self.site_name,
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'link': input_data
            }
            
        except Exception as e:
            return self.create_error_result(f"Dynamic scraping failed: {str(e)}")
