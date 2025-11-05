"""
Amazon India Scraper
Scrapes product data from Amazon.in
"""

from scrapers.hybrid_scraper import HybridScraper
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict
import urllib.parse


class AmazonScraper(HybridScraper):
    """
    Scraper for Amazon India (amazon.in)
    """
    
    def __init__(self):
        super().__init__()
        self.site_name = "Amazon"
        self.base_url = "https://www.amazon.in"
        self.search_url = "https://www.amazon.in/s?k={}"
    
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape Amazon for product - handles both search query and direct URL
        """
        # Check if input is URL or search query
        if input_data.startswith('http'):
            # Direct product URL
            return super().scrape(input_data)
        else:
            # Search query - get first result
            return self._search_and_scrape(input_data)
    
    def _search_and_scrape(self, query: str) -> Dict:
        """
        Search for product and scrape first result
        """
        try:
            # Encode search query
            encoded_query = urllib.parse.quote(query)
            search_url = self.search_url.format(encoded_query)
            
            # Get search results
            response = requests.get(search_url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first product link
            product_link = self._extract_first_product_link(soup)
            
            if not product_link:
                return self.create_error_result("No products found for this search")
            
            # Now scrape the product page
            return super().scrape(product_link)
            
        except Exception as e:
            return self.create_error_result(f"Search failed: {str(e)}")
    
    def _extract_first_product_link(self, soup: BeautifulSoup) -> str:
        """Extract first valid product link from search results"""
        # Amazon search result selectors
        product_divs = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for div in product_divs[:3]:  # Check first 3 results
            link_tag = div.find('a', {'class': 'a-link-normal s-no-outline'})
            if link_tag and link_tag.get('href'):
                href = link_tag['href']
                if href.startswith('/'):
                    return self.base_url + href
                return href
        
        return None
    
    def _scrape_static(self, input_data: str) -> Dict:
        """
        Scrape using static requests
        """
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
        """
        Scrape using Selenium (fallback)
        """
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
        """Extract product title"""
        selectors = [
            {'id': 'productTitle'},
            {'id': 'title'},
        ]
        
        for selector in selectors:
            element = soup.find(**selector)
            if element:
                return element.get_text().strip()
        
        return "Title not found"
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract product price"""
        # Try multiple price selectors
        price_patterns = [
            {'class_': 'a-price-whole'},
            {'class_': 'a-price'},
            {'class_': 'apexPriceToPay'},
        ]
        
        for pattern in price_patterns:
            elements = soup.find_all('span', pattern)
            for element in elements:
                text = element.get_text().strip()
                # Look for price with ₹ symbol or digits
                match = re.search(r'₹?\s*[\d,]+\.?\d*', text)
                if match:
                    price = match.group().replace(',', '')
                    if '₹' not in price:
                        price = '₹' + price
                    return price
        
        return "Price not available"
    
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """Extract product rating"""
        # Try rating selectors
        rating_span = soup.find('span', {'class': 'a-icon-alt'})
        if rating_span:
            text = rating_span.get_text()
            match = re.search(r'(\d+\.?\d*)\s*out of', text)
            if match:
                return match.group(1)
        
        # Alternative selector
        rating_span = soup.find('i', {'class': 'a-icon-star'})
        if rating_span:
            text = rating_span.get_text()
            match = re.search(r'(\d+\.?\d*)', text)
            if match:
                return match.group(1)
        
        return "N/A"
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract availability status"""
        availability_div = soup.find('div', {'id': 'availability'})
        if availability_div:
            text = availability_div.get_text().strip().lower()
            if 'in stock' in text:
                return "In Stock"
            elif 'out of stock' in text:
                return "Out of Stock"
            elif 'currently unavailable' in text:
                return "Currently Unavailable"
            return text[:50]
        
        return "Unknown"
