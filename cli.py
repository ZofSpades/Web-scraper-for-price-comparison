"""
Command-line interface for Web Scraper with export functionality
"""

import argparse
import sys
import json
from typing import List, Dict, Any, Optional
from export_utils import CSVExporter, PDFExporter


class ScraperCLI:
    """Command-line interface for web scraper with export options"""
    
    def __init__(self):
        self.parser = self._setup_parser()
        self.csv_exporter = CSVExporter()
        self.pdf_exporter = PDFExporter()
    
    def _setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser with all options"""
        parser = argparse.ArgumentParser(
            description='Web Scraper for Price Comparison',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic search
  python cli.py --search "laptop" --sites amazon flipkart
  
  # Search with CSV export
  python cli.py --search "smartphone" --export-csv results.csv
  
  # Search with PDF report
  python cli.py --search "headphones" --export-pdf report.pdf
  
  # Export both formats
  python cli.py --search "camera" --export-csv data.csv --export-pdf report.pdf
  
  # Specify custom fields for CSV
  python cli.py --search "watch" --export-csv --csv-fields product_name price rating
  
  # Generate PDF with charts
  python cli.py --search "tablet" --export-pdf --include-charts
            """
        )
        
        # Search options
        search_group = parser.add_argument_group('Search Options')
        search_group.add_argument(
            '--search', '-s',
            type=str,
            required=False,
            help='Product name or search query'
        )
        search_group.add_argument(
            '--sites',
            nargs='+',
            choices=['amazon', 'flipkart', 'snapdeal', 'all'],
            default=['all'],
            help='E-commerce sites to scrape (default: all)'
        )
        search_group.add_argument(
            '--max-results',
            type=int,
            default=50,
            help='Maximum number of results per site (default: 50)'
        )
        search_group.add_argument(
            '--min-rating',
            type=float,
            default=0.0,
            help='Minimum product rating filter (default: 0.0)'
        )
        
        # Export options
        export_group = parser.add_argument_group('Export Options')
        export_group.add_argument(
            '--export-csv',
            type=str,
            nargs='?',
            const='auto',
            metavar='FILENAME',
            help='Export results to CSV file (auto-generate filename if not specified)'
        )
        export_group.add_argument(
            '--export-pdf',
            type=str,
            nargs='?',
            const='auto',
            metavar='FILENAME',
            help='Export results to PDF report (auto-generate filename if not specified)'
        )
        export_group.add_argument(
            '--csv-fields',
            nargs='+',
            help='Specific fields to include in CSV export'
        )
        export_group.add_argument(
            '--include-charts',
            action='store_true',
            default=True,
            help='Include charts in PDF report (default: True)'
        )
        export_group.add_argument(
            '--no-charts',
            action='store_true',
            help='Exclude charts from PDF report'
        )
        
        # Selection options
        selection_group = parser.add_argument_group('Selection Options')
        selection_group.add_argument(
            '--select',
            nargs='+',
            type=int,
            help='Export only selected product indices (0-based)'
        )
        
        # Input/Output options
        io_group = parser.add_argument_group('Input/Output Options')
        io_group.add_argument(
            '--input-json',
            type=str,
            help='Load results from JSON file instead of scraping'
        )
        io_group.add_argument(
            '--output-json',
            type=str,
            help='Save scraping results to JSON file'
        )
        
        # Display options
        display_group = parser.add_argument_group('Display Options')
        display_group.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress output messages'
        )
        display_group.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Verbose output'
        )
        display_group.add_argument(
            '--sort-by',
            choices=['price', 'rating', 'discount', 'name'],
            default='price',
            help='Sort results by field (default: price)'
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None):
        """Run the CLI with provided arguments"""
        parsed_args = self.parser.parse_args(args)
        
        try:
            # Load or scrape results
            results = self._get_results(parsed_args)
            
            if not results:
                print("No results found.")
                return 1
            
            # Sort results
            results = self._sort_results(results, parsed_args.sort_by)
            
            # Display results if not quiet
            if not parsed_args.quiet:
                self._display_results(results, parsed_args.verbose)
            
            # Handle selection
            if parsed_args.select:
                results = self._filter_selected(results, parsed_args.select)
            
            # Export to CSV if requested
            if parsed_args.export_csv:
                self._export_csv(results, parsed_args)
            
            # Export to PDF if requested
            if parsed_args.export_pdf:
                self._export_pdf(results, parsed_args)
            
            # Save to JSON if requested
            if parsed_args.output_json:
                self._save_json(results, parsed_args.output_json)
            
            return 0
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _get_results(self, args) -> List[Dict[str, Any]]:
        """Get results either from JSON file or by scraping"""
        if args.input_json:
            # Load from JSON
            with open(args.input_json, 'r') as f:
                return json.load(f)
        else:
            # This would call the actual scraper
            # For demonstration, return sample data
            if args.search:
                print(f"Scraping for: {args.search}")
                print(f"Sites: {args.sites}")
                print(f"Max results: {args.max_results}")
                # In real implementation, call scraper here
                return self._generate_sample_data(args.search)
            else:
                raise ValueError("Either --search or --input-json must be provided")
    
    def _generate_sample_data(self, query: str) -> List[Dict[str, Any]]:
        """Generate sample data for demonstration"""
        from datetime import datetime
        
        return [
            {
                'product_name': f'{query} Model A - Premium Edition',
                'price': 29999.00,
                'original_price': 39999.00,
                'discount_percentage': 25,
                'rating': 4.5,
                'reviews_count': 1234,
                'availability': 'In Stock',
                'seller': 'Amazon',
                'url': 'https://amazon.in/product1',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'product_name': f'{query} Model B - Standard',
                'price': 19999.00,
                'original_price': 24999.00,
                'discount_percentage': 20,
                'rating': 4.2,
                'reviews_count': 856,
                'availability': 'In Stock',
                'seller': 'Flipkart',
                'url': 'https://flipkart.com/product2',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'product_name': f'{query} Model C - Budget Friendly',
                'price': 14999.00,
                'original_price': 14999.00,
                'discount_percentage': 0,
                'rating': 3.9,
                'reviews_count': 432,
                'availability': 'Limited Stock',
                'seller': 'Snapdeal',
                'url': 'https://snapdeal.com/product3',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'product_name': f'{query} Model D - Pro Version',
                'price': 45999.00,
                'original_price': 54999.00,
                'discount_percentage': 16,
                'rating': 4.8,
                'reviews_count': 2341,
                'availability': 'In Stock',
                'seller': 'Amazon',
                'url': 'https://amazon.in/product4',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'product_name': f'{query} Model E - Value Pack',
                'price': 24999.00,
                'original_price': 32999.00,
                'discount_percentage': 24,
                'rating': 4.3,
                'reviews_count': 678,
                'availability': 'In Stock',
                'seller': 'Flipkart',
                'url': 'https://flipkart.com/product5',
                'scraped_at': datetime.now().isoformat()
            },
        ]
    
    def _sort_results(self, results: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Sort results by specified field"""
        sort_key_map = {
            'price': lambda x: float(x.get('price', 0)),
            'rating': lambda x: float(x.get('rating', 0)),
            'discount': lambda x: float(x.get('discount_percentage', 0)),
            'name': lambda x: x.get('product_name', '')
        }
        
        if sort_by in sort_key_map:
            reverse = sort_by in ['rating', 'discount']  # Higher is better for these
            return sorted(results, key=sort_key_map[sort_by], reverse=reverse)
        
        return results
    
    def _display_results(self, results: List[Dict[str, Any]], verbose: bool = False):
        """Display results in console"""
        print(f"\n{'='*80}")
        print(f"Found {len(results)} products")
        print(f"{'='*80}\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('product_name', 'N/A')}")
            print(f"   Price: ₹{result.get('price', 0):.2f}", end='')
            
            if result.get('discount_percentage', 0) > 0:
                print(f" (Save {result.get('discount_percentage')}%)", end='')
            
            print(f" | Rating: {result.get('rating', 'N/A')}/5.0")
            print(f"   Seller: {result.get('seller', 'N/A')} | {result.get('availability', 'N/A')}")
            
            if verbose:
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Reviews: {result.get('reviews_count', 0)}")
            
            print()
    
    def _filter_selected(self, results: List[Dict[str, Any]], indices: List[int]) -> List[Dict[str, Any]]:
        """Filter results by selected indices"""
        return [results[i] for i in indices if i < len(results)]
    
    def _export_csv(self, results: List[Dict[str, Any]], args):
        """Export results to CSV"""
        filename = args.export_csv if args.export_csv != 'auto' else None
        fields = args.csv_fields if args.csv_fields else None
        
        output_file = self.csv_exporter.export_to_csv(results, filename, fields)
        print(f"✓ CSV exported to: {output_file}")
    
    def _export_pdf(self, results: List[Dict[str, Any]], args):
        """Export results to PDF"""
        filename = args.export_pdf if args.export_pdf != 'auto' else None
        include_charts = not args.no_charts
        
        output_file = self.pdf_exporter.generate_report(
            results, 
            filename=filename,
            include_charts=include_charts
        )
        print(f"✓ PDF report generated: {output_file}")
    
    def _save_json(self, results: List[Dict[str, Any]], filename: str):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved to: {filename}")


def main():
    """Main entry point"""
    cli = ScraperCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
