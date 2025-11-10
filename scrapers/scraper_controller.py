"""
Central Scraper Controller
Orchestrates scraping across multiple sites with retry and timeout logic.
"""

import concurrent.futures
import time
from typing import Dict, List, Optional

from scrapers.base_scraper import BaseScraper
from scrapers.scraper_registry import ScraperRegistry


class ScraperController:
    """
    Central controller that manages scraping operations across registered scrapers.
    Includes retry logic, timeout handling, and result aggregation.
    """

    def __init__(self, registry: Optional[ScraperRegistry] = None):
        """
        Initialize the controller.

        Args:
            registry (Optional[ScraperRegistry]): Scraper registry to use.
                                                   Creates new one if not provided.
        """
        self.registry = registry if registry else ScraperRegistry()
        self.default_timeout = 10  # seconds
        self.max_retries = 3
        self.retry_delay = 1  # seconds between retries
        self.max_workers = 5  # concurrent scraper threads

    def set_timeout(self, timeout: int):
        """
        Set the default timeout for scraper calls.

        Args:
            timeout (int): Timeout in seconds
        """
        self.default_timeout = timeout

    def set_max_retries(self, retries: int):
        """
        Set the maximum number of retry attempts.

        Args:
            retries (int): Number of retries
        """
        self.max_retries = retries

    def set_retry_delay(self, delay: float):
        """
        Set the delay between retry attempts.

        Args:
            delay (float): Delay in seconds
        """
        self.retry_delay = delay

    def set_max_workers(self, workers: int):
        """
        Set the maximum number of concurrent scraper workers.

        Args:
            workers (int): Number of concurrent workers
        """
        self.max_workers = workers

    def _scrape_with_retry(self, scraper: BaseScraper, input_data: str) -> Dict:
        """
        Execute scraper with retry logic.

        Args:
            scraper (BaseScraper): Scraper to execute
            input_data (str): Product name or URL

        Returns:
            Dict: Scraping result or error result
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Call the scraper's scrape method
                result = scraper.scrape(input_data)

                # Validate the output
                if scraper.validate_output(result):
                    return result
                else:
                    last_error = "Invalid output format"

            except Exception as e:
                last_error = str(e)

                # Wait before retrying (except on last attempt)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        # All retries failed, return error result
        error_msg = f"Failed after {self.max_retries} attempts: {last_error}"
        return scraper.create_error_result(error_msg)

    def _scrape_with_timeout(self, scraper: BaseScraper, input_data: str,
                             timeout: Optional[int] = None) -> Dict:
        """
        Execute scraper with timeout.

        Args:
            scraper (BaseScraper): Scraper to execute
            input_data (str): Product name or URL
            timeout (Optional[int]): Timeout in seconds (uses default if None)

        Returns:
            Dict: Scraping result or error result
        """
        timeout = timeout if timeout is not None else self.default_timeout

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._scrape_with_retry, scraper, input_data)

            try:
                result = future.result(timeout=timeout)
                return result
            except concurrent.futures.TimeoutError:
                # Timeout occurred
                return scraper.create_error_result(f"Timeout after {timeout} seconds")
            except Exception as e:
                return scraper.create_error_result(f"Unexpected error: {str(e)}")

    def scrape_all(self, input_data: str,
                   specific_sites: Optional[List[str]] = None) -> List[Dict]:
        """
        Scrape product information from all registered scrapers (or specific sites).

        Args:
            input_data (str): Product name or URL to search/scrape
            specific_sites (Optional[List[str]]): List of specific site names to scrape.
                                                   If None, scrapes all registered sites.

        Returns:
            List[Dict]: Aggregated results from all scrapers
        """
        # Get scrapers to use
        if specific_sites:
            scrapers = []
            for site_name in specific_sites:
                scraper = self.registry.get_scraper(site_name)
                if scraper:
                    scrapers.append(scraper)
        else:
            scrapers = self.registry.get_all_scrapers()

        if not scrapers:
            return []

        results = []

        # Execute scrapers concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraper tasks
            future_to_scraper = {
                executor.submit(self._scrape_with_timeout, scraper, input_data): scraper
                for scraper in scrapers
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_scraper):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    scraper = future_to_scraper[future]
                    results.append(scraper.create_error_result(f"Controller error: {str(e)}"))

        return results

    def scrape_single(self, site_name: str, input_data: str) -> Optional[Dict]:
        """
        Scrape from a single specific site.

        Args:
            site_name (str): Name of the site to scrape
            input_data (str): Product name or URL

        Returns:
            Optional[Dict]: Scraping result or None if scraper not found
        """
        scraper = self.registry.get_scraper(site_name)

        if not scraper:
            return None

        return self._scrape_with_timeout(scraper, input_data)

    def get_status(self) -> Dict:
        """
        Get controller status information.

        Returns:
            Dict: Status information including registered scrapers and settings
        """
        return {
            'registered_scrapers': self.registry.count(),
            'scraper_sites': self.registry.get_registered_sites(),
            'default_timeout': self.default_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'max_workers': self.max_workers
        }

    def validate_all_scrapers(self) -> Dict[str, bool]:
        """
        Validate that all registered scrapers are properly configured.

        Returns:
            Dict[str, bool]: Dictionary mapping site names to validation status
        """
        validation_results = {}

        for scraper in self.registry.get_all_scrapers():
            site_name = scraper.get_site_name()
            try:
                # Check if scraper has required methods and attributes
                has_scrape = hasattr(scraper, 'scrape') and callable(scraper.scrape)
                has_headers = hasattr(scraper, 'headers') and isinstance(scraper.headers, dict)
                has_timeout = hasattr(scraper, 'timeout')

                validation_results[site_name] = has_scrape and has_headers and has_timeout
            except Exception:
                validation_results[site_name] = False

        return validation_results
