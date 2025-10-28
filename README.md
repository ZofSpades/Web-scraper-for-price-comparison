# Web Scraper Export Features - Implementation Guide

## Overview

This implementation adds CSV export and PDF report generation capabilities to the Web Scraper for Price Comparison project (P60).

## Features Implemented

### ✅ T1: CSV Export
- Export all or selected search results to CSV format
- Customizable field selection
- Both file download and string output support
- Automatic timestamp-based filename generation

### ✅ T2: PDF Report Generation
- Professional PDF reports with charts and tables
- Summary statistics and analytics
- Best deals section highlighting top discounts
- Price comparison visualizations
- Customizable report titles and content

### ✅ T3: Export Buttons & CLI Flags
- **Web UI**: Export buttons with product selection
- **CLI**: Comprehensive command-line interface with multiple flags
- **API**: RESTful endpoints for programmatic access

## File Structure

```
web_scraper_exports/
├── export_utils.py          # Core export functionality (CSV & PDF)
├── cli.py                   # Command-line interface
├── app.py                   # Flask web application
├── requirements.txt         # Python dependencies
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Search page
│   └── results.html        # Results with export buttons
└── README.md               # This file
```

## Installation

1. **Clone or copy the files to your project directory**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -c "import reportlab; import flask; print('Dependencies OK')"
   ```

## Usage

### Web Interface

1. **Start the Flask application:**
   ```bash
   python app.py
   ```

2. **Open browser:**
   - Navigate to `http://localhost:5000`
   - Enter search query and select sites
   - View results and select products
   - Click "Export CSV" or "Export PDF" buttons

3. **Export options:**
   - **Export All**: Click export button without selecting any products
   - **Export Selected**: Check product checkboxes, then click export button

### Command-Line Interface

1. **Basic search with CSV export:**
   ```bash
   python cli.py --search "laptop" --export-csv
   ```

2. **Generate PDF report:**
   ```bash
   python cli.py --search "smartphone" --export-pdf
   ```

3. **Export both formats with custom filenames:**
   ```bash
   python cli.py --search "headphones" \
       --export-csv my_results.csv \
       --export-pdf my_report.pdf
   ```

4. **Custom CSV fields:**
   ```bash
   python cli.py --search "tablet" \
       --export-csv \
       --csv-fields product_name price rating seller
   ```

5. **PDF without charts:**
   ```bash
   python cli.py --search "camera" \
       --export-pdf --no-charts
   ```

6. **Export selected products only:**
   ```bash
   python cli.py --search "watch" \
       --export-csv \
       --select 0 1 2  # Export first 3 products
   ```

7. **Load from JSON and export:**
   ```bash
   python cli.py --input-json results.json \
       --export-pdf report.pdf
   ```

### Programmatic Usage (Python)

```python
from export_utils import CSVExporter, PDFExporter

# Sample product data
results = [
    {
        'product_name': 'Laptop ABC',
        'price': 45999.00,
        'original_price': 54999.00,
        'discount_percentage': 16,
        'rating': 4.5,
        'reviews_count': 1234,
        'availability': 'In Stock',
        'seller': 'Amazon',
        'url': 'https://amazon.in/product1',
        'scraped_at': '2025-10-28T10:30:00'
    },
    # ... more products
]

# CSV Export
csv_exporter = CSVExporter()
csv_exporter.export_to_csv(results, 'output.csv')

# PDF Export
pdf_exporter = PDFExporter()
pdf_exporter.generate_report(results, 'report.pdf', 
                            title='My Price Comparison Report')

# Export selected products
selected_indices = [0, 2, 4]  # Export 1st, 3rd, 5th products
csv_exporter.export_selected_products(results, selected_indices, 'selected.csv')
```

## API Endpoints

### POST /api/search
Search for products and return JSON results.

**Request:**
```json
{
  "query": "laptop",
  "sites": ["amazon", "flipkart"]
}
```

**Response:**
```json
{
  "success": true,
  "query": "laptop",
  "total": 5,
  "results": [...]
}
```

### POST /api/export/csv
Export results to CSV format.

**Request:**
```json
{
  "results": [...]
}
```

**Response:**
```json
{
  "success": true,
  "format": "csv",
  "data": "product_name,price,rating,..."
}
```

### POST /api/export/pdf
Generate PDF report.

**Request:**
```json
{
  "results": [...]
}
```

**Response:**
```json
{
  "success": true,
  "format": "pdf",
  "filename": "report_20251028_103000.pdf"
}
```

## CSV Export Features

- **Default Fields:**
  - product_name
  - price
  - original_price
  - discount_percentage
  - rating
  - reviews_count
  - availability
  - seller
  - url
  - scraped_at

