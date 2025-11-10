"""
Selenium Configuration and Driver Manager
Handles Selenium WebDriver setup with headless mode support.
"""

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

        # Configure logging
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

    def create_driver(self):
        """
        Create and configure a Chrome WebDriver instance.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver
        """
        chrome_options = Options()

        # Headless mode
        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

        # Performance and stability options
        chrome_options.add_argument(f'--window-size={self.window_size}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        # User agent (polite headers)
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/119.0.0.0 Safari/537.36'
        )

        # Additional options for headless stability
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--ignore-certificate-errors')

        # Experimental options to avoid detection
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Create driver with automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Set timeouts
        driver.set_page_load_timeout(self.page_load_timeout)
        driver.implicitly_wait(self.implicit_wait)

        # Remove webdriver property to avoid detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })

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
    Helper utilities for Selenium operations.
    """

    @staticmethod
    def wait_for_element(driver, by, value, timeout=10):
        """
        Wait for an element to be present.

        Args:
            driver: Selenium WebDriver instance
            by: Locator strategy (By.ID, By.CLASS_NAME, etc.)
            value: Locator value
            timeout: Maximum wait time in seconds

        Returns:
            WebElement or None if timeout
        """
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception:
            return None

    @staticmethod
    def wait_for_element_clickable(driver, by, value, timeout=10):
        """
        Wait for an element to be clickable.

        Args:
            driver: Selenium WebDriver instance
            by: Locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds

        Returns:
            WebElement or None if timeout
        """
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception:
            return None

    @staticmethod
    def safe_find_element(driver, by, value):
        """
        Safely find an element without throwing exception.

        Args:
            driver: Selenium WebDriver instance
            by: Locator strategy
            value: Locator value

        Returns:
            WebElement or None if not found
        """
        try:
            return driver.find_element(by, value)
        except Exception:
            return None

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

    @staticmethod
    def is_element_present(driver, by, value):
        """
        Check if an element is present on the page.

        Args:
            driver: Selenium WebDriver instance
            by: Locator strategy
            value: Locator value

        Returns:
            bool: True if element present, False otherwise
        """
        try:
            driver.find_element(by, value)
            return True
        except Exception:
            return False

    @staticmethod
    def scroll_to_element(driver, element):
        """
        Scroll to make an element visible.

        Args:
            driver: Selenium WebDriver instance
            element: WebElement to scroll to
        """
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except Exception as e:
            # Silently ignore scroll errors - element may not be scrollable
            logging.debug(f"Scroll to element failed: {e}")
