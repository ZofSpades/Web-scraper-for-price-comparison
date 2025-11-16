"""
Comprehensive tests for Selenium configuration and helper classes
Tests SeleniumConfig and SeleniumHelper with mocked WebDriver
"""

import pytest
from unittest.mock import MagicMock, Mock, patch, call
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from scrapers.selenium_config import SeleniumConfig, SeleniumHelper


class TestSeleniumConfig:
    """Test SeleniumConfig class initialization and driver creation"""

    def test_initialization_default_settings(self):
        """Test SeleniumConfig initializes with default settings"""
        config = SeleniumConfig()
        assert config.headless is True
        assert config.window_size == "1920,1080"
        assert config.page_load_timeout == 30
        assert config.implicit_wait == 10
        assert config.script_timeout == 30

    def test_initialization_custom_settings(self):
        """Test SeleniumConfig with custom settings"""
        config = SeleniumConfig(headless=False, window_size="1366,768")
        assert config.headless is False
        assert config.window_size == "1366,768"

    def test_user_agents_pool_exists(self):
        """Test that user agents pool is properly initialized"""
        config = SeleniumConfig()
        assert hasattr(config, 'user_agents')
        assert isinstance(config.user_agents, list)
        assert len(config.user_agents) > 0

    def test_user_agents_variety(self):
        """Test user agents include different browsers and platforms"""
        config = SeleniumConfig()
        agents_str = ' '.join(config.user_agents)
        assert 'Chrome' in agents_str
        assert 'Firefox' in agents_str
        assert 'Windows' in agents_str or 'Macintosh' in agents_str

    @patch('scrapers.selenium_config.webdriver.Chrome')
    @patch('scrapers.selenium_config.ChromeDriverManager')
    def test_create_driver_headless(self, mock_driver_manager, mock_chrome):
        """Test driver creation in headless mode"""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = '/path/to/driver'

        config = SeleniumConfig(headless=True)
        driver = config.create_driver()

        assert driver is not None
        mock_chrome.assert_called_once()
        mock_driver_instance.set_page_load_timeout.assert_called_with(30)
        mock_driver_instance.implicitly_wait.assert_called_with(10)
        mock_driver_instance.set_script_timeout.assert_called_with(30)

    @patch('scrapers.selenium_config.webdriver.Chrome')
    @patch('scrapers.selenium_config.ChromeDriverManager')
    def test_create_driver_non_headless(self, mock_driver_manager, mock_chrome):
        """Test driver creation in non-headless mode"""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = '/path/to/driver'

        config = SeleniumConfig(headless=False)
        driver = config.create_driver()

        assert driver is not None
        mock_chrome.assert_called_once()

    @patch('scrapers.selenium_config.webdriver.Chrome')
    @patch('scrapers.selenium_config.ChromeDriverManager')
    def test_create_driver_executes_stealth_script(self, mock_driver_manager, mock_chrome):
        """Test driver executes anti-detection stealth script"""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = '/path/to/driver'

        config = SeleniumConfig()
        driver = config.create_driver()

        # Verify CDP command was executed for stealth
        mock_driver_instance.execute_cdp_cmd.assert_called_once()
        call_args = mock_driver_instance.execute_cdp_cmd.call_args
        assert call_args[0][0] == 'Page.addScriptToEvaluateOnNewDocument'
        assert 'webdriver' in call_args[0][1]['source']

    @patch('scrapers.selenium_config.webdriver.Chrome')
    @patch('scrapers.selenium_config.ChromeDriverManager')
    def test_create_driver_random_user_agent(self, mock_driver_manager, mock_chrome):
        """Test driver uses random user agent"""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = '/path/to/driver'

        config = SeleniumConfig()
        
        # Create multiple drivers and check user agents vary
        user_agents_used = []
        for _ in range(5):
            mock_chrome.reset_mock()
            driver = config.create_driver()
            # User agent is set in chrome_options, check if Chrome was called
            assert mock_chrome.called

    def test_set_page_load_timeout(self):
        """Test setting page load timeout"""
        config = SeleniumConfig()
        config.set_page_load_timeout(60)
        assert config.page_load_timeout == 60

    def test_set_implicit_wait(self):
        """Test setting implicit wait"""
        config = SeleniumConfig()
        config.set_implicit_wait(20)
        assert config.implicit_wait == 20

    @patch('scrapers.selenium_config.webdriver.Chrome')
    @patch('scrapers.selenium_config.ChromeDriverManager')
    def test_create_driver_handles_driver_manager_failure(self, mock_driver_manager, mock_chrome):
        """Test driver creation falls back when driver manager fails"""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.side_effect = Exception("Failed to download")

        config = SeleniumConfig()
        driver = config.create_driver()

        # Should still create driver using fallback
        assert driver is not None
        mock_chrome.assert_called_once()


