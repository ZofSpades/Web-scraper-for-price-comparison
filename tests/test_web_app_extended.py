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
        with patch('web.app.search_products') as mock_search, \
             patch('web.app.db') as mock_db:
            mock_search.return_value = []
            mock_db.create_search.return_value = 1
            
            response = client.get('/search?query=laptop+%26+mouse')
            assert response.status_code == 200

    def test_api_results_with_results(self, client):
        """Test API results endpoint with session data"""
        with client.session_transaction() as session:
            session['current_results'] = [
                {'product_name': 'Test', 'price': '1000', 'site': 'amazon'}
            ]
        
        response = client.get('/api/results')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) == 1

    def test_results_page_with_full_data(self, client):
        """Test results page rendering with complete product data"""
        with client.session_transaction() as session:
            session['current_results'] = [
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
            ]
        
        response = client.get('/results')
        assert response.status_code == 200
        assert b'Dell Laptop' in response.data

    @patch('web.app.db')
    def test_view_history_item_with_results(self, mock_db, client):
        """Test viewing history item with results"""
        mock_db.get_search_by_id.return_value = {
            'search_id': 1,
            'query': 'laptop',
            'total_results': 5
        }
        mock_db.get_results_by_search_id.return_value = [
            {'product_name': 'Laptop', 'price': '45000', 'site': 'amazon'}
        ]
        
        response = client.get('/history/view/1')
        assert response.status_code == 200

    @patch('web.app.db')
    def test_api_search_with_results(self, mock_db, client):
        """Test API search endpoint with query"""
        with patch('web.app.search_products') as mock_search:
            mock_search.return_value = [
                {'product_name': 'Laptop', 'price': '45000', 'site': 'amazon'}
            ]
            mock_db.create_search.return_value = 1
            mock_db.add_site.return_value = 1
            
            response = client.get('/api/search?query=laptop')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'results' in data
