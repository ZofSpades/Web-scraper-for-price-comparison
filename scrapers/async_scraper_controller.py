"""
Asynchronous Scraper Controller
Orchestrates concurrent scraping across multiple sites using asyncio for improved performance.
Target: ≤15 seconds for 5 websites
"""

import asyncio
import time
from typing import Dict, List, Optional

from scrapers.base_scraper import BaseScraper
from scrapers.scraper_registry import ScraperRegistry


class AsyncScraperController:
    """
    Asynchronous controller that manages scraping operations concurrently.
    Uses asyncio to scrape multiple sites in parallel for optimal performance.
    """

    def __init__(self, registry: Optional[ScraperRegistry] = None):
        """
        Initialize the async controller.

        Args:
            registry (Optional[ScraperRegistry]): Scraper registry to use.
                                                   Creates new one if not provided.
        """
        self.registry = registry if registry else ScraperRegistry()
        self.default_timeout = 15  # seconds per scraper
        self.max_retries = 2
        self.retry_delay = 0.5  # seconds between retries
        self.total_timeout = 15  # total timeout for all scrapers

    def set_timeout(self, timeout: int):
        """Set the default timeout for individual scraper calls."""
        self.default_timeout = timeout

    def set_total_timeout(self, timeout: int):
        """Set the total timeout for all scraping operations."""
        self.total_timeout = timeout

    def set_max_retries(self, retries: int):
        """Set the maximum number of retry attempts."""
        self.max_retries = retries

    def set_retry_delay(self, delay: float):
        """Set the delay between retry attempts."""
        self.retry_delay = delay

    async def _scrape_with_retry_async(self, scraper: BaseScraper, input_data: str) -> Dict:
        """
        Execute scraper with retry logic asynchronously.

        Args:
            scraper (BaseScraper): Scraper to execute
            input_data (str): Product name or URL

        Returns:
            Dict: Scraping result or error result
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Run the synchronous scrape method in an executor
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, scraper.scrape, input_data)

                # Validate the output
                if scraper.validate_output(result):
                    return result
                else:
                    last_error = "Invalid output format"

            except Exception as e:
                last_error = str(e)

                # Wait before retrying (except on last attempt)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        # All retries failed, return error result
        error_msg = f"Failed after {self.max_retries} attempts: {last_error}"
        return scraper.create_error_result(error_msg)

    async def _scrape_with_timeout_async(self, scraper: BaseScraper, input_data: str,
                                         timeout: Optional[int] = None) -> Dict:
        """
        Execute scraper with timeout asynchronously.

        Args:
            scraper (BaseScraper): Scraper to execute
            input_data (str): Product name or URL
            timeout (Optional[int]): Timeout in seconds (uses default if None)

        Returns:
            Dict: Scraping result or error result
        """
        timeout = timeout if timeout is not None else self.default_timeout

        try:
            result = await asyncio.wait_for(
                self._scrape_with_retry_async(scraper, input_data),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return scraper.create_error_result(f"Timeout after {timeout} seconds")
        except Exception as e:
            return scraper.create_error_result(f"Unexpected error: {str(e)}")

    async def scrape_all_async(self, input_data: str,
                               specific_sites: Optional[List[str]] = None) -> List[Dict]:
        """
        Scrape product information from all registered scrapers concurrently.

        Args:
            input_data (str): Product name or URL to search/scrape
            specific_sites (Optional[List[str]]): List of specific site names to scrape.
                                                   If None, scrapes all registered sites.

        Returns:
            List[Dict]: Aggregated results from all scrapers
        """
        start_time = time.time()

        # Get scrapers to use
        if specific_sites:
            scrapers = []
            for site_name in specific_sites:
                # Normalize site name to capitalize first letter (e.g., "amazon" -> "Amazon")
                # to maintain backward compatibility with case-insensitive lookups
                normalized_name = site_name.lower().capitalize()
                scraper = self.registry.get_scraper(normalized_name)
                if scraper:
                    scrapers.append(scraper)
        else:
            scrapers = self.registry.get_all_scrapers()

        if not scrapers:
            return []

        print(f"[ASYNC CONTROLLER] Starting concurrent scraping for {len(scrapers)} sites...")

        # Create tasks for all scrapers
        tasks = [
            asyncio.create_task(self._scrape_with_timeout_async(scraper, input_data))
            for scraper in scrapers
        ]

        # Execute all tasks concurrently with overall timeout
        # Use asyncio.wait() instead of wait_for() to preserve partial results
        done, pending = await asyncio.wait(tasks, timeout=self.total_timeout)

        elapsed_time = time.time() - start_time

        # Process completed tasks
        processed_results = []
        completed_count = 0

        for task in done:
            try:
                result = task.result()
                if isinstance(result, Exception):
                    # Task raised an exception
                    scraper_index = tasks.index(task)
                    scraper = scrapers[scraper_index]
                    processed_results.append(
                        scraper.create_error_result(f"Exception: {str(result)}")
                    )
                else:
                    processed_results.append(result)
                    completed_count += 1
            except Exception as e:
                # Task exception not caught properly
                scraper_index = tasks.index(task)
                scraper = scrapers[scraper_index]
                processed_results.append(
                    scraper.create_error_result(f"Task exception: {str(e)}")
                )

        # Handle pending (timed out) tasks
        if pending:
            print(f"[ASYNC CONTROLLER] {len(pending)} scrapers timed out, cancelling...")
            for task in pending:
                task.cancel()
                # Find which scraper this task belongs to
                scraper_index = tasks.index(task)
                scraper = scrapers[scraper_index]
                processed_results.append(
                    scraper.create_error_result(f"Timeout after {self.total_timeout}s")
                )

        print(f"[ASYNC CONTROLLER] Completed {completed_count}/{len(scrapers)} scrapers in {elapsed_time:.2f}s")

        return processed_results

    def scrape_all(self, input_data: str,
                   specific_sites: Optional[List[str]] = None) -> List[Dict]:
        """
        Synchronous wrapper for async scraping (for compatibility with existing code).
        Callable from Flask (synchronous context).

        Args:
            input_data (str): Product name or URL to search/scrape
            specific_sites (Optional[List[str]]): List of specific site names to scrape.

        Returns:
            List[Dict]: Aggregated results from all scrapers
        """
        # Flask is synchronous, so no running event loop exists
        # Simply use asyncio.run() to create a new event loop
        return asyncio.run(self.scrape_all_async(input_data, specific_sites))

    async def scrape_single_async(self, site_name: str, input_data: str) -> Optional[Dict]:
        """
        Scrape from a single specific site asynchronously.

        Args:
            site_name (str): Name of the site to scrape (case-insensitive)
            input_data (str): Product name or URL

        Returns:
            Optional[Dict]: Scraping result or None if scraper not found
        """
        # Normalize site name to capitalize first letter (e.g., "amazon" -> "Amazon")
        # to maintain backward compatibility with case-insensitive lookups
        normalized_name = site_name.lower().capitalize()
        scraper = self.registry.get_scraper(normalized_name)

        if not scraper:
            return None

        return await self._scrape_with_timeout_async(scraper, input_data)

    def scrape_single(self, site_name: str, input_data: str) -> Optional[Dict]:
        """
        Synchronous wrapper for single site scraping.
        Callable from Flask (synchronous context).

        Args:
            site_name (str): Name of the site to scrape
            input_data (str): Product name or URL

        Returns:
            Optional[Dict]: Scraping result or None if scraper not found
        """
        # Flask is synchronous, so no running event loop exists
        # Simply use asyncio.run() to create a new event loop
        return asyncio.run(self.scrape_single_async(site_name, input_data))

    def get_status(self) -> Dict:
        """
        Get controller status information.

        Returns:
            Dict: Status information including registered scrapers and settings
        """
        return {
            'controller_type': 'async',
            'registered_scrapers': self.registry.count(),
            'scraper_sites': self.registry.get_registered_sites(),
            'default_timeout': self.default_timeout,
            'total_timeout': self.total_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }
