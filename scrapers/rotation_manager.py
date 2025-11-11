"""
Proxy and User-Agent Rotation Manager
Prevents IP bans and blocking by rotating proxies and user agents.
"""

import logging
import random
import time
from typing import Dict, List, Optional, Tuple


class UserAgentRotator:
    """
    Manages rotation of user agents to avoid detection.
    Includes a diverse set of modern browser user agents.
    """

    def __init__(self):
        """Initialize the user agent rotator with a pool of user agents."""
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Chrome on Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox on Linux
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            
            # Mobile Chrome
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
            
            # Mobile Safari
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        ]
        
        self.current_index = 0
        self.logger = logging.getLogger(__name__)

    def get_random(self) -> str:
        """
        Get a random user agent from the pool.
        
        Returns:
            str: A random user agent string
        """
        return random.choice(self.user_agents)

    def get_next(self) -> str:
        """
        Get the next user agent in rotation.
        
        Returns:
            str: Next user agent string
        """
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent

    def add_user_agent(self, user_agent: str):
        """
        Add a custom user agent to the pool.
        
        Args:
            user_agent (str): User agent string to add
        """
        if user_agent not in self.user_agents:
            self.user_agents.append(user_agent)
            self.logger.info(f"Added custom user agent: {user_agent[:50]}...")


class ProxyRotator:
    """
    Manages rotation of proxy servers to avoid IP bans.
    Supports tracking of failed proxies and automatic rotation.
    """

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize the proxy rotator.
        
        Args:
            proxy_list (Optional[List[str]]): List of proxy URLs
                Format: 'protocol://host:port' or 'protocol://user:pass@host:port'
                Example: ['http://proxy1.com:8080', 'http://user:pass@proxy2.com:8080']
        """
        self.proxies = proxy_list if proxy_list else []
        self.current_index = 0
        self.failed_proxies = {}  # Track failures: {proxy: (count, last_fail_time)}
        self.max_failures = 3  # Max failures before removing proxy
        self.failure_cooldown = 300  # Cooldown period in seconds (5 minutes)
        self.logger = logging.getLogger(__name__)

    def add_proxy(self, proxy: str):
        """
        Add a proxy to the rotation pool.
        
        Args:
            proxy (str): Proxy URL
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.logger.info(f"Added proxy: {proxy}")

    def add_proxies(self, proxy_list: List[str]):
        """
        Add multiple proxies to the rotation pool.
        
        Args:
            proxy_list (List[str]): List of proxy URLs
        """
        for proxy in proxy_list:
            self.add_proxy(proxy)

    def get_random(self) -> Optional[Dict[str, str]]:
        """
        Get a random available proxy from the pool.
        
        Returns:
            Optional[Dict[str, str]]: Proxy dict for requests library or None
        """
        available_proxies = self._get_available_proxies()
        
        if not available_proxies:
            self.logger.warning("No available proxies")
            return None
        
        proxy = random.choice(available_proxies)
        return self._format_proxy(proxy)

    def get_next(self) -> Optional[Dict[str, str]]:
        """
        Get the next available proxy in rotation.
        
        Returns:
            Optional[Dict[str, str]]: Proxy dict for requests library or None
        """
        available_proxies = self._get_available_proxies()
        
        if not available_proxies:
            self.logger.warning("No available proxies")
            return None
        
        # Find next available proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy in available_proxies:
                return self._format_proxy(proxy)
            
            attempts += 1
        
        return None

    def mark_failure(self, proxy_dict: Optional[Dict[str, str]]):
        """
        Mark a proxy as failed.
        
        Args:
            proxy_dict (Optional[Dict[str, str]]): Proxy dict that failed
        """
        if not proxy_dict:
            return
        
        # Extract proxy URL from dict
        proxy = proxy_dict.get('http') or proxy_dict.get('https')
        
        if not proxy:
            return
        
        # Update failure count
        if proxy in self.failed_proxies:
            count, _ = self.failed_proxies[proxy]
            self.failed_proxies[proxy] = (count + 1, time.time())
        else:
            self.failed_proxies[proxy] = (1, time.time())
        
        count, _ = self.failed_proxies[proxy]
        self.logger.warning(f"Proxy failed ({count}/{self.max_failures}): {proxy}")

    def mark_success(self, proxy_dict: Optional[Dict[str, str]]):
        """
        Mark a proxy as successful, clearing failure count.
        
        Args:
            proxy_dict (Optional[Dict[str, str]]): Proxy dict that succeeded
        """
        if not proxy_dict:
            return
        
        # Extract proxy URL from dict
        proxy = proxy_dict.get('http') or proxy_dict.get('https')
        
        if proxy and proxy in self.failed_proxies:
            del self.failed_proxies[proxy]
            self.logger.info(f"Proxy success: {proxy}")

    def _get_available_proxies(self) -> List[str]:
        """
        Get list of available proxies (not failed or cooled down).
        
        Returns:
            List[str]: List of available proxy URLs
        """
        current_time = time.time()
        available = []
        
        for proxy in self.proxies:
            if proxy not in self.failed_proxies:
                available.append(proxy)
            else:
                count, last_fail = self.failed_proxies[proxy]
                
                # Check if proxy should be removed permanently
                if count >= self.max_failures:
                    # Check if cooldown period has passed
                    if current_time - last_fail > self.failure_cooldown:
                        # Reset failure count
                        del self.failed_proxies[proxy]
                        available.append(proxy)
                    # else: still in cooldown, skip
                else:
                    # Not max failures yet, still available
                    available.append(proxy)
        
        return available

    def _format_proxy(self, proxy: str) -> Dict[str, str]:
        """
        Format proxy URL for requests library.
        
        Args:
            proxy (str): Proxy URL
            
        Returns:
            Dict[str, str]: Formatted proxy dict
        """
        # Support both http and https
        return {
            'http': proxy,
            'https': proxy
        }

    def has_proxies(self) -> bool:
        """
        Check if any proxies are configured.
        
        Returns:
            bool: True if proxies are available
        """
        return len(self._get_available_proxies()) > 0

    def get_proxy_count(self) -> Tuple[int, int]:
        """
        Get total and available proxy counts.
        
        Returns:
            Tuple[int, int]: (total_count, available_count)
        """
        return len(self.proxies), len(self._get_available_proxies())


