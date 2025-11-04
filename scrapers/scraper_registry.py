"""
Scraper Registry
Manages dynamic registration and unregistration of scraper implementations.
"""

from typing import Dict, List, Optional
from base_scraper import BaseScraper
import threading


class ScraperRegistry:
    """
    Central registry for managing scraper implementations.
    Allows dynamic registration and unregistration of scrapers.
    """
    
    def __init__(self):
        """Initialize the registry with an empty scraper dictionary."""
        self._scrapers: Dict[str, BaseScraper] = {}
        self._lock = threading.Lock()
    
    def register(self, scraper: BaseScraper) -> bool:
        """
        Register a new scraper implementation.
        
        Args:
            scraper (BaseScraper): Scraper instance to register
            
        Returns:
            bool: True if registration successful, False if already registered
        """
        if not isinstance(scraper, BaseScraper):
            raise TypeError("Scraper must be an instance of BaseScraper")
        
        site_name = scraper.get_site_name()
        
        with self._lock:
            if site_name in self._scrapers:
                return False
            
            self._scrapers[site_name] = scraper
            return True
    
    def unregister(self, site_name: str) -> bool:
        """
        Unregister a scraper by site name.
        
        Args:
            site_name (str): Name of the site to unregister
            
        Returns:
            bool: True if unregistration successful, False if not found
        """
        with self._lock:
            if site_name in self._scrapers:
                del self._scrapers[site_name]
                return True
            return False
    
    def get_scraper(self, site_name: str) -> Optional[BaseScraper]:
        """
        Get a registered scraper by site name.
        
        Args:
            site_name (str): Name of the site
            
        Returns:
            Optional[BaseScraper]: Scraper instance or None if not found
        """
        with self._lock:
            return self._scrapers.get(site_name)
    
    def get_all_scrapers(self) -> List[BaseScraper]:
        """
        Get all registered scrapers.
        
        Returns:
            List[BaseScraper]: List of all registered scraper instances
        """
        with self._lock:
            return list(self._scrapers.values())
    
    def get_registered_sites(self) -> List[str]:
        """
        Get names of all registered sites.
        
        Returns:
            List[str]: List of registered site names
        """
        with self._lock:
            return list(self._scrapers.keys())
    
    def is_registered(self, site_name: str) -> bool:
        """
        Check if a scraper is registered.
        
        Args:
            site_name (str): Name of the site to check
            
        Returns:
            bool: True if registered, False otherwise
        """
        with self._lock:
            return site_name in self._scrapers
    
    def count(self) -> int:
        """
        Get the number of registered scrapers.
        
        Returns:
            int: Number of registered scrapers
        """
        with self._lock:
            return len(self._scrapers)
    
    def clear(self):
        """
        Clear all registered scrapers.
        """
        with self._lock:
            self._scrapers.clear()
    
    def get_scraper_info(self) -> List[Dict]:
        """
        Get information about all registered scrapers.
        
        Returns:
            List[Dict]: List of scraper information dictionaries
        """
        with self._lock:
            info = []
            for site_name, scraper in self._scrapers.items():
                info.append({
                    'site_name': site_name,
                    'class_name': scraper.__class__.__name__,
                    'timeout': scraper.timeout
                })
            return info
