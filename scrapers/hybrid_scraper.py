"""
Hybrid Scraper Base Class
Extends BaseScraper to support both static and Selenium-based scraping.
"""

from base_scraper import BaseScraper
from selenium_config import SeleniumConfig
from typing import Dict, Optional
import requests
from abc import abstractmethod


class HybridScraper(BaseScraper):
    """
    Hybrid scraper that can fallback to Selenium for JS-rendered content.
    Tries static scraping first, falls back to Selenium if needed.
    """
    
    def __init__(self, use_selenium=False):
        """
        Initialize hybrid scraper.
        
        Args:
            use_selenium (bool): If True, always use Selenium. If False, use static first.
        """
        super().__init__()
        self.use_selenium = use_selenium
        self.selenium_config = SeleniumConfig(headless=True)
        self.static_failed = False
    
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape with fallback logic: static -> Selenium.
        
        Args:
            input_data (str): Product name or URL
            
        Returns:
            Dict: Product information
        """
        # If configured to always use Selenium
        if self.use_selenium:
            return self._scrape_with_selenium(input_data)
        
        # Try static scraping first
        try:
            result = self._scrape_static(input_data)
            
            # Check if result indicates JS-rendered content
            if self._is_dynamic_content_detected(result):
                self.static_failed = True
                return self._scrape_with_selenium(input_data)
            
            return result
            
        except Exception as e:
            # Static scraping failed, fallback to Selenium
            self.static_failed = True
            try:
                return self._scrape_with_selenium(input_data)
            except Exception as selenium_error:
                # Both methods failed
                return self.create_error_result(
                    f"Static error: {str(e)}, Selenium error: {str(selenium_error)}"
                )
    
    @abstractmethod
    def _scrape_static(self, input_data: str) -> Dict:
        """
        Perform static scraping using requests/BeautifulSoup.
        Must be implemented by subclasses.
        
        Args:
            input_data (str): Product name or URL
            
        Returns:
            Dict: Product information
        """
        pass
    
    @abstractmethod
    def _scrape_with_selenium(self, input_data: str) -> Dict:
        """
        Perform scraping using Selenium for JS-rendered content.
        Must be implemented by subclasses.
        
        Args:
            input_data (str): Product name or URL
            
        Returns:
            Dict: Product information
        """
        pass
    
    def _is_dynamic_content_detected(self, result: Dict) -> bool:
        """
        Detect if the page likely has JS-rendered content.
        Override this method for custom detection logic.
        
        Args:
            result (Dict): Result from static scraping
            
        Returns:
            bool: True if dynamic content detected
        """
        # Check for common indicators of JS-rendered content
        if 'error' in result:
            return True
        
        # Check if critical fields are missing or have placeholder values
        if result.get('title') == 'N/A' or result.get('price') == 'N/A':
            return True
        
        # Check for common JS loading indicators in title
        title = result.get('title', '').lower()
        if 'loading' in title or 'please wait' in title:
            return True
        
        return False
    
    def set_selenium_mode(self, enabled: bool):
        """
        Enable or disable Selenium mode.
        
        Args:
            enabled (bool): True to always use Selenium, False for fallback mode
        """
        self.use_selenium = enabled
    
    def set_headless(self, headless: bool):
        """
        Set headless mode for Selenium.
        
        Args:
            headless (bool): True for headless mode
        """
        self.selenium_config.headless = headless
    
    def get_scraping_method(self) -> str:
        """
        Get the last scraping method used.
        
        Returns:
            str: 'selenium' if Selenium was used, 'static' otherwise
        """
        return 'selenium' if self.static_failed else 'static'
