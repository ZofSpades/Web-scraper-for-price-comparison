# Quick Start Guide - Export Features

## Installation & Setup (2 minutes)

1. **Install dependencies:**
   ```bash
   cd /home/geckbags/Programs/SE/web_scraper_exports
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python demo.py
   ```
   This will create sample CSV and PDF files to verify everything works.

## Quick Usage Examples

### 1. Command Line (Fastest)

```bash
# Search and export to CSV
python cli.py --search "laptop" --export-csv

# Search and generate PDF report
python cli.py --search "smartphone" --export-pdf

# Both formats at once
python cli.py --search "headphones" --export-csv --export-pdf
```

### 2. Web Interface (Most User-Friendly)

```bash
# Start the web server
python app.py

# Open browser to: http://localhost:5000
# - Enter search term
# - Select products (optional)
# - Click "Export CSV" or "Export PDF"
```

### 3. Python Code (Most Flexible)

```python
from export_utils import CSVExporter, PDFExporter

# Your product data
products = [
    {
        'product_name': 'Product A',
        'price': 999.00,
        'rating': 4.5,
        'seller': 'Amazon',
        # ... more fields
    }
]

# Export to CSV
CSVExporter().export_to_csv(products, 'output.csv')

# Generate PDF report
PDFExporter().generate_report(products, 'report.pdf')
```

## Testing the Demo

Run the demonstration script to see all features:

```bash
python demo.py
```

This creates 6 example files:
- 3 CSV files (all products, custom fields, selected products)
- 3 PDF reports (comprehensive, no charts, comparison)

## CLI Cheat Sheet

```bash
# Basic search
python cli.py --search "product name"

# Export CSV with custom fields
python cli.py --search "laptop" --export-csv --csv-fields product_name price rating

# Export PDF without charts
python cli.py --search "phone" --export-pdf --no-charts

# Export selected products (indices 0, 1, 2)
python cli.py --search "tablet" --select 0 1 2 --export-csv

# Verbose output
python cli.py --search "watch" --export-pdf --verbose

# Quiet mode
python cli.py --search "camera" --export-csv --quiet
```

## Integration Steps

To integrate with your existing web scraper:

1. **Copy these files to your project:**
   - `export_utils.py` (core functionality)
   - `requirements.txt` (add to your existing file)

2. **In your scraper code:**
   ```python
   from export_utils import CSVExporter, PDFExporter
   
   # After scraping
   results = your_scraper.scrape(query)
   
   # Export
   CSVExporter().export_to_csv(results, 'results.csv')
   PDFExporter().generate_report(results, 'report.pdf')
   ```

3. **For Flask integration:**
   - Copy routes from `app.py` to your Flask app
   - Copy templates to your `templates/` directory
   - Add export buttons to your results page

## Common Issues

**Problem: reportlab not found**
```bash
pip install reportlab
```

**Problem: Flask not found**
```bash
pip install Flask
```

**Problem: Permission denied**
```bash
# Make sure you have write permissions in current directory
cd ~/Documents
python path/to/cli.py --search "test" --export-csv
```

## Next Steps

1. ✅ Run `python demo.py` to verify everything works
2. ✅ Try CLI: `python cli.py --search "laptop" --export-csv --export-pdf`
3. ✅ Try Web UI: `python app.py` then visit http://localhost:5000
4. ✅ Read full documentation in README.md
5. ✅ Integrate with your web scraper code

## Support

For detailed documentation, see README.md
For code examples, see demo.py

---

**Project:** Web Scraper for Price Comparison (P60)
**Team:** Team 5
**Course:** UE23CS341A - PES University
