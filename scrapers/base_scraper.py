"""
Base Scraper Interface
Defines the abstract interface that all site-specific scrapers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from scrapers.rotation_manager import RotationManager


class BaseScraper(ABC):
    """
    Abstract base class for all site-specific scrapers.
    Each scraper must implement the scrape method.
    """

    # Class-level rotation manager shared across all scrapers
    _rotation_manager = None

    def __init__(self):
        """Initialize the scraper with basic configuration."""
        self.site_name = self.__class__.__name__.replace('Scraper', '')
        self.timeout = 10  # Default timeout in seconds
        
        # Initialize rotation manager if not already done
        if BaseScraper._rotation_manager is None:
            BaseScraper._rotation_manager = RotationManager()
        
        # Base headers (User-Agent will be rotated)
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Current proxy being used (for tracking)
        self.current_proxy = None

    @abstractmethod
    def scrape(self, input_data: str) -> Dict:
        """
        Scrape product information from the site.

        Args:
            input_data (str): Product name or URL to scrape

        Returns:
            Dict: JSON object with the following keys:
                - site (str): Name of the website
                - title (str): Product title
                - price (str): Product price
                - rating (str): Product rating
                - availability (str): Stock availability
                - link (str): Product URL

        Raises:
            Exception: If scraping fails
        """
        pass

    def get_site_name(self) -> str:
        """
        Get the name of the site this scraper handles.

        Returns:
            str: Site name
        """
        return self.site_name

    def set_timeout(self, timeout: int):
        """
        Set the timeout for HTTP requests.

        Args:
            timeout (int): Timeout in seconds
        """
        self.timeout = timeout

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with rotated User-Agent.

        Returns:
            Dict: HTTP headers with rotated User-Agent
        """
        return BaseScraper._rotation_manager.get_headers_with_rotation(self.base_headers)

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get the next available proxy from rotation.
        
        Returns:
            Optional[Dict[str, str]]: Proxy dict or None if no proxies configured
        """
        return BaseScraper._rotation_manager.proxy_rotator.get_next()

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get a random proxy from the pool.
        
        Returns:
            Optional[Dict[str, str]]: Proxy dict or None if no proxies configured
        """
        return BaseScraper._rotation_manager.proxy_rotator.get_random()

    def mark_proxy_failure(self, proxy_dict: Optional[Dict[str, str]] = None):
        """
        Mark a proxy as failed. If no proxy specified, uses current_proxy.
        
        Args:
            proxy_dict (Optional[Dict[str, str]]): Proxy to mark as failed
        """
        proxy = proxy_dict if proxy_dict is not None else self.current_proxy
        BaseScraper._rotation_manager.mark_proxy_failure(proxy)

    def mark_proxy_success(self, proxy_dict: Optional[Dict[str, str]] = None):
        """
        Mark a proxy as successful. If no proxy specified, uses current_proxy.
        
        Args:
            proxy_dict (Optional[Dict[str, str]]): Proxy to mark as successful
        """
        proxy = proxy_dict if proxy_dict is not None else self.current_proxy
        BaseScraper._rotation_manager.mark_proxy_success(proxy)

    @classmethod
    def configure_proxies(cls, proxy_list: list):
        """
        Configure proxy rotation for all scrapers.
        
        Args:
            proxy_list (list): List of proxy URLs
        """
        if cls._rotation_manager is None:
            cls._rotation_manager = RotationManager(proxy_list)
        else:
            cls._rotation_manager.add_proxies(proxy_list)

    @classmethod
    def get_rotation_status(cls) -> Dict:
        """
        Get status of rotation manager.
        
        Returns:
            Dict: Rotation manager status
        """
        if cls._rotation_manager is None:
            cls._rotation_manager = RotationManager()
        return cls._rotation_manager.get_status()

    def set_custom_header(self, key: str, value: str):
        """
        Add or update a custom header.

        Args:
            key (str): Header key
            value (str): Header value
        """
        self.base_headers[key] = value

    def create_error_result(self, error_message: str) -> Dict:
        """
        Create standardized error result.
        
        Args:
            error_message (str): Error message
            
        Returns:
            Dict: Error result dict
        """
        return {
            'site': self.site_name,
            'title': 'N/A',
            'price': 'N/A',
            'rating': 'N/A',
            'availability': 'N/A',
            'link': 'N/A',
            'error': error_message
        }

    def validate_output(self, result: Dict) -> bool:
        """
        Validate that the scraper output has all required fields.

        Args:
            result (Dict): Scraper output to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['site', 'title', 'price', 'rating', 'availability', 'link']
        return all(field in result for field in required_fields)

    def create_error_result(self, error_message: str) -> Dict:
        """
        Create a standardized error result.

        Args:
            error_message (str): Error description

        Returns:
            Dict: Error result in standard format
        """
        return {
            'site': self.site_name,
            'title': 'Error',
            'price': 'N/A',
            'rating': 'N/A',
            'availability': 'Error',
            'link': '#',
            'error': error_message
        }