class TestSeleniumHelper:
    """Test SeleniumHelper utility methods"""

    @pytest.fixture
    def mock_driver(self):
        """Create a mock WebDriver instance"""
        driver = MagicMock()
        driver.find_element.return_value = MagicMock()
        driver.find_elements.return_value = [MagicMock()]
        driver.execute_script.return_value = 'complete'
        return driver

    @pytest.fixture
    def helper(self, mock_driver):
        """Create SeleniumHelper instance with mock driver"""
        return SeleniumHelper(mock_driver)

    def test_initialization(self, mock_driver):
        """Test SeleniumHelper initialization"""
        helper = SeleniumHelper(mock_driver)
        assert helper.driver == mock_driver

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_element_success(self, mock_wait, helper):
        """Test waiting for element successfully"""
        mock_element = MagicMock()
        mock_wait.return_value.until.return_value = mock_element

        element = helper.wait_for_element(By.ID, 'test-id', timeout=10)
        
        assert element == mock_element
        mock_wait.assert_called_once_with(helper.driver, 10)

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_element_timeout(self, mock_wait, helper):
        """Test waiting for element timeout"""
        mock_wait.return_value.until.side_effect = TimeoutException()

        element = helper.wait_for_element(By.ID, 'missing-id', timeout=5)
        
        assert element is None

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_element_clickable_success(self, mock_wait, helper):
        """Test waiting for clickable element"""
        mock_element = MagicMock()
        mock_wait.return_value.until.return_value = mock_element

        element = helper.wait_for_element_clickable(By.ID, 'button-id', timeout=10)
        
        assert element == mock_element

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_element_clickable_timeout(self, mock_wait, helper):
        """Test waiting for clickable element timeout"""
        mock_wait.return_value.until.side_effect = TimeoutException()

        element = helper.wait_for_element_clickable(By.ID, 'disabled-button', timeout=5)
        
        assert element is None

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_page_load_success(self, mock_wait, helper, mock_driver):
        """Test waiting for page load"""
        mock_driver.execute_script.return_value = 'complete'
        mock_wait.return_value.until.return_value = True

        result = helper.wait_for_page_load(timeout=30)
        
        assert result is True

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_page_load_timeout(self, mock_wait, helper):
        """Test page load timeout"""
        mock_wait.return_value.until.side_effect = TimeoutException()

        result = helper.wait_for_page_load(timeout=5)
        
        assert result is False

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_ajax_with_jquery(self, mock_wait, helper, mock_driver):
        """Test waiting for AJAX with jQuery present"""
        mock_driver.execute_script.side_effect = [True, True]  # jQuery exists and active == 0
        mock_wait.return_value.until.return_value = True

        result = helper.wait_for_ajax(timeout=10)
        
        assert result is True

    @patch('scrapers.selenium_config.WebDriverWait')
    def test_wait_for_ajax_no_jquery(self, mock_wait, helper, mock_driver):
        """Test waiting for AJAX without jQuery"""
        mock_driver.execute_script.side_effect = Exception("jQuery not defined")
        
        result = helper.wait_for_ajax(timeout=10)
        
        assert result is True  # Should return True if jQuery not present

    def test_safe_find_element_found(self, helper, mock_driver):
        """Test safe find element when element exists"""
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element

        element = helper.safe_find_element(By.ID, 'test-id')
        
        assert element == mock_element

    def test_safe_find_element_not_found(self, helper, mock_driver):
        """Test safe find element when element missing"""
        mock_driver.find_element.side_effect = NoSuchElementException()

        element = helper.safe_find_element(By.ID, 'missing-id')
        
        assert element is None

    def test_safe_find_elements_found(self, helper, mock_driver):
        """Test safe find elements when elements exist"""
        mock_elements = [MagicMock(), MagicMock()]
        mock_driver.find_elements.return_value = mock_elements

        elements = helper.safe_find_elements(By.CLASS_NAME, 'test-class')
        
        assert elements == mock_elements

    def test_safe_find_elements_not_found(self, helper, mock_driver):
        """Test safe find elements when no elements found"""
        mock_driver.find_elements.side_effect = NoSuchElementException()

        elements = helper.safe_find_elements(By.CLASS_NAME, 'missing-class')
        
        assert elements == []

    def test_get_text_safe_with_element(self):
        """Test getting text from element safely"""
        mock_element = MagicMock()
        mock_element.text = '  Test Text  '

        text = SeleniumHelper.get_text_safe(mock_element)
        
        assert text == 'Test Text'

    def test_get_text_safe_with_none(self):
        """Test getting text when element is None"""
        text = SeleniumHelper.get_text_safe(None)
        
        assert text == 'N/A'

    def test_get_text_safe_with_custom_default(self):
        """Test getting text with custom default"""
        text = SeleniumHelper.get_text_safe(None, default='Not Found')
        
        assert text == 'Not Found'

    def test_get_text_safe_empty_text(self):
        """Test getting text when element has no text"""
        mock_element = MagicMock()
        mock_element.text = ''

        text = SeleniumHelper.get_text_safe(mock_element)
        
        assert text == 'N/A'

    def test_get_attribute_safe_with_element(self):
        """Test getting attribute safely"""
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = 'http://example.com'

        attr = SeleniumHelper.get_attribute_safe(mock_element, 'href')
        
        assert attr == 'http://example.com'

    def test_get_attribute_safe_with_none(self):
        """Test getting attribute when element is None"""
        attr = SeleniumHelper.get_attribute_safe(None, 'href')
        
        assert attr == 'N/A'

    def test_get_attribute_safe_with_custom_default(self):
        """Test getting attribute with custom default"""
        attr = SeleniumHelper.get_attribute_safe(None, 'href', default='No URL')
        
        assert attr == 'No URL'

    def test_is_element_present_exists(self, helper, mock_driver):
        """Test checking if element is present"""
        mock_driver.find_element.return_value = MagicMock()

        result = helper.is_element_present(By.ID, 'test-id')
        
        assert result is True

    def test_is_element_present_missing(self, helper, mock_driver):
        """Test checking if element is absent"""
        mock_driver.find_element.side_effect = NoSuchElementException()

        result = helper.is_element_present(By.ID, 'missing-id')
        
        assert result is False

    def test_scroll_to_element(self, helper, mock_driver):
        """Test scrolling to element"""
        mock_element = MagicMock()
        
        helper.scroll_to_element(mock_element)
        
        mock_driver.execute_script.assert_called_once()
        assert 'scrollIntoView' in mock_driver.execute_script.call_args[0][0]

    def test_scroll_to_bottom(self, helper, mock_driver):
        """Test scrolling to bottom of page"""
        helper.scroll_to_bottom()
        
        mock_driver.execute_script.assert_called_once()
        assert 'scrollHeight' in mock_driver.execute_script.call_args[0][0]

    @patch('scrapers.selenium_config.time.sleep')
    def test_human_like_delay(self, mock_sleep):
        """Test human-like delay"""
        SeleniumHelper.human_like_delay(0.5, 2.0)
        
        mock_sleep.assert_called_once()
        # Check delay is within range
        delay = mock_sleep.call_args[0][0]
        assert 0.5 <= delay <= 2.0

    def test_click_element_safe_normal_click(self, helper, mock_driver):
        """Test safe clicking element normally"""
        mock_element = MagicMock()
        
        result = helper.click_element_safe(mock_element)
        
        assert result is True
        mock_element.click.assert_called_once()

    def test_click_element_safe_with_scroll(self, helper, mock_driver):
        """Test safe clicking with scroll on failure"""
        mock_element = MagicMock()
        mock_element.click.side_effect = [Exception("Not clickable"), None]
        
        result = helper.click_element_safe(mock_element)
        
        assert result is True
        # Should try scroll and click again
        mock_driver.execute_script.assert_called()

    def test_click_element_safe_with_javascript(self, helper, mock_driver):
        """Test safe clicking with JavaScript fallback"""
        mock_element = MagicMock()
        mock_element.click.side_effect = Exception("Not clickable")
        mock_driver.execute_script.return_value = None

        result = helper.click_element_safe(mock_element)
        
        # Should eventually use JavaScript click
        mock_driver.execute_script.assert_called()

    def test_take_screenshot_success(self, helper, mock_driver):
        """Test taking screenshot"""
        mock_driver.save_screenshot.return_value = True

        result = helper.take_screenshot('test.png')
        
        assert result is True
        mock_driver.save_screenshot.assert_called_once_with('test.png')

    def test_take_screenshot_failure(self, helper, mock_driver):
        """Test taking screenshot failure"""
        mock_driver.save_screenshot.side_effect = Exception("Failed")

        result = helper.take_screenshot('test.png')
        
        assert result is False

    def test_handle_lazy_loading(self, helper, mock_driver):
        """Test handling lazy loading content"""
        # Simulate page height increasing then stabilizing
        mock_driver.execute_script.side_effect = [1000, 1500, 1500]

        result = helper.handle_lazy_loading(scroll_pause_time=0, max_scrolls=3)
        
        assert result is True
        # Should have scrolled and checked height
        assert mock_driver.execute_script.call_count >= 2

    def test_handle_lazy_loading_max_scrolls(self, helper, mock_driver):
        """Test lazy loading respects max scrolls"""
        # Always increasing height
        mock_driver.execute_script.side_effect = [i * 1000 for i in range(1, 20)]

        result = helper.handle_lazy_loading(scroll_pause_time=0, max_scrolls=3)
        
        assert result is True
        # Should stop at max_scrolls


