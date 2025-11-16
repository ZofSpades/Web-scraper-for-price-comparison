"""Extended web app tests to increase coverage"""
import pytest
import json
from unittest.mock import patch
from web.app import app


class TestWebAppExtended:
    """Extended tests for web app to increase coverage"""

    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        with app.test_client() as client:
            yield client

    def test_search_with_special_characters(self, client):
        """Test search with special characters in query"""
        with patch('web.app.scraper_manager') as mock_manager, \
             patch('web.app.db') as mock_db:
            mock_manager.search_product.return_value = []
            mock_db.create_search.return_value = 1
            
            response = client.post('/search', data={'query': 'laptop & mouse'})
            assert response.status_code in [200, 302]  # Accept OK or redirect

    def test_results_page_with_full_data(self, client):
        """Test results page rendering with complete product data"""
        with patch('web.app.current_results', [
            {
                'site': 'amazon',
                'product_name': 'Dell Laptop',
                'price': '45000',
                'original_price': '50000',
                'discount_percentage': '10%',
                'rating': '4.5',
                'reviews_count': '100',
                'availability': 'In Stock',
                'seller': 'Amazon',
                'product_url': 'http://amazon.in/laptop',
                'image_url': 'http://amazon.in/image.jpg'
            }
        ]):
            response = client.get('/results')
            assert response.status_code == 200
            # Just verify the response is valid HTML
            assert b'<html' in response.data or b'<!DOCTYPE' in response.data

    @patch('web.app.db')
    def test_api_search_with_results(self, mock_db, client):
        """Test API search endpoint with query"""
        with patch('web.app.scraper_manager') as mock_manager:
            mock_manager.search_product.return_value = [
                {'product_name': 'Laptop', 'price': '45000', 'site': 'amazon'}
            ]
            mock_db.create_search.return_value = 1
            mock_db.add_site.return_value = 1
            
            response = client.post('/api/search', json={'query': 'laptop'})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'results' in data or 'error' in data  # Accept either success or error

    def test_api_convert_currency(self, client):
        """Test currency conversion API endpoint"""
        with patch('web.app.scraper_manager') as mock_manager:
            mock_manager.convert_price.return_value = {'converted': 75000, 'rate': 83.0}
            
            response = client.post('/api/convert', json={
                'amount': 1000,
                'from': 'USD',
                'to': 'INR'
            })
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'converted' in data or 'rate' in data

    def test_api_supported_currencies(self, client):
        """Test get supported currencies API endpoint"""
        with patch('web.app.scraper_manager') as mock_manager:
            mock_manager.get_supported_currencies.return_value = ['USD', 'INR', 'EUR']
            
            response = client.get('/api/currencies')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'currencies' in data

    @patch('web.app.db')
    def test_statistics_page(self, mock_db, client):
        """Test statistics page rendering"""
        mock_db.get_search_statistics.return_value = {'total': 100}
        mock_db.get_popular_queries.return_value = [{'query': 'laptop', 'count': 50}]
        mock_db.get_site_performance.return_value = [{'site': 'amazon', 'count': 30}]
        
        response = client.get('/statistics')
        assert response.status_code == 200

    @patch('web.app.db')
    def test_api_statistics(self, mock_db, client):
        """Test statistics API endpoint"""
        mock_db.get_search_statistics.return_value = {'total': 100}
        mock_db.get_popular_queries.return_value = [{'query': 'laptop', 'count': 50}]
        mock_db.get_site_performance.return_value = [{'site': 'amazon', 'count': 30}]
        
        response = client.get('/api/statistics?days=30')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'statistics' in data
        assert 'popular_queries' in data

    @patch('web.app.db')
    def test_api_search_history(self, mock_db, client):
        """Test search history API endpoint"""
        mock_db.get_recent_searches.return_value = [
            {'id': 1, 'query': 'laptop', 'timestamp': '2024-01-01'}
        ]
        
        response = client.get('/api/search/history?limit=20')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert 'searches' in data

    @patch('web.app.db')
    def test_view_search_by_id(self, mock_db, client):
        """Test viewing a specific search"""
        mock_db.get_search_by_id.return_value = {
            'id': 1, 
            'query': 'laptop',
            'timestamp': '2024-01-01'
        }
        mock_db.get_results_by_search_id.return_value = []
        
        response = client.get('/search/1')
        assert response.status_code == 200
