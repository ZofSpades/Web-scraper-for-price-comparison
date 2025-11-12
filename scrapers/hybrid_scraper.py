"""
Hybrid Scraper Base Class
Extends BaseScraper to support both static and Selenium-based scraping.
Enhanced with intelligent fallback detection and retry mechanisms.
"""

from scrapers.base_scraper import BaseScraper
from scrapers.selenium_config import SeleniumConfig, SeleniumHelper
from typing import Dict, Optional
import requests
from abc import abstractmethod
import logging

logger = logging.getLogger(__name__)


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
        self.retry_attempts = 2  # Number of retry attempts
        self.retry_delay = 1  # Delay between retries in seconds
    
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape with intelligent fallback logic: static -> Selenium.
        Includes retry mechanism for improved reliability.
        
        Args:
            input_data (str): Product name or URL
            
        Returns:
            Dict: Product information
        """
        # If configured to always use Selenium
        if self.use_selenium:
            logger.info(f"Using Selenium (forced mode) for: {input_data}")
            return self._scrape_with_retry(self._scrape_with_selenium, input_data)
        
        # Try static scraping first
        try:
            logger.info(f"Attempting static scraping for: {input_data}")
            result = self._scrape_static(input_data)
            
            # Check if result indicates JS-rendered content or incomplete data
            if self._should_fallback_to_selenium(result):
                logger.warning(f"Dynamic content detected, falling back to Selenium for: {input_data}")
                self.static_failed = True
                return self._scrape_with_retry(self._scrape_with_selenium, input_data)
            
            logger.info(f"Static scraping successful for: {input_data}")
            return result
            
        except Exception as e:
            # Static scraping failed, fallback to Selenium
            logger.warning(f"Static scraping failed: {str(e)}. Trying Selenium...")
            self.static_failed = True
            try:
                return self._scrape_with_retry(self._scrape_with_selenium, input_data)
            except Exception as selenium_error:
                # Both methods failed
                error_msg = f"Static error: {str(e)}, Selenium error: {str(selenium_error)}"
                logger.error(error_msg)
                return self.create_error_result(error_msg)
    
    def _scrape_with_retry(self, scrape_func, input_data: str) -> Dict:
        """
        Execute scraping function with retry logic.
        
        Args:
            scrape_func: Scraping function to execute
            input_data: Input data for scraping
            
        Returns:
            Dict: Scraping result
        """
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                result = scrape_func(input_data)
                
                # Validate result
                if result and not result.get('error'):
                    return result
                
                logger.warning(f"Attempt {attempt + 1} returned invalid result")
                last_error = result.get('error', 'Invalid result')
                
                if attempt < self.retry_attempts - 1:
                    import time
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                
                if attempt < self.retry_attempts - 1:
                    import time
                    time.sleep(self.retry_delay)
        
        # All retries failed
        return self.create_error_result(f"All retry attempts failed. Last error: {last_error}")
    
    def _should_fallback_to_selenium(self, result: Dict) -> bool:
        """
        Enhanced detection logic to determine if Selenium fallback is needed.
        Checks multiple indicators of dynamic content or failed scraping.
        
        Args:
            result (Dict): Result from static scraping
            
        Returns:
            bool: True if Selenium fallback should be used
        """
        # Check for errors
        if 'error' in result:
            return True
        
        # Check if critical fields are missing or have placeholder values
        title = result.get('title', '')
        price = result.get('price', '')
        
        if not title or title in ['N/A', 'Title not found', 'Title not available', 'Error']:
            logger.debug("Title missing or invalid - triggering Selenium fallback")
            return True
        
        if not price or price in ['N/A', 'Price not available', 'Price not found', 'Error']:
            logger.debug("Price missing or invalid - triggering Selenium fallback")
            return True
        
        # Check for suspiciously short content (likely JS placeholder)
        if len(title) < 5:
            logger.debug("Title too short - triggering Selenium fallback")
            return True
        
        # Check for common JS loading indicators
        indicators = ['loading', 'please wait', 'redirecting', 'enable javascript']
        title_lower = title.lower()
        
        if any(indicator in title_lower for indicator in indicators):
            logger.debug(f"JS loading indicator detected in title - triggering Selenium fallback")
            return True
        
        # Check for bot detection messages
        bot_indicators = ['access denied', 'blocked', 'captcha', 'verify', 'robot']
        if any(indicator in title_lower for indicator in bot_indicators):
            logger.debug(f"Bot detection indicator found - triggering Selenium fallback")
            return True
        
        return False
    
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
    
    def set_selenium_mode(self, enabled: bool):
        """
        Enable or disable Selenium mode.
        
        Args:
            enabled (bool): True to always use Selenium, False for fallback mode
        """
        self.use_selenium = enabled
        logger.info(f"Selenium mode set to: {'always' if enabled else 'fallback'}")
    
    def set_headless(self, headless: bool):
        """
        Set headless mode for Selenium.
        
        Args:
            headless (bool): True for headless mode
        """
        self.selenium_config.headless = headless
        logger.info(f"Selenium headless mode set to: {headless}")
    
    def set_retry_attempts(self, attempts: int):
        """
        Set number of retry attempts.
        
        Args:
            attempts (int): Number of retry attempts
        """
        self.retry_attempts = max(1, attempts)
        logger.info(f"Retry attempts set to: {self.retry_attempts}")
    
    def get_scraping_method(self) -> str:
        """
        Get the last scraping method used.
        
        Returns:
            str: 'selenium' if Selenium was used, 'static' otherwise
        """
        return 'selenium' if self.static_failed else 'static'
    
    def get_scraping_stats(self) -> Dict:
        """
        Get statistics about the scraping session.
        
        Returns:
            Dict: Scraping statistics
        """
        return {
            'method_used': self.get_scraping_method(),
            'selenium_mode': 'always' if self.use_selenium else 'fallback',
            'retry_attempts': self.retry_attempts,
            'headless': self.selenium_config.headless
        }