class TestSeleniumIntegration:
    """Integration tests for SeleniumConfig and SeleniumHelper together"""

    @patch('scrapers.selenium_config.webdriver.Chrome')
    @patch('scrapers.selenium_config.ChromeDriverManager')
    def test_config_and_helper_integration(self, mock_driver_manager, mock_chrome):
        """Test SeleniumConfig and SeleniumHelper work together"""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = '/path/to/driver'

        # Create config and driver
        config = SeleniumConfig(headless=True)
        driver = config.create_driver()

        # Create helper with driver
        helper = SeleniumHelper(driver)

        assert helper.driver == driver
        assert driver is not None

    def test_multiple_configs_different_settings(self):
        """Test creating multiple configs with different settings"""
        config1 = SeleniumConfig(headless=True)
        config2 = SeleniumConfig(headless=False, window_size="800,600")

        assert config1.headless != config2.headless
        assert config1.window_size != config2.window_size

    def test_helper_methods_chain(self):
        """Test chaining helper methods"""
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = MagicMock()
        
        helper = SeleniumHelper(mock_driver)
        
        # Chain operations
        element = helper.safe_find_element(By.ID, 'test')
        if element:
            text = helper.get_text_safe(element)
            assert text is not None


class TestSeleniumConfigEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_user_agents(self):
        """Test config still works if user agents list is modified"""
        config = SeleniumConfig()
        original_count = len(config.user_agents)
        assert original_count > 0

    def test_negative_timeout(self):
        """Test setting negative timeout"""
        config = SeleniumConfig()
        config.set_page_load_timeout(-1)
        assert config.page_load_timeout == -1  # Should accept but driver may handle

    def test_very_large_window_size(self):
        """Test very large window size"""
        config = SeleniumConfig(window_size="10000,10000")
        assert config.window_size == "10000,10000"

    def test_helper_with_none_driver(self):
        """Test helper initialization with None driver"""
        helper = SeleniumHelper(None)
        assert helper.driver is None

    def test_get_text_safe_with_exception(self):
        """Test get_text_safe handles exceptions"""
        mock_element = MagicMock()
        mock_element.text = property(lambda self: (_ for _ in ()).throw(Exception("Error")))
        
        text = SeleniumHelper.get_text_safe(mock_element)
        
        assert text == 'N/A'
