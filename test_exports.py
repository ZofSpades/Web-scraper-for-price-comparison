"""
Test script for export functionality
Run this to verify that CSV and PDF exports work correctly
"""

import os
import sys
from datetime import datetime


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from export_utils import CSVExporter, PDFExporter, create_exporter
        from cli import ScraperCLI
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("\nPlease install required packages:")
        print("  pip install -r requirements.txt")
        return False


def test_csv_export():
    """Test CSV export functionality"""
    print("\nTesting CSV export...")
    try:
        from export_utils import CSVExporter
        
        # Sample data
        test_data = [
            {
                'product_name': 'Test Product 1',
                'price': 999.99,
                'rating': 4.5,
                'seller': 'TestSeller'
            },
            {
                'product_name': 'Test Product 2',
                'price': 1999.99,
                'rating': 4.0,
                'seller': 'TestSeller2'
            }
        ]
        
        exporter = CSVExporter()
        
        # Test file export
        filename = exporter.export_to_csv(test_data, 'test_export.csv')
        assert os.path.exists(filename), "CSV file not created"
        
        # Test string export
        csv_string = exporter.export_to_csv_string(test_data)
        assert len(csv_string) > 0, "CSV string is empty"
        assert 'product_name' in csv_string, "CSV missing headers"
        
        # Clean up
        os.remove(filename)
        
        print("✓ CSV export tests passed")
        return True
    except Exception as e:
        print(f"✗ CSV export test failed: {e}")
        return False


def test_pdf_export():
    """Test PDF export functionality"""
    print("\nTesting PDF export...")
    try:
        from export_utils import PDFExporter
        
        # Sample data
        test_data = [
            {
                'product_name': 'Test Product 1',
                'price': 999.99,
                'original_price': 1499.99,
                'discount_percentage': 33,
                'rating': 4.5,
                'reviews_count': 100,
                'availability': 'In Stock',
                'seller': 'TestSeller',
                'url': 'https://example.com',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'product_name': 'Test Product 2',
                'price': 1999.99,
                'original_price': 2499.99,
                'discount_percentage': 20,
                'rating': 4.0,
                'reviews_count': 50,
                'availability': 'In Stock',
                'seller': 'TestSeller2',
                'url': 'https://example.com',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        exporter = PDFExporter()
        
        # Test PDF generation
        filename = exporter.generate_report(test_data, 'test_report.pdf')
        assert os.path.exists(filename), "PDF file not created"
        
        # Check file size (should be > 0)
        file_size = os.path.getsize(filename)
        assert file_size > 0, "PDF file is empty"
        
        # Clean up
        os.remove(filename)
        
        print("✓ PDF export tests passed")
        return True
    except Exception as e:
        print(f"✗ PDF export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli():
    """Test CLI functionality"""
    print("\nTesting CLI...")
    try:
        from cli import ScraperCLI
        
        cli = ScraperCLI()
        
        # Test help
        try:
            cli.parser.parse_args(['--help'])
        except SystemExit:
            pass  # Help exits normally
        
        # Test basic argument parsing
        args = cli.parser.parse_args(['--search', 'test'])
        assert args.search == 'test', "Search argument not parsed"
        
        print("✓ CLI tests passed")
        return True
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def test_factory():
    """Test factory function"""
    print("\nTesting factory function...")
    try:
        from export_utils import create_exporter, CSVExporter, PDFExporter
        
        csv_exp = create_exporter('csv')
        assert isinstance(csv_exp, CSVExporter), "Factory didn't create CSVExporter"
        
        pdf_exp = create_exporter('pdf')
        assert isinstance(pdf_exp, PDFExporter), "Factory didn't create PDFExporter"
        
        try:
            create_exporter('invalid')
            assert False, "Factory should raise error for invalid format"
        except ValueError:
            pass  # Expected
        
        print("✓ Factory function tests passed")
        return True
    except Exception as e:
        print(f"✗ Factory test failed: {e}")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    print("\nChecking dependencies...")
    required = [
        ('flask', 'Flask'),
        ('reportlab', 'reportlab'),
    ]
    
    all_installed = True
    for module, package in required:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not installed")
            all_installed = False
    
    if not all_installed:
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
    
    return all_installed


def main():
    """Run all tests"""
    print("="*60)
    print("Export Features Test Suite")
    print("="*60)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Imports", test_imports),
        ("CSV Export", test_csv_export),
        ("PDF Export", test_pdf_export),
        ("CLI", test_cli),
        ("Factory", test_factory),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Export features are working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
