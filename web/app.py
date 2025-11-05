"""
Flask web application with export functionality
Provides web interface for scraper with CSV/PDF export buttons
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from datetime import datetime
import io
import json
from typing import List, Dict, Any
from utils.export_utils import CSVExporter, PDFExporter
from scrapers.scraper_manager import scraper_manager


app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your-secret-key-change-this'  # Change in production

# Initialize exporters
csv_exporter = CSVExporter()
pdf_exporter = PDFExporter()

# Store results in session (in production, use database or cache)
current_results = []


@app.route('/')
def index():
    """Home page with search form"""
    return render_template('index.html')


@app.route('/submit_input', methods=['POST'])
def submit_input():
    """Handle input validation from search form (for compatibility with index.html template)"""
    from utils.input_handler import validate_input
    
    # Get input from form
    user_input = request.form.get('search_input', '').strip()
    
    # Validate the input
    result = validate_input(user_input)
    
    if result['valid']:
        return jsonify({
            'success': True,
            'message': f"Valid {result['type'].replace('_', ' ')} received!",
            'type': result['type'],
            'value': result['value']
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid input. Please enter a valid product name or URL.',
            'type': None,
            'value': None
        }), 400


@app.route('/search', methods=['POST'])
def search():
    """Handle search request and display results with real-time scraping"""
    global current_results
    
    query = request.form.get('query', '')
    sites = request.form.getlist('sites')
    
    if not query:
        flash('Please enter a search query', 'error')
        return redirect(url_for('index'))
    
    try:
        # Log search attempt
        print(f"[SEARCH] Query: {query}, Sites: {sites}")
        
        # Perform real-time scraping
        current_results = scraper_manager.search_product(query, sites if sites else None)
        
        print(f"[SEARCH] Results count: {len(current_results)}")
        print(f"[SEARCH] Results: {current_results}")
        
        if not current_results:
            flash('No results found. The scrapers may be blocked or the product was not found. Try a simpler search term like "iPhone 15".', 'warning')
            return redirect(url_for('index'))
        
        return render_template('results.html', 
                             results=current_results, 
                             query=query,
                             total=len(current_results))
    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'An error occurred while searching: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/results', methods=['GET'])
def results():
    """Display cached results (for when URL is accessed directly)"""
    global current_results
    
    query = request.args.get('q', 'recent search')
    
    if not current_results:
        flash('No results available. Please perform a new search.', 'info')
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                         results=current_results, 
                         query=query,
                         total=len(current_results))


@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for search with real-time scraping"""
    data = request.get_json()
    query = data.get('query', '')
    sites = data.get('sites', ['all'])
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        # Perform real-time scraping
        results = scraper_manager.search_product(query, sites)
        
        return jsonify({
            'success': True,
            'query': query,
            'total': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/convert', methods=['POST'])
def api_convert_currency():
    """API endpoint for currency conversion"""
    data = request.get_json()
    amount = data.get('amount', 0)
    from_currency = data.get('from', 'USD')
    to_currency = data.get('to', 'INR')
    
    try:
        result = scraper_manager.convert_price(amount, from_currency, to_currency)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/currencies', methods=['GET'])
def api_supported_currencies():
    """API endpoint to get supported currencies"""
    return jsonify({
        'currencies': scraper_manager.get_supported_currencies()
    })


@app.route('/export/csv', methods=['POST'])
def export_csv():
    """Export current results to CSV"""
    global current_results
    
    if not current_results:
        flash('No results to export', 'error')
        return redirect(url_for('index'))
    
    # Get selected indices if any
    selected = request.form.getlist('selected')
    
    if selected:
        selected_indices = [int(i) for i in selected]
        export_data = [current_results[i] for i in selected_indices if i < len(current_results)]
    else:
        export_data = current_results
    
    # Generate CSV in memory
    csv_string = csv_exporter.export_to_csv_string(export_data)
    
    # Create file-like object
    csv_bytes = io.BytesIO(csv_string.encode('utf-8'))
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"price_comparison_{timestamp}.csv"
    
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    """Export current results to PDF"""
    global current_results
    
    if not current_results:
        flash('No results to export', 'error')
        return redirect(url_for('index'))
    
    # Get selected indices if any
    selected = request.form.getlist('selected')
    
    if selected:
        selected_indices = [int(i) for i in selected]
        export_data = [current_results[i] for i in selected_indices if i < len(current_results)]
    else:
        export_data = current_results
    
    # Generate PDF in memory
    pdf_bytes = io.BytesIO()
    
    # Generate PDF (temporarily save to file, then read)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"/tmp/report_{timestamp}.pdf"
    
    pdf_exporter.generate_report(export_data, filename=temp_filename)
    
    # Read the file into memory
    with open(temp_filename, 'rb') as f:
        pdf_bytes = io.BytesIO(f.read())
    
    # Clean up temp file
    import os
    os.remove(temp_filename)
    
    filename = f"price_comparison_report_{timestamp}.pdf"
    
    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/export/csv', methods=['POST'])
def api_export_csv():
    """API endpoint for CSV export"""
    data = request.get_json()
    results = data.get('results', [])
    
    if not results:
        return jsonify({'error': 'No results provided'}), 400
    
    csv_string = csv_exporter.export_to_csv_string(results)
    
    return jsonify({
        'success': True,
        'format': 'csv',
        'data': csv_string
    })


@app.route('/api/export/pdf', methods=['POST'])
def api_export_pdf():
    """API endpoint to generate PDF (returns filename for download)"""
    data = request.get_json()
    results = data.get('results', [])
    
    if not results:
        return jsonify({'error': 'No results provided'}), 400
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.pdf"
    
    pdf_exporter.generate_report(results, filename=filename)
    
    return jsonify({
        'success': True,
        'format': 'pdf',
        'filename': filename
    })


def generate_sample_results(query: str) -> List[Dict[str, Any]]:
    """Generate sample results for demonstration"""
    return [
        {
            'product_name': f'{query} - Premium Model A',
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
            'product_name': f'{query} - Standard Edition',
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
            'product_name': f'{query} - Budget Variant',
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
            'product_name': f'{query} - Pro Version',
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
            'product_name': f'{query} - Value Pack',
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
