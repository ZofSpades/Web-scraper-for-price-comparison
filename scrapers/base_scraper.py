"""
Base Scraper Interface
Defines the abstract interface that all site-specific scrapers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseScraper(ABC):
    """
    Abstract base class for all site-specific scrapers.
    Each scraper must implement the scrape method.
    """

    def __init__(self):
        """Initialize the scraper with basic configuration."""
        self.site_name = self.__class__.__name__.replace('Scraper', '')
        self.timeout = 10  # Default timeout in seconds
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

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
        Get the HTTP headers to use for requests.

        Returns:
            Dict: HTTP headers with polite User-Agent
        """
        return self.headers.copy()

    def set_custom_header(self, key: str, value: str):
        """
        Add or update a custom header.

        Args:
            key (str): Header key
            value (str): Header value
        """
        self.headers[key] = value

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
