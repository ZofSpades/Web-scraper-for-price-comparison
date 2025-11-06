"""
Flask web application with export functionality and database integration
Provides web interface for scraper with CSV/PDF export buttons and search history
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from datetime import datetime
import io
import time
import os
import tempfile
from typing import List, Dict, Any
from utils.export_utils import CSVExporter, PDFExporter
from scrapers.scraper_manager import scraper_manager
from database.database import create_sqlite_db


app = Flask(__name__, template_folder='../templates')
# Use environment variable for secret key, fallback to dev key for development only
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-only-change-in-production')

# Initialize exporters
csv_exporter = CSVExporter()
pdf_exporter = PDFExporter()

# Initialize database
db = create_sqlite_db('scraper_history.db', schema_file='database/schema_sqlite.sql')

# Store current search context
current_search_id = None
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
    global current_results, current_search_id
    
    query = request.form.get('query', '')
    sites = request.form.getlist('sites')
    
    if not query:
        flash('Please enter a search query', 'error')
        return redirect(url_for('index'))
    
    # Create search record in database
    current_search_id = db.create_search(query=query, status='in_progress')
    start_time = time.time()
    
    try:
        # Log search attempt
        print(f"[SEARCH] Query: {query}, Sites: {sites}, Search ID: {current_search_id}")
        
        # Perform real-time scraping
        current_results = scraper_manager.search_product(query, sites if sites else None)
        
        print(f"[SEARCH] Results count: {len(current_results)}")
        
        # Save results to database
        if current_results:
            db.add_results_batch(current_search_id, current_results)
        
        # Update search with completion status
        duration_ms = int((time.time() - start_time) * 1000)
        db.update_search(
            search_id=current_search_id,
            total_results=len(current_results),
            status='completed',
            duration_ms=duration_ms
        )
        
        # Add metadata
        db.add_metadata(current_search_id, 'source', 'web_ui')
        if sites:
            db.add_metadata(current_search_id, 'sites_filter', ','.join(sites))
        
        if not current_results:
            flash('No results found. The scrapers may be blocked or the product was not found. Try a simpler search term like "iPhone 15".', 'warning')
            return redirect(url_for('index'))
        
        return render_template('results.html', 
                             results=current_results, 
                             query=query,
                             search_id=current_search_id,
                             total=len(current_results))
    except Exception as e:
        # Update search with error status
        duration_ms = int((time.time() - start_time) * 1000)
        db.update_search(
            search_id=current_search_id,
            total_results=0,
            status='failed',
            duration_ms=duration_ms
        )
        db.add_metadata(current_search_id, 'error', str(e))
        
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
    global current_results, current_search_id
    
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
    
    # Record export in database
    if current_search_id:
        db.record_export(
            search_id=current_search_id,
            export_format='csv',
            result_count=len(export_data),
            file_path=f'/exports/{filename}'
        )
    
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    """Export current results to PDF"""
    global current_results, current_search_id
    
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
    
    # Generate PDF using temporary file with cross-platform compatibility
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create temporary file that works on both Windows and Unix
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        pdf_exporter.generate_report(export_data, filename=temp_filename)
        
        # Read the file into memory
        with open(temp_filename, 'rb') as f:
            pdf_bytes = io.BytesIO(f.read())
    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    
    filename = f"price_comparison_report_{timestamp}.pdf"
    
    # Record export in database
    if current_search_id:
        db.record_export(
            search_id=current_search_id,
            export_format='pdf',
            result_count=len(export_data),
            file_path=f'/exports/{filename}'
        )
    
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


@app.route('/history')
def history():
    """View search history"""
    limit = request.args.get('limit', 50, type=int)
    recent_searches = db.get_recent_searches(limit=limit)
    
    return render_template('history.html', searches=recent_searches)


@app.route('/statistics')
def statistics():
    """View statistics and analytics"""
    days = request.args.get('days', 30, type=int)
    
    stats = db.get_search_statistics(days=days)
    popular = db.get_popular_queries(limit=10)
    sites = db.get_site_performance()
    
    return render_template('statistics.html',
                         stats=stats,
                         popular=popular,
                         sites=sites,
                         days=days)


@app.route('/search/<int:search_id>')
def view_search(search_id):
    """View a specific search and its results"""
    search = db.get_search_by_id(search_id)
    
    if not search:
        flash('Search not found', 'error')
        return redirect(url_for('history'))
    
    results = db.get_results_by_search_id(search_id)
    metadata = db.get_metadata(search_id)
    exports = db.get_export_history(search_id)
    
    return render_template('search_detail.html',
                         search=search,
                         results=results,
                         metadata=metadata,
                         exports=exports)


@app.route('/export/csv/<int:search_id>', methods=['POST'])
def export_search_csv(search_id):
    """Export a specific search's results to CSV"""
    # Get results from database
    results = db.get_results_by_search_id(search_id)
    
    if not results:
        flash('No results found for this search', 'error')
        return redirect(url_for('view_search', search_id=search_id))
    
    # Convert database results to export format
    export_data = [
        {
            'product_name': r['product_name'],
            'price': r['price'],
            'original_price': r['original_price'],
            'discount_percentage': r['discount_percentage'],
            'rating': r['rating'],
            'reviews_count': r['reviews_count'],
            'availability': r['availability'],
            'seller': r['seller'],
            'url': r['product_url'],
            'site': r['site_name'],
            'scraped_at': r['scraped_at']
        }
        for r in results
    ]
    
    # Generate CSV
    csv_string = csv_exporter.export_to_csv_string(export_data)
    csv_bytes = io.BytesIO(csv_string.encode('utf-8'))
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_{search_id}_{timestamp}.csv"
    
    # Record export
    db.record_export(
        search_id=search_id,
        export_format='csv',
        result_count=len(export_data),
        file_path=f'/exports/{filename}'
    )
    
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/statistics')
def api_statistics():
    """API endpoint for search statistics"""
    days = request.args.get('days', 30, type=int)
    
    stats = db.get_search_statistics(days=days)
    popular = db.get_popular_queries(limit=10)
    sites = db.get_site_performance()
    
    return jsonify({
        'statistics': stats,
        'popular_queries': popular,
        'site_performance': sites
    })


@app.route('/api/search/history')
def api_search_history():
    """API endpoint for search history"""
    limit = request.args.get('limit', 20, type=int)
    query_filter = request.args.get('query')
    
    if query_filter:
        searches = db.search_by_query(f'%{query_filter}%')
    else:
        searches = db.get_recent_searches(limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(searches),
        'searches': searches
    })


@app.route('/api/search/<int:search_id>/results')
def api_search_results(search_id):
    """API endpoint to get results for a specific search"""
    # Optional date filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        results = db.get_results_by_search_and_date(search_id, start_date, end_date)
    else:
        results = db.get_results_by_search_id(search_id)
    
    return jsonify({
        'success': True,
        'search_id': search_id,
        'count': len(results),
        'results': results
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
