"""
Selenium Configuration and Driver Manager
Handles Selenium WebDriver setup with headless mode support.
Enhanced with anti-detection features and dynamic content handling.
"""

import logging
import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumConfig:
    """
    Configuration manager for Selenium WebDriver.
    Supports headless mode for CI/CD and automated environments.
    """
    
    def __init__(self, headless=True, window_size="1920,1080"):
        """
        Initialize Selenium configuration.
        
        Args:
            headless (bool): Run browser in headless mode
            window_size (str): Browser window size (width,height)
        """
        self.headless = headless
        self.window_size = window_size
        self.page_load_timeout = 30
        self.implicit_wait = 10
        self.script_timeout = 30
        
        # Configure logging
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # User agents pool for rotation (20+ realistic user agents)
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Chrome on Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            # Firefox on Linux
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            # Safari on iOS
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        ]
    
    def create_driver(self):
        """
        Create and configure a Chrome WebDriver instance with enhanced anti-detection.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver
        """
        chrome_options = Options()
        
        # Headless mode with enhanced settings
        if self.headless:
            chrome_options.add_argument('--headless=new')  # New headless mode
            chrome_options.add_argument('--disable-gpu')
        
        # Performance and stability options
        chrome_options.add_argument(f'--window-size={self.window_size}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Random user agent from pool
        random_user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f'user-agent={random_user_agent}')
        
        # Additional stealth options
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        
        # Language and locale
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en;q=0.9',
        })
        
        # Experimental options to avoid detection
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Create driver with automatic driver management
        try:
            # Try with webdriver-manager
            from webdriver_manager.chrome import ChromeDriverManager
            import os
            
            driver_path = ChromeDriverManager().install()
            
            # Fix for Windows - get the actual chromedriver.exe path
            if os.path.isdir(driver_path) or driver_path.endswith('THIRD_PARTY_NOTICES.chromedriver'):
                # Navigate to the actual exe
                driver_dir = os.path.dirname(driver_path)
                if 'chromedriver-win32' in driver_dir:
                    driver_dir = os.path.join(os.path.dirname(driver_dir), 'chromedriver-win32')
                
                # Find chromedriver.exe
                if os.path.exists(os.path.join(driver_dir, 'chromedriver.exe')):
                    driver_path = os.path.join(driver_dir, 'chromedriver.exe')
                elif os.path.exists(os.path.join(driver_dir, 'chromedriver')):
                    driver_path = os.path.join(driver_dir, 'chromedriver')
            
            service = Service(driver_path)
        except Exception as e:
            # Fallback to system ChromeDriver
            logging.warning(f"ChromeDriverManager failed: {e}. Using system chromedriver.")
            service = Service()
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        driver.set_page_load_timeout(self.page_load_timeout)
        driver.implicitly_wait(self.implicit_wait)
        driver.set_script_timeout(self.script_timeout)
        
        # Enhanced anti-detection scripts
        stealth_js = """
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins array
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Permissions query
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state:'denied' }) :
                    originalQuery(parameters)
            );
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_js})
        
        return driver
    
    def set_page_load_timeout(self, timeout):
        """
        Set page load timeout.
        
        Args:
            timeout (int): Timeout in seconds
        """
        self.page_load_timeout = timeout
    
    def set_implicit_wait(self, wait_time):
        """
        Set implicit wait time.
        
        Args:
            wait_time (int): Wait time in seconds
        """
        self.implicit_wait = wait_time


class SeleniumHelper:
    """
    Enhanced helper utilities for Selenium operations.
    Provides intelligent wait mechanisms and element interaction methods.
    """
    
    def __init__(self, driver):
        """
        Initialize SeleniumHelper with a WebDriver instance.
        
        Args:
        """
        self.driver = driver
    
    def wait_for_element(self, by, value, timeout=10):
        """
        Wait for an element to be present.
        
        Args:
            by: Locator strategy (By.ID, By.CLASS_NAME, etc.)
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement or None if timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def wait_for_element_clickable(self, by, value, timeout=10):
        """
        Wait for an element to be clickable.
        
        Args:
            by: Locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement or None if timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def wait_for_any_element(self, selectors, timeout=10):
        """
        Wait for any element from a list of selectors to appear.
        
        Args:
            selectors: List of tuples (By, value)
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement or None if timeout
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                lambda d: any(
                    d.find_elements(by, value) for by, value in selectors
                )
            )
            for by, value in selectors:
                elements = self.driver.find_elements(by, value)
                if elements:
                    return elements[0]
            return None
        except TimeoutException:
            return None
    
    def wait_for_page_load(self, timeout=30):
        """
        Wait for page to fully load including dynamic content.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            # Additional wait for dynamic content
            time.sleep(1)
            return True
        except TimeoutException:
            return False
    
    def wait_for_ajax(self, timeout=10):
        """
        Wait for AJAX/jQuery requests to complete.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            bool: True if AJAX completed
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return jQuery.active == 0') if d.execute_script('return typeof jQuery != "undefined"') else True
            )
            return True
        except:
            return True  # jQuery might not be present
    
    def safe_find_element(self, by, value):
        """
        Safely find an element without throwing exception.
        
        Args:
            by: Locator strategy
            value: Locator value
            
        Returns:
            WebElement or None if not found
        """
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None
    
    def safe_find_elements(self, by, value):
        """
        Safely find multiple elements without throwing exception.
        
        Args:
            by: Locator strategy
            value: Locator value
            
        Returns:
            List of WebElements or empty list if not found
        """
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []
    
    @staticmethod
    def get_text_safe(element, default='N/A'):
        """
        Safely get text from an element.
        
        Args:
            element: Selenium WebElement
            default: Default value if element is None or has no text
            
        Returns:
            str: Element text or default value
        """
        if element is None:
            return default
        try:
            text = element.text.strip()
            return text if text else default
        except Exception:
            return default
    
    @staticmethod
    def get_attribute_safe(element, attribute, default='N/A'):
        """
        Safely get an attribute from an element.
        
        Args:
            element: Selenium WebElement
            attribute: Attribute name
            default: Default value if not found
            
        Returns:
            str: Attribute value or default
        """
        if element is None:
            return default
        try:
            value = element.get_attribute(attribute)
            return value if value else default
        except Exception:
            return default
    
    def is_element_present(self, by, value):
        """
        Check if an element is present on the page.
        
        Args:
            by: Locator strategy
            value: Locator value
            
        Returns:
            bool: True if element present, False otherwise
        """
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False
    
    def scroll_to_element(self, element):
        """
        Scroll to make an element visible.
        
        Args:
            element: WebElement to scroll to
        """
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)  # Wait for scroll animation
        except Exception:
            pass
    
    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the page to load lazy content.
        """
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        except Exception:
            pass
    
    @staticmethod
    def human_like_delay(min_seconds=0.5, max_seconds=2.0):
        """
        Add a random delay to simulate human behavior.
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def click_element_safe(self, element):
        """
        Safely click an element with retry and scroll logic.
        
        Args:
            element: WebElement to click
            
        Returns:
            bool: True if clicked successfully
        """
        try:
            # Try normal click
            element.click()
            return True
        except Exception:
            try:
                # Scroll to element and try again
                self.scroll_to_element(element)
                element.click()
                return True
            except Exception:
                try:
                    # Try JavaScript click as last resort
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception:
                    return False
    
    def take_screenshot(self, filename='screenshot.png'):
        """
        Take a screenshot for debugging purposes.
        
        Args:
            filename: Output filename
            
        Returns:
            bool: True if successful
        """
        try:
            self.driver.save_screenshot(filename)
            return True
        except Exception:
            return False
    
    def handle_lazy_loading(self, scroll_pause_time=2, max_scrolls=5):
        """
        Handle lazy loading by scrolling down the page incrementally.
        
        Args:
            scroll_pause_time: Time to wait between scrolls
            max_scrolls: Maximum number of scroll attempts
            
        Returns:
            bool: True if completed
        """
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scrolls = 0
            
            while scrolls < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                
                # Calculate new height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scrolls += 1
            
            return True
        except Exception:
            return False
