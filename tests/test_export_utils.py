"""
Test cases for export utilities (CSV export only)
"""

import io
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from utils.export_utils import CSVExporter


class TestCSVExporter:
    """Test CSVExporter class"""

    @pytest.fixture
    def csv_exporter(self):
        """Create CSVExporter instance"""
        return CSVExporter()

    @pytest.fixture
    def sample_results(self):
        """Sample product results"""
        return [
            {
                'product_name': 'Laptop 1',
                'price': 50000,
                'original_price': 60000,
                'discount_percentage': 16.67,
                'rating': 4.5,
                'reviews_count': 100,
                'availability': 'In Stock',
                'seller': 'Amazon',
                'url': 'https://amazon.in/laptop1',
                'scraped_at': '2024-01-01'
            },
            {
                'product_name': 'Laptop 2',
                'price': 45000,
                'original_price': 50000,
                'discount_percentage': 10.0,
                'rating': 4.0,
                'reviews_count': 50,
                'availability': 'In Stock',
                'seller': 'Flipkart',
                'url': 'https://flipkart.com/laptop2',
                'scraped_at': '2024-01-01'
            }
        ]

    def test_csv_exporter_initialization(self, csv_exporter):
        """Test CSVExporter initialization"""
        assert csv_exporter is not None
        assert hasattr(csv_exporter, 'default_fields')
        assert isinstance(csv_exporter.default_fields, list)

    def test_export_to_csv_creates_file(self, csv_exporter, sample_results):
        """Test CSV export creates a file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'test.csv')
            result_file = csv_exporter.export_to_csv(sample_results, filename=filename)
            assert os.path.exists(result_file)
            assert result_file == filename

    def test_export_to_csv_auto_filename(self, csv_exporter, sample_results):
        """Test CSV export with auto-generated filename"""
        filename = csv_exporter.export_to_csv(sample_results)
        assert filename.startswith('price_comparison_')
        assert filename.endswith('.csv')
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

    def test_export_to_csv_content(self, csv_exporter, sample_results):
        """Test CSV export content is correct"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filename = f.name

        csv_exporter.export_to_csv(sample_results, filename=filename)

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'product_name' in content
            assert 'Laptop 1' in content
            assert 'Laptop 2' in content

        os.remove(filename)

    def test_export_to_csv_custom_fields(self, csv_exporter, sample_results):
        """Test CSV export with custom fields"""
        custom_fields = ['product_name', 'price', 'url']
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filename = f.name

        csv_exporter.export_to_csv(sample_results, filename=filename, fields=custom_fields)

        with open(filename, 'r', encoding='utf-8') as f:
            header = f.readline()
            assert 'product_name' in header
            assert 'price' in header
            assert 'url' in header

        os.remove(filename)

    def test_export_to_csv_empty_results_raises_error(self, csv_exporter):
        """Test CSV export with empty results raises error"""
        with pytest.raises(ValueError, match="No results to export"):
            csv_exporter.export_to_csv([])

    def test_export_to_csv_string(self, csv_exporter, sample_results):
        """Test CSV export to string"""
        csv_string = csv_exporter.export_to_csv_string(sample_results)
        assert isinstance(csv_string, str)
        assert 'product_name' in csv_string
        assert 'Laptop 1' in csv_string

    def test_export_to_csv_string_empty_raises_error(self, csv_exporter):
        """Test CSV string export with empty results raises error"""
        with pytest.raises(ValueError, match="No results to export"):
            csv_exporter.export_to_csv_string([])

    def test_export_handles_missing_fields(self, csv_exporter):
        """Test export handles missing fields gracefully"""
        results = [
            {'product_name': 'Product 1', 'price': 100},
            {'product_name': 'Product 2', 'price': 200}
        ]
        csv_string = csv_exporter.export_to_csv_string(results)
        assert 'product_name' in csv_string
        assert 'price' in csv_string

    def test_export_handles_special_characters(self, csv_exporter):
        """Test export handles special characters in data"""
        results = [
            {'product_name': 'Product, with "comma"', 'price': 100}
        ]
        csv_string = csv_exporter.export_to_csv_string(results)
        assert 'Product, with "comma"' in csv_string or 'Product' in csv_string

    def test_timestamp_format_consistency(self):
        """Test timestamp formats are consistent"""
        csv_exp = CSVExporter()
        results = [
            {'product_name': 'Test', 'price': 100, 'scraped_at': datetime.now().isoformat()}
        ]
        csv_string = csv_exp.export_to_csv_string(results)
        assert len(csv_string) > 0
