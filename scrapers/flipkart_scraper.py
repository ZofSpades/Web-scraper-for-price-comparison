"""
Flipkart Scraper
Scrapes product data from Flipkart.com
"""

from scrapers.hybrid_scraper import HybridScraper
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict
import urllib.parse


class FlipkartScraper(HybridScraper):
    """
    Scraper for Flipkart (flipkart.com)
    """
    
    def __init__(self):
        super().__init__()
        self.site_name = "Flipkart"
        self.base_url = "https://www.flipkart.com"
        self.search_url = "https://www.flipkart.com/search?q={}"
    
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape Flipkart for product
        """
        if input_data.startswith('http'):
            return super().scrape(input_data)
        else:
            return self._search_and_scrape(input_data)
    
    def _search_and_scrape(self, query: str) -> Dict:
        """Search and scrape first result"""
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = self.search_url.format(encoded_query)
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_link = self._extract_first_product_link(soup)
            
            if not product_link:
                return self.create_error_result("No products found")
            
            return super().scrape(product_link)
            
        except Exception as e:
            return self.create_error_result(f"Search failed: {str(e)}")
    
    def _extract_first_product_link(self, soup: BeautifulSoup) -> str:
        """Extract first product link from search"""
        # Flipkart product link patterns
        link_tags = soup.find_all('a', {'class': '_1fQZEK'})
        if not link_tags:
            link_tags = soup.find_all('a', href=re.compile(r'/p/'))
        
        for link in link_tags[:3]:
            href = link.get('href')
            if href:
                if href.startswith('/'):
                    return self.base_url + href
                return href
        
        return None
    
    def _scrape_static(self, input_data: str) -> Dict:
        """Scrape using static requests"""
        try:
            response = requests.get(input_data, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            raise Exception(f"Static scraping failed: {str(e)}")
    
    def _scrape_with_selenium(self, input_data: str) -> Dict:
        """Scrape using Selenium"""
        from scrapers.selenium_config import SeleniumConfig
        
        driver = None
        try:
            config = SeleniumConfig()
            driver = config.create_driver()
            driver.get(input_data)
            
            import time
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
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
            
        finally:
            if driver:
                driver.quit()
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        selectors = [
            {'class_': 'B_NuCI'},
            {'class_': '_35KyD6'},
        ]
        
        for selector in selectors:
            element = soup.find('span', selector)
            if element:
                return element.get_text().strip()
        
        return "Title not found"
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract price"""
        price_patterns = [
            {'class_': '_30jeq3'},
            {'class_': '_30jeq3 _16Jk6d'},
        ]
        
        for pattern in price_patterns:
            element = soup.find('div', pattern)
            if element:
                price_text = element.get_text().strip()
                match = re.search(r'₹[\d,]+', price_text)
                if match:
                    return match.group()
        
        return "Price not available"
    
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """Extract rating"""
        rating_div = soup.find('div', {'class': '_3LWZlK'})
        if rating_div:
            match = re.search(r'(\d+\.?\d*)', rating_div.get_text())
            if match:
                return match.group(1)
        
        return "N/A"
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract availability"""
        # Check for out of stock
        oos = soup.find(text=re.compile(r'out of stock', re.IGNORECASE))
        if oos:
            return "Out of Stock"
        
        # Check for in stock indicators
        buy_button = soup.find('button', {'class': '_2KpZ6l _2U9uOA _3v1-ww'})
        if buy_button:
            return "In Stock"
        
        return "Unknown"
