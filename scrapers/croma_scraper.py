"""
Croma Scraper
Scrapes product data from Croma.com (Electronics)
"""

from scrapers.hybrid_scraper import HybridScraper
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict
import urllib.parse


class CromaScraper(HybridScraper):
    """
    Scraper for Croma Electronics (croma.com)
    """
    
    def __init__(self):
        super().__init__()
        self.site_name = "Croma"
        self.base_url = "https://www.croma.com"
        self.search_url = "https://www.croma.com/search/?text={}"
    
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape Croma for product - handles both search query and direct URL
        """
        # Check if input is URL or search query
        if input_data.startswith('http'):
            if 'croma.com' in input_data.lower():
                return super().scrape(input_data)
            else:
                return self._search_and_scrape(input_data)
        else:
            return self._search_and_scrape(input_data)
    
    def _search_and_scrape(self, query: str) -> Dict:
        """
        Search for product and scrape first result
        """
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = self.search_url.format(encoded_query)
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_link = self._extract_first_product_link(soup)
            
            if not product_link:
                return self.create_error_result("No products found for this search")
            
            return super().scrape(product_link)
            
        except Exception as e:
            return self.create_error_result(f"Search failed: {str(e)}")
    
    def _extract_first_product_link(self, soup: BeautifulSoup) -> str:
        """Extract first valid product link from search results"""
        # Croma product links
        product_links = soup.find_all('a', {'class': 'product-title'})
        
        for link in product_links[:3]:
            href = link.get('href')
            if href and '/p/' in href:
                if href.startswith('http'):
                    return href
                return self.base_url + href
        
        # Alternative selector
        product_items = soup.find_all('div', {'class': 'product-item'})
        for item in product_items[:3]:
            link = item.find('a')
            if link:
                href = link.get('href')
                if href:
                    if href.startswith('http'):
                        return href
                    return self.base_url + href
        
        return None
    
    def _scrape_static(self, input_data: str) -> Dict:
        """
        Scrape using static requests
        """
        try:
            response = requests.get(input_data, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"[CROMA DEBUG] Scraping: {input_data}")
            
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
            # Try h1 title
            title_tag = soup.find('h1', {'class': 'pd-title'})
            if title_tag:
                return title_tag.get_text(strip=True)
            
            # Try alternative
            title_tag = soup.find('h1', {'itemprop': 'name'})
            if title_tag:
                return title_tag.get_text(strip=True)
            
            return "Title not available"
        except:
            return "Title not available"
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract product price"""
        try:
            # Try sale price
            price_tag = soup.find('span', {'class': 'amount'})
            if price_tag:
                return price_tag.get_text(strip=True)
            
            # Try alternative
            price_tag = soup.find('span', {'class': 'new-price'})
            if price_tag:
                return price_tag.get_text(strip=True)
            
            # Try itemprop price
            price_tag = soup.find('span', {'itemprop': 'price'})
            if price_tag:
                return f"₹{price_tag.get_text(strip=True)}"
            
            return "Price not available"
        except:
            return "Price not available"
    
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """Extract product rating"""
        try:
            rating_tag = soup.find('span', {'itemprop': 'ratingValue'})
            if rating_tag:
                return rating_tag.get_text(strip=True)
            
            # Alternative selector
            rating_tag = soup.find('div', {'class': 'rating-value'})
            if rating_tag:
                return rating_tag.get_text(strip=True)
            
            return "N/A"
        except:
            return "N/A"
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract availability status"""
        try:
            # Check for out of stock
            oos_tag = soup.find('div', {'class': 'out-of-stock'})
            if oos_tag:
                return "Out of Stock"
            
            # Check availability
            avail_tag = soup.find('link', {'itemprop': 'availability'})
            if avail_tag:
                href = avail_tag.get('href', '')
                if 'InStock' in href:
                    return "In Stock"
                elif 'OutOfStock' in href:
                    return "Out of Stock"
            
            # Check add to cart button
            cart_btn = soup.find('button', {'class': 'add-to-cart'})
            if cart_btn:
                return "In Stock"
            
            return "In Stock"
        except:
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
            time.sleep(3)
            
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