- **Custom Field Selection**: Specify only the fields you need
- **UTF-8 Encoding**: Supports international characters
- **Automatic Headers**: Column names included automatically

## PDF Report Features

- **Summary Statistics:**
  - Average, minimum, and maximum prices
  - Average rating
  - Discount statistics

- **Product Comparison Table:**
  - Up to 20 products in detailed table
  - Sortable and formatted data

- **Visual Analytics:**
  - Price distribution bar chart
  - Top 10 products comparison

- **Best Deals Section:**
  - Top 5 products by discount percentage
  - Highlighted for quick reference

- **Professional Formatting:**
  - Custom color scheme
  - Headers and footers
  - Page breaks for readability

## Integration with Existing Scraper

To integrate these export features with your existing web scraper:

1. **Import the exporters:**
   ```python
   from export_utils import CSVExporter, PDFExporter
   ```

2. **After scraping, pass results to exporters:**
   ```python
   # Your scraper code
   scraper_results = scrape_products(query)
   
   # Export to CSV
   csv_exporter = CSVExporter()
   csv_exporter.export_to_csv(scraper_results, 'results.csv')
   
   # Generate PDF report
   pdf_exporter = PDFExporter()
   pdf_exporter.generate_report(scraper_results, 'report.pdf')
   ```

3. **In Flask routes:**
   - Replace `generate_sample_results()` with your actual scraper function
   - The export routes are already set up and ready to use

4. **In CLI:**
   - Replace the `_generate_sample_data()` method with your scraper call
   - All export flags will work automatically

## CLI Options Reference

```
Search Options:
  --search, -s          Product search query
  --sites              Sites to scrape (amazon, flipkart, snapdeal, all)
  --max-results        Maximum results per site (default: 50)
  --min-rating         Minimum product rating (default: 0.0)

Export Options:
  --export-csv         Export to CSV file
  --export-pdf         Export to PDF report
  --csv-fields         Specific CSV fields to include
  --include-charts     Include charts in PDF (default: True)
  --no-charts          Exclude charts from PDF

Selection Options:
  --select            Export only selected product indices

Input/Output Options:
  --input-json        Load results from JSON file
  --output-json       Save results to JSON file

Display Options:
  --quiet, -q         Suppress output messages
  --verbose, -v       Verbose output
  --sort-by           Sort by: price, rating, discount, name
```

## Examples

### Web UI Screenshots

1. **Search Page** - Enter product name and select sites
2. **Results Page** - View products with selection checkboxes
3. **Export Buttons** - CSV and PDF export buttons at top

### CLI Examples

**Example 1: Quick search and export**
```bash
python cli.py --search "gaming laptop" --export-csv --export-pdf
```

**Example 2: Specific sites and custom fields**
```bash
python cli.py --search "iPhone 15" \
    --sites amazon flipkart \
    --export-csv phones.csv \
    --csv-fields product_name price seller rating
```

**Example 3: Load, filter, and export**
```bash
python cli.py --input-json all_results.json \
    --select 0 1 2 3 4 \
    --export-pdf top5.pdf \
    --include-charts
```

## Testing

Run the demonstration:

```bash
# Test CLI
python cli.py --search "test product" --export-csv test.csv --export-pdf test.pdf

# Test Web UI
python app.py
# Then visit http://localhost:5000 in browser
```

## Customization

### Custom PDF Styling

Edit `export_utils.py` - `PDFExporter._setup_custom_styles()`:

```python
def _setup_custom_styles(self):
    # Modify colors, fonts, sizes here
    self.styles.add(ParagraphStyle(
        name='CustomTitle',
        fontSize=28,  # Change title size
        textColor=colors.blue,  # Change color
        # ... more customizations
    ))
```

### Custom CSV Fields

Modify `CSVExporter.default_fields` to change default columns:

```python
self.default_fields = [
    'product_name',
    'price',
    'rating',
    'seller',
    # Add or remove fields as needed
]
```

## Troubleshooting

**Issue: reportlab import error**
```bash
pip install --upgrade reportlab
```

**Issue: Flask not found**
```bash
pip install Flask
```

**Issue: PDF charts not showing**
- Ensure `include_charts=True` in PDF generation
- Check that products have valid price data

**Issue: CSV encoding problems**
- Files are saved as UTF-8
- Open in Excel using "Import Data" feature

## Future Enhancements

Potential improvements:
- Excel export (.xlsx) with formatting
- Email report delivery
- Scheduled automatic reports
- Comparison charts between multiple products
- Historical price tracking in reports
- Multi-language support in PDFs

## Credits

**Team 5 - Web Scraper for Price Comparison**
- Project P60
- Course: UE23CS341A
- PES University
- Academic Year: 2025

## License

This project is developed for educational purposes as part of the PES University curriculum.

---

For questions or issues, please contact the development team.
