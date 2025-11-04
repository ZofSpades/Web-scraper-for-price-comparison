"""
Example script demonstrating CSV and PDF export functionality
Run this to test the export features with sample data
"""

from export_utils import CSVExporter, PDFExporter
from datetime import datetime


def generate_sample_data():
    """Generate sample product data for demonstration"""
    return [
        {
            'product_name': 'Samsung Galaxy S24 Ultra - 256GB',
            'price': 124999.00,
            'original_price': 149999.00,
            'discount_percentage': 17,
            'rating': 4.6,
            'reviews_count': 3421,
            'availability': 'In Stock',
            'seller': 'Amazon',
            'url': 'https://amazon.in/samsung-s24',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'Apple iPhone 15 Pro - 128GB',
            'price': 134900.00,
            'original_price': 139900.00,
            'discount_percentage': 4,
            'rating': 4.8,
            'reviews_count': 5234,
            'availability': 'In Stock',
            'seller': 'Flipkart',
            'url': 'https://flipkart.com/iphone-15-pro',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'OnePlus 12 - 256GB',
            'price': 64999.00,
            'original_price': 69999.00,
            'discount_percentage': 7,
            'rating': 4.5,
            'reviews_count': 2156,
            'availability': 'In Stock',
            'seller': 'Amazon',
            'url': 'https://amazon.in/oneplus-12',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'Google Pixel 8 Pro - 128GB',
            'price': 84999.00,
            'original_price': 106999.00,
            'discount_percentage': 21,
            'rating': 4.4,
            'reviews_count': 1876,
            'availability': 'Limited Stock',
            'seller': 'Flipkart',
            'url': 'https://flipkart.com/pixel-8-pro',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'Xiaomi 14 Pro - 256GB',
            'price': 79999.00,
            'original_price': 89999.00,
            'discount_percentage': 11,
            'rating': 4.3,
            'reviews_count': 1543,
            'availability': 'In Stock',
            'seller': 'Amazon',
            'url': 'https://amazon.in/xiaomi-14-pro',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'Vivo X100 Pro - 256GB',
            'price': 89999.00,
            'original_price': 89999.00,
            'discount_percentage': 0,
            'rating': 4.2,
            'reviews_count': 987,
            'availability': 'In Stock',
            'seller': 'Snapdeal',
            'url': 'https://snapdeal.com/vivo-x100',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'OPPO Find X7 Ultra - 256GB',
            'price': 94999.00,
            'original_price': 109999.00,
            'discount_percentage': 14,
            'rating': 4.4,
            'reviews_count': 1234,
            'availability': 'In Stock',
            'seller': 'Flipkart',
            'url': 'https://flipkart.com/oppo-find-x7',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'product_name': 'Realme GT 5 Pro - 256GB',
            'price': 54999.00,
            'original_price': 64999.00,
            'discount_percentage': 15,
            'rating': 4.3,
            'reviews_count': 2345,
            'availability': 'In Stock',
            'seller': 'Amazon',
            'url': 'https://amazon.in/realme-gt5-pro',
            'scraped_at': datetime.now().isoformat()
        },
    ]


def demo_csv_export():
    """Demonstrate CSV export functionality"""
    print("\n" + "="*60)
    print("CSV Export Demonstration")
    print("="*60)
    
    # Get sample data
    products = generate_sample_data()
    
    # Initialize CSV exporter
    csv_exporter = CSVExporter()
    
    # Export all products
    print("\n1. Exporting all products to CSV...")
    filename = csv_exporter.export_to_csv(products, 'demo_all_products.csv')
    print(f"   ✓ Exported {len(products)} products to: {filename}")
    
    # Export with custom fields
    print("\n2. Exporting with custom fields...")
    custom_fields = ['product_name', 'price', 'rating', 'seller']
    filename = csv_exporter.export_to_csv(
        products, 
        'demo_custom_fields.csv',
        fields=custom_fields
    )
    print(f"   ✓ Exported to: {filename}")
    print(f"   ✓ Fields: {', '.join(custom_fields)}")
    
    # Export selected products
    print("\n3. Exporting selected products (top 3)...")
    selected_indices = [0, 1, 2]
    filename = csv_exporter.export_selected_products(
        products,
        selected_indices,
        'demo_top3.csv'
    )
    print(f"   ✓ Exported {len(selected_indices)} products to: {filename}")
    
    # Generate CSV string (for web downloads)
    print("\n4. Generating CSV string (first 50 characters)...")
    csv_string = csv_exporter.export_to_csv_string(products)
    print(f"   ✓ Generated CSV string: {csv_string[:50]}...")