class RotationManager:
    """
    Combined manager for user agent and proxy rotation.
    Provides a unified interface for anti-detection measures.
    """

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize rotation manager.
        
        Args:
            proxy_list (Optional[List[str]]): List of proxy URLs
        """
        self.user_agent_rotator = UserAgentRotator()
        self.proxy_rotator = ProxyRotator(proxy_list)
        self.logger = logging.getLogger(__name__)

    def get_random_config(self) -> Tuple[str, Optional[Dict[str, str]]]:
        """
        Get random user agent and proxy combination.
        
        Returns:
            Tuple[str, Optional[Dict[str, str]]]: (user_agent, proxy_dict)
        """
        user_agent = self.user_agent_rotator.get_random()
        proxy = self.proxy_rotator.get_random()
        return user_agent, proxy

    def get_next_config(self) -> Tuple[str, Optional[Dict[str, str]]]:
        """
        Get next user agent and proxy in rotation.
        
        Returns:
            Tuple[str, Optional[Dict[str, str]]]: (user_agent, proxy_dict)
        """
        user_agent = self.user_agent_rotator.get_next()
        proxy = self.proxy_rotator.get_next()
        return user_agent, proxy

    def get_headers_with_rotation(self, base_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get HTTP headers with rotated user agent.
        
        Args:
            base_headers (Optional[Dict[str, str]]): Base headers to extend
            
        Returns:
            Dict[str, str]: Headers with rotated user agent
        """
        headers = base_headers.copy() if base_headers else {}
        headers['User-Agent'] = self.user_agent_rotator.get_random()
        return headers

    def add_proxies(self, proxy_list: List[str]):
        """Add multiple proxies to the pool."""
        self.proxy_rotator.add_proxies(proxy_list)

    def mark_proxy_failure(self, proxy_dict: Optional[Dict[str, str]]):
        """Mark a proxy as failed."""
        self.proxy_rotator.mark_failure(proxy_dict)

    def mark_proxy_success(self, proxy_dict: Optional[Dict[str, str]]):
        """Mark a proxy as successful."""
        self.proxy_rotator.mark_success(proxy_dict)

    def has_proxies(self) -> bool:
        """Check if proxies are configured."""
        return self.proxy_rotator.has_proxies()

    def get_status(self) -> Dict[str, any]:
        """
        Get status information about rotation manager.
        
        Returns:
            Dict: Status information
        """
        total_proxies, available_proxies = self.proxy_rotator.get_proxy_count()
        
        return {
            'user_agents_count': len(self.user_agent_rotator.user_agents),
            'total_proxies': total_proxies,
            'available_proxies': available_proxies,
            'proxies_enabled': total_proxies > 0
        }
