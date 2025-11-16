"""
Comprehensive working tests for all scrapers with correct method calls
"""

import pytest
from unittest.mock import MagicMock, Mock, patch

from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from scrapers.croma_scraper import CromaScraper
from scrapers.snapdeal_scraper import SnapdealScraper
from scrapers.myntra_scraper import MyntraScraper
from scrapers.hybrid_scraper import HybridScraper
from scrapers.base_scraper import BaseScraper


class TestAmazonScraperComplete:
    """Complete tests for Amazon scraper"""

    @pytest.fixture
    def scraper(self):
        return AmazonScraper()

    def test_initialization(self, scraper):
        assert scraper.site_name == "Amazon"
        assert "amazon" in scraper.base_url.lower()

    def test_scrape_with_product_name(self, scraper):
        with patch.object(scraper, '_search_and_scrape') as mock:
            mock.return_value = {'title': 'Laptop', 'price': '50000'}
            result = scraper.scrape("laptop")
            mock.assert_called_once_with("laptop")

    def test_scrape_with_amazon_url(self, scraper):
        url = "https://www.amazon.in/dp/B0TEST"
        with patch.object(scraper, '_scrape_static') as mock:
            mock.return_value = {'title': 'Product', 'price': '1000'}
            scraper.scrape(url)
            mock.assert_called_once()


class TestFlipkartScraperComplete:
    """Complete tests for Flipkart scraper"""

    @pytest.fixture
    def scraper(self):
        return FlipkartScraper()

    def test_initialization(self, scraper):
        assert scraper.site_name == "Flipkart"
        assert "flipkart" in scraper.base_url.lower()

    def test_scrape_with_product_name(self, scraper):
        with patch.object(scraper, '_search_and_scrape') as mock:
            mock.return_value = {'title': 'Phone', 'price': '30000'}
            result = scraper.scrape("phone")
            mock.assert_called_once()


class TestCromaScraperComplete:
    """Complete tests for Croma scraper"""

    @pytest.fixture
    def scraper(self):
        return CromaScraper()

    def test_initialization(self, scraper):
        assert scraper.site_name == "Croma"
        assert "croma" in scraper.base_url.lower()


class TestSnapdealScraperComplete:
    """Complete tests for Snapdeal scraper"""

    @pytest.fixture
    def scraper(self):
        return SnapdealScraper()

    def test_initialization(self, scraper):
        assert scraper.site_name == "Snapdeal"
        assert "snapdeal" in scraper.base_url.lower()


class TestMyntraScraperComplete:
    """Complete tests for Myntra scraper"""

    @pytest.fixture
    def scraper(self):
        return MyntraScraper()

    def test_initialization(self, scraper):
        assert scraper.site_name == "Myntra"
        assert "myntra" in scraper.base_url.lower()


class TestHybridScraperComplete:
    """Complete tests for HybridScraper"""

    def test_initialization(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {'title': 'Test', 'price': '100'}
            def _scrape_with_selenium(self, input_data):
                return {'title': 'Test', 'price': '100'}

        scraper = TestScraper()
        assert scraper.use_selenium is False
        assert scraper.retry_attempts == 2

    def test_should_fallback_to_selenium_with_error(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        result = {'error': 'test error'}
        assert scraper._should_fallback_to_selenium(result) is True

    def test_should_fallback_with_missing_title(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        result = {'title': 'N/A', 'price': '100'}
        assert scraper._should_fallback_to_selenium(result) is True

    def test_should_fallback_with_missing_price(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        result = {'title': 'Good Title', 'price': 'N/A'}
        assert scraper._should_fallback_to_selenium(result) is True

    def test_no_fallback_with_valid_data(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        result = {'title': 'Valid Product Title', 'price': '999'}
        assert scraper._should_fallback_to_selenium(result) is False

    def test_set_selenium_mode(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        scraper.set_selenium_mode(True)
        assert scraper.use_selenium is True

    def test_set_headless(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        scraper.set_headless(False)
        assert scraper.selenium_config.headless is False

    def test_set_retry_attempts(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        scraper.set_retry_attempts(5)
        assert scraper.retry_attempts == 5

    def test_get_scraping_method(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        assert scraper.get_scraping_method() == 'static'
        scraper.static_failed = True
        assert scraper.get_scraping_method() == 'selenium'

    def test_get_scraping_stats(self):
        class TestScraper(HybridScraper):
            def _scrape_static(self, input_data):
                return {}
            def _scrape_with_selenium(self, input_data):
                return {}

        scraper = TestScraper()
        stats = scraper.get_scraping_stats()
        assert 'method_used' in stats
        assert 'selenium_mode' in stats
        assert 'retry_attempts' in stats
        assert 'headless' in stats


class TestBaseScraperComplete:
    """Complete tests for BaseScraper"""

    def test_base_scraper_initialization(self):
        class TestScraper(BaseScraper):
            def scrape(self, input_data):
                return {}

        scraper = TestScraper()
        assert scraper.timeout == 10

    def test_get_headers(self):
        class TestScraper(BaseScraper):
            def scrape(self, input_data):
                return {}

        scraper = TestScraper()
        headers = scraper.get_headers()
        assert 'User-Agent' in headers
        assert isinstance(headers, dict)

    def test_create_error_result(self):
        class TestScraper(BaseScraper):
            def scrape(self, input_data):
                return {}

        scraper = TestScraper()
        error = scraper.create_error_result("Test error")
        assert 'error' in error
        assert error['error'] == "Test error"


class TestScraperCommonBehavior:
    """Test common behavior across all scrapers"""

    @pytest.mark.parametrize("scraper_class", [
        AmazonScraper,
        FlipkartScraper,
        CromaScraper,
        SnapdealScraper,
        MyntraScraper
    ])
    def test_all_scrapers_have_required_attributes(self, scraper_class):
        scraper = scraper_class()
        assert hasattr(scraper, 'site_name')
        assert hasattr(scraper, 'base_url')
        assert hasattr(scraper, 'scrape')
        assert len(scraper.site_name) > 0
        assert scraper.base_url.startswith('http')

    @pytest.mark.parametrize("scraper_class", [
        AmazonScraper,
        FlipkartScraper,
        CromaScraper,
        SnapdealScraper,
        MyntraScraper
    ])
    def test_all_scrapers_inherit_from_hybrid(self, scraper_class):
        assert issubclass(scraper_class, HybridScraper)

    @pytest.mark.parametrize("scraper_class", [
        AmazonScraper,
        FlipkartScraper,
        CromaScraper,
        SnapdealScraper,
        MyntraScraper
    ])
    def test_scrapers_implement_required_methods(self, scraper_class):
        scraper = scraper_class()
        assert callable(getattr(scraper, 'scrape', None))
        assert callable(getattr(scraper, 'get_headers', None))
        assert callable(getattr(scraper, 'create_error_result', None))
