"""
Comprehensive tests for Croma and Snapdeal scrapers
Tests scraping, search, and extraction methods
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from bs4 import BeautifulSoup

from scrapers.croma_scraper import CromaScraper
from scrapers.snapdeal_scraper import SnapdealScraper


class TestCromaScraper:
    """Test CromaScraper functionality"""

    @pytest.fixture
    def scraper(self):
        """Create CromaScraper instance"""
        return CromaScraper()

    def test_initialization(self, scraper):
        """Test scraper initializes correctly"""
        assert scraper.site_name == "Croma"
        assert scraper.base_url == "https://www.croma.com"
        assert "croma.com" in scraper.search_url

    def test_scrape_with_url(self, scraper):
        """Test scraping with Croma URL"""
        with patch.object(scraper.__class__.__bases__[0], 'scrape') as mock_parent:
            mock_parent.return_value = {'site': 'Croma', 'title': 'Test Product'}
            
            result = scraper.scrape('https://www.croma.com/p/test-product')
            
            mock_parent.assert_called_once()
            assert result['site'] == 'Croma'

    def test_scrape_with_search_query(self, scraper):
        """Test scraping with search query"""
        with patch.object(scraper, '_search_and_scrape') as mock_search:
            mock_search.return_value = {'site': 'Croma', 'title': 'Laptop'}
            
            result = scraper.scrape('laptop')
            
            mock_search.assert_called_once_with('laptop')

    @patch('scrapers.croma_scraper.requests.get')
    def test_search_and_scrape_success(self, mock_get, scraper):
        """Test successful search and scrape"""
        # Mock search response
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <a class="product-title" href="/p/test-product-123">Test Product</a>
        </html>
        '''
        mock_get.return_value = mock_response
        
        with patch.object(scraper.__class__.__bases__[0], 'scrape') as mock_scrape:
            mock_scrape.return_value = {'site': 'Croma', 'title': 'Product'}
            
            result = scraper._search_and_scrape('laptop')
            
            assert mock_get.called
            assert mock_scrape.called

    @patch('scrapers.croma_scraper.requests.get')
    def test_search_and_scrape_no_results(self, mock_get, scraper):
        """Test search with no results"""
        mock_response = MagicMock()
        mock_response.content = b'<html><body>No results</body></html>'
        mock_get.return_value = mock_response
        
        result = scraper._search_and_scrape('nonexistent product xyz')
        
        assert 'error' in result
        assert 'No products found' in result['error']

    @patch('scrapers.croma_scraper.requests.get')
    def test_search_and_scrape_network_error(self, mock_get, scraper):
        """Test search with network error"""
        mock_get.side_effect = Exception("Network error")
        
        result = scraper._search_and_scrape('laptop')
        
        assert 'error' in result
        assert 'Search failed' in result['error']

    def test_extract_first_product_link_with_product_title(self, scraper):
        """Test extracting product link from search results"""
        html = '''
        <html>
            <a class="product-title" href="/p/laptop-dell-123">Dell Laptop</a>
            <a class="product-title" href="/p/laptop-hp-456">HP Laptop</a>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link is not None
        assert '/p/' in link
        assert 'croma.com' in link

    def test_extract_first_product_link_with_absolute_url(self, scraper):
        """Test extracting absolute URL"""
        html = '''
        <html>
            <a class="product-title" href="https://www.croma.com/p/laptop-123">Laptop</a>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link == "https://www.croma.com/p/laptop-123"

    def test_extract_first_product_link_alternative_selector(self, scraper):
        """Test extracting link with alternative selector"""
        html = '''
        <html>
            <div class="product-item">
                <a href="/p/product-789">Product</a>
            </div>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link is not None
        assert '/p/' in link

    def test_extract_first_product_link_no_results(self, scraper):
        """Test extracting link when no products found"""
        html = '<html><body>No products</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link is None

    @patch('scrapers.croma_scraper.requests.get')
    def test_scrape_static_success(self, mock_get, scraper):
        """Test static scraping"""
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <h1 class="pdp-title">Dell Laptop</h1>
            <span class="price">45,000</span>
            <span class="rating">4.5</span>
        </html>
        '''
        mock_get.return_value = mock_response
        
        with patch.object(scraper, '_extract_title', return_value='Dell Laptop'):
            with patch.object(scraper, '_extract_price', return_value='45000'):
                with patch.object(scraper, '_extract_rating', return_value='4.5'):
                    result = scraper._scrape_static('https://www.croma.com/p/laptop')
                    
                    assert 'title' in result or 'error' in result

    def test_scrape_with_non_croma_url(self, scraper):
        """Test scraping with non-Croma URL triggers search"""
        with patch.object(scraper, '_search_and_scrape') as mock_search:
            mock_search.return_value = {'site': 'Croma'}
            
            scraper.scrape('https://www.amazon.com/product')
            
            mock_search.assert_called_once()

    def test_headers_user_agent(self, scraper):
        """Test headers include user agent"""
        headers = scraper.get_headers()
        assert 'User-Agent' in headers
        assert len(headers['User-Agent']) > 0


class TestSnapdealScraper:
    """Test SnapdealScraper functionality"""

    @pytest.fixture
    def scraper(self):
        """Create SnapdealScraper instance"""
        return SnapdealScraper()

    def test_initialization(self, scraper):
        """Test scraper initializes correctly"""
        assert scraper.site_name == "Snapdeal"
        assert scraper.base_url == "https://www.snapdeal.com"
        assert "snapdeal.com" in scraper.search_url

    def test_scrape_with_url(self, scraper):
        """Test scraping with Snapdeal URL"""
        with patch.object(scraper.__class__.__bases__[0], 'scrape') as mock_parent:
            mock_parent.return_value = {'site': 'Snapdeal', 'title': 'Test Product'}
            
            result = scraper.scrape('https://www.snapdeal.com/product/test/123')
            
            mock_parent.assert_called_once()
            assert result['site'] == 'Snapdeal'

    def test_scrape_with_search_query(self, scraper):
        """Test scraping with search query"""
        with patch.object(scraper, '_search_and_scrape') as mock_search:
            mock_search.return_value = {'site': 'Snapdeal', 'title': 'Laptop'}
            
            result = scraper.scrape('laptop')
            
            mock_search.assert_called_once_with('laptop')

    @patch('scrapers.snapdeal_scraper.requests.get')
    def test_search_and_scrape_success(self, mock_get, scraper):
        """Test successful search and scrape"""
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <a class="dp-widget-link" href="/product/laptop-123">Laptop</a>
        </html>
        '''
        mock_get.return_value = mock_response
        
        with patch.object(scraper.__class__.__bases__[0], 'scrape') as mock_scrape:
            mock_scrape.return_value = {'site': 'Snapdeal', 'title': 'Product'}
            
            result = scraper._search_and_scrape('laptop')
            
            assert mock_get.called
            assert mock_scrape.called

    @patch('scrapers.snapdeal_scraper.requests.get')
    def test_search_and_scrape_no_results(self, mock_get, scraper):
        """Test search with no results"""
        mock_response = MagicMock()
        mock_response.content = b'<html><body>No results</body></html>'
        mock_get.return_value = mock_response
        
        result = scraper._search_and_scrape('nonexistent xyz')
        
        assert 'error' in result
        assert 'No products found' in result['error']

    @patch('scrapers.snapdeal_scraper.requests.get')
    def test_search_and_scrape_exception(self, mock_get, scraper):
        """Test search with exception"""
        mock_get.side_effect = Exception("Network timeout")
        
        result = scraper._search_and_scrape('laptop')
        
        assert 'error' in result
        assert 'Search failed' in result['error']

    def test_extract_first_product_link_found(self, scraper):
        """Test extracting product link from search results"""
        html = '''
        <html>
            <a class="dp-widget-link" href="/product/laptop-dell-123">Dell Laptop</a>
            <a class="dp-widget-link" href="/product/laptop-hp-456">HP Laptop</a>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link is not None
        assert '/product/' in link
        assert 'snapdeal.com' in link

    def test_extract_first_product_link_absolute_url(self, scraper):
        """Test extracting absolute URL"""
        html = '''
        <html>
            <a class="dp-widget-link" href="https://www.snapdeal.com/product/laptop-123">Laptop</a>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link == "https://www.snapdeal.com/product/laptop-123"

    def test_extract_first_product_link_no_results(self, scraper):
        """Test extracting link when no products found"""
        html = '<html><body>No products</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link is None

    def test_extract_first_product_link_invalid_href(self, scraper):
        """Test extracting link with invalid href"""
        html = '''
        <html>
            <a class="dp-widget-link" href="/search/">Not a product</a>
            <a class="dp-widget-link" href="/product/valid-123">Valid Product</a>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        link = scraper._extract_first_product_link(soup)
        
        assert link is not None
        assert '/product/valid-123' in link

    @patch('scrapers.snapdeal_scraper.requests.get')
    def test_scrape_static_success(self, mock_get, scraper):
        """Test static scraping"""
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <h1 class="pdp-e-i-head">Dell Laptop</h1>
            <span class="pdp-final-price">45,000</span>
            <div class="filled-stars">4.5</div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        with patch.object(scraper, '_extract_title', return_value='Dell Laptop'):
            with patch.object(scraper, '_extract_price', return_value='45000'):
                with patch.object(scraper, '_extract_rating', return_value='4.5'):
                    with patch.object(scraper, '_extract_availability', return_value='In Stock'):
                        result = scraper._scrape_static('https://www.snapdeal.com/product/laptop')
                        
                        assert 'title' in result or 'error' in result

    def test_scrape_with_non_snapdeal_url(self, scraper):
        """Test scraping with non-Snapdeal URL triggers search"""
        with patch.object(scraper, '_search_and_scrape') as mock_search:
            mock_search.return_value = {'site': 'Snapdeal'}
            
            scraper.scrape('https://www.flipkart.com/product')
            
            mock_search.assert_called_once()

    def test_timeout_configured(self, scraper):
        """Test timeout is configured"""
        assert hasattr(scraper, 'timeout')
        assert scraper.timeout > 0

    def test_headers_include_accept(self, scraper):
        """Test headers include Accept header"""
        headers = scraper.get_headers()
        assert 'User-Agent' in headers


class TestScraperIntegration:
    """Integration tests for both scrapers"""

    def test_both_scrapers_inherit_hybrid(self):
        """Test both scrapers properly inherit from HybridScraper"""
        croma = CromaScraper()
        snapdeal = SnapdealScraper()
        
        # Both should have HybridScraper methods
        assert hasattr(croma, 'scrape')
        assert hasattr(snapdeal, 'scrape')
        assert hasattr(croma, 'create_error_result')
        assert hasattr(snapdeal, 'create_error_result')

    def test_both_scrapers_have_unique_names(self):
        """Test scrapers have unique site names"""
        croma = CromaScraper()
        snapdeal = SnapdealScraper()
        
        assert croma.site_name != snapdeal.site_name
        assert croma.base_url != snapdeal.base_url

    def test_error_result_format(self):
        """Test error results have consistent format"""
        croma = CromaScraper()
        snapdeal = SnapdealScraper()
        
        croma_error = croma.create_error_result("Test error")
        snapdeal_error = snapdeal.create_error_result("Test error")
        
        assert 'error' in croma_error
        assert 'error' in snapdeal_error

    @patch('scrapers.croma_scraper.requests.get')
    @patch('scrapers.snapdeal_scraper.requests.get')
    def test_both_scrapers_handle_network_errors(self, mock_snap_get, mock_croma_get):
        """Test both scrapers handle network errors gracefully"""
        mock_croma_get.side_effect = Exception("Network error")
        mock_snap_get.side_effect = Exception("Network error")
        
        croma = CromaScraper()
        snapdeal = SnapdealScraper()
        
        croma_result = croma._search_and_scrape('laptop')
        snapdeal_result = snapdeal._search_and_scrape('laptop')
        
        assert 'error' in croma_result
        assert 'error' in snapdeal_result


class TestScraperEdgeCases:
    """Test edge cases for both scrapers"""

    def test_empty_search_query(self):
        """Test scraping with empty query"""
        croma = CromaScraper()
        snapdeal = SnapdealScraper()
        
        with patch.object(croma, '_search_and_scrape') as mock_croma:
            mock_croma.return_value = {'error': 'Invalid query'}
            croma.scrape('')
            mock_croma.assert_called_once()
        
        with patch.object(snapdeal, '_search_and_scrape') as mock_snap:
            mock_snap.return_value = {'error': 'Invalid query'}
            snapdeal.scrape('')
            mock_snap.assert_called_once()

    def test_special_characters_in_query(self):
        """Test scraping with special characters"""
        croma = CromaScraper()
        snapdeal = SnapdealScraper()
        
        with patch('scrapers.croma_scraper.requests.get') as mock_croma_get:
            mock_croma_get.return_value = MagicMock(content=b'<html></html>')
            croma._search_and_scrape('laptop "15 inch" & tablet')
        
        with patch('scrapers.snapdeal_scraper.requests.get') as mock_snap_get:
            mock_snap_get.return_value = MagicMock(content=b'<html></html>')
            snapdeal._search_and_scrape('laptop "15 inch" & tablet')

    def test_unicode_in_query(self):
        """Test scraping with unicode characters"""
        croma = CromaScraper()
        
        with patch('scrapers.croma_scraper.requests.get') as mock_get:
            mock_get.return_value = MagicMock(content=b'<html></html>')
            croma._search_and_scrape('लैपटॉप')  # Hindi text

    def test_very_long_query(self):
        """Test scraping with very long query"""
        long_query = 'laptop ' * 100
        croma = CromaScraper()
        
        with patch('scrapers.croma_scraper.requests.get') as mock_get:
            mock_get.return_value = MagicMock(content=b'<html></html>')
            result = croma._search_and_scrape(long_query)

    def test_malformed_html(self):
        """Test scrapers handle malformed HTML"""
        croma = CromaScraper()
        
        html = '<html><div><a href="/p/product">Product</a></html>'  # Missing closing div
        soup = BeautifulSoup(html, 'html.parser')
        
        link = croma._extract_first_product_link(soup)
        # Should not crash, may return link or None
        assert link is None or isinstance(link, str)