def demo_pdf_export():
    """Demonstrate PDF export functionality"""
    print("\n" + "="*60)
    print("PDF Export Demonstration")
    print("="*60)
    
    # Get sample data
    products = generate_sample_data()
    
    # Initialize PDF exporter
    pdf_exporter = PDFExporter()
    
    # Generate comprehensive report
    print("\n1. Generating comprehensive PDF report...")
    filename = pdf_exporter.generate_report(
        products,
        'demo_comprehensive_report.pdf',
        title='Smartphone Price Comparison Report',
        include_charts=True
    )
    print(f"   ✓ Generated report: {filename}")
    print(f"   ✓ Includes: Summary stats, charts, product table, best deals")
    
    # Generate report without charts
    print("\n2. Generating PDF report without charts...")
    filename = pdf_exporter.generate_report(
        products,
        'demo_no_charts.pdf',
        title='Simple Price Comparison',
        include_charts=False
    )
    print(f"   ✓ Generated report: {filename}")
    
    # Generate comparison for selected products
    print("\n3. Generating comparison report for top 3...")
    selected_indices = [0, 1, 2]
    filename = pdf_exporter.generate_comparison_report(
        products,
        selected_indices,
        'demo_top3_comparison.pdf'
    )
    print(f"   ✓ Generated comparison: {filename}")


def demo_statistics():
    """Display statistics about the sample data"""
    print("\n" + "="*60)
    print("Sample Data Statistics")
    print("="*60)
    
    products = generate_sample_data()
    
    prices = [p['price'] for p in products]
    ratings = [p['rating'] for p in products]
    discounts = [p['discount_percentage'] for p in products if p['discount_percentage'] > 0]
    
    print(f"\nTotal Products: {len(products)}")
    print(f"\nPrice Range:")
    print(f"  Lowest:  ₹{min(prices):,.2f}")
    print(f"  Highest: ₹{max(prices):,.2f}")
    print(f"  Average: ₹{sum(prices)/len(prices):,.2f}")
    
    print(f"\nRatings:")
    print(f"  Average: {sum(ratings)/len(ratings):.2f}/5.0")
    print(f"  Highest: {max(ratings)}/5.0")
    
    print(f"\nDiscounts:")
    print(f"  Products with discount: {len(discounts)}/{len(products)}")
    if discounts:
        print(f"  Average discount: {sum(discounts)/len(discounts):.1f}%")
        print(f"  Best discount: {max(discounts)}%")


def main():
    """Run all demonstrations"""
    print("\n" + "="*60)
    print("Web Scraper Export Features - Demonstration")
    print("Team 5 - Price Comparison Project (P60)")
    print("="*60)
    
    try:
        # Show sample data statistics
        demo_statistics()
        
        # Demonstrate CSV export
        demo_csv_export()
        
        # Demonstrate PDF export
        demo_pdf_export()
        
        print("\n" + "="*60)
        print("✓ All demonstrations completed successfully!")
        print("="*60)
        print("\nGenerated files:")
        print("  - demo_all_products.csv")
        print("  - demo_custom_fields.csv")
        print("  - demo_top3.csv")
        print("  - demo_comprehensive_report.pdf")
        print("  - demo_no_charts.pdf")
        print("  - demo_top3_comparison.pdf")
        print("\nYou can now open these files to see the results!")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
