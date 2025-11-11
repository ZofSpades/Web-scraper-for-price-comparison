"""
Hybrid Scraper Base Class
Extends BaseScraper to support both static and Selenium-based scraping.
Supports proxy and user-agent rotation for both modes.
"""

import requests
from abc import abstractmethod
from typing import Dict

from scrapers.base_scraper import BaseScraper
from scrapers.selenium_config import SeleniumConfig


class HybridScraper(BaseScraper):
    """
    Hybrid scraper that can fallback to Selenium for JS-rendered content.
    Tries static scraping first, falls back to Selenium if needed.
    Supports proxy and user-agent rotation.
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

    def make_request(self, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with rotation support.
        Automatically handles proxy rotation and retry on failure.
        
        Args:
            url (str): URL to request
            **kwargs: Additional arguments for requests.get
            
        Returns:
            requests.Response: Response object
            
        Raises:
            Exception: If all attempts fail
        """
        # Get headers with rotated user-agent
        headers = kwargs.get('headers', self.get_headers())
        kwargs['headers'] = headers
        
        # Get proxy
        proxy = self.get_proxy()
        self.current_proxy = proxy
        
        max_attempts = 3
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                # Make request with or without proxy
                if proxy:
                    kwargs['proxies'] = proxy
                
                response = requests.get(url, **kwargs)
                response.raise_for_status()
                
                # Success - mark proxy as working
                if proxy:
                    self.mark_proxy_success(proxy)
                
                return response
                
            except Exception as e:
                last_error = e
                
                # Mark proxy as failed
                if proxy:
                    self.mark_proxy_failure(proxy)
                
                # Try different proxy on retry
                if attempt < max_attempts - 1:
                    proxy = self.get_proxy()
                    self.current_proxy = proxy
                    # Also rotate user-agent
                    kwargs['headers'] = self.get_headers()
        
        # All attempts failed
        raise last_error

    def create_selenium_driver(self):
        """
        Create Selenium driver with rotation support.
        
        Returns:
            webdriver.Chrome: Configured driver with rotated user-agent and proxy
        """
        # Get rotated user-agent
        headers = self.get_headers()
        user_agent = headers.get('User-Agent')
        
        # Get proxy
        proxy = self.get_proxy()
        self.current_proxy = proxy
        
        try:
            driver = self.selenium_config.create_driver(user_agent=user_agent, proxy=proxy)
            # Mark proxy as successful if driver created
            if proxy:
                self.mark_proxy_success(proxy)
            return driver
        except Exception as e:
            # Mark proxy as failed
            if proxy:
                self.mark_proxy_failure(proxy)
            raise e

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
