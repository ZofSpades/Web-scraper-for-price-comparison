"""
Example: Flask app integration with database
This shows how to integrate the database layer into the existing app.py
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from datetime import datetime
import io
import time
from typing import List, Dict, Any
from export_utils import CSVExporter, PDFExporter
from database import create_sqlite_db

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Initialize exporters
csv_exporter = CSVExporter()
pdf_exporter = PDFExporter()

# Initialize database
db = create_sqlite_db('scraper_history.db')

# Track current search for the session
current_search_id = None
current_results = []


@app.route('/')
def index():
    """Home page with search form"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle search request and display results with database tracking"""
    global current_search_id, current_results
    
    query = request.form.get('query', '')
    sites = request.form.getlist('sites')
    
    if not query:
        flash('Please enter a search query', 'error')
        return redirect(url_for('index'))
    
    # Create search record in database
    current_search_id = db.create_search(query=query, status='in_progress')
    start_time = time.time()
    
    try:
        # In production, call actual scraper here
        # For demo, generate sample data
        current_results = generate_sample_results(query)
        
        # Save results to database
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
        flash(f'Search failed: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/history')
def history():
    """View search history"""
    limit = request.args.get('limit', 50, type=int)
    recent_searches = db.get_recent_searches(limit=limit)
    
    return render_template('history.html', searches=recent_searches)


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


@app.route('/export/csv', methods=['POST'])
def export_csv():
    """Export current results to CSV and track in database"""
    global current_search_id, current_results
    
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
    
    # Generate CSV
    csv_string = csv_exporter.export_to_csv_string(export_data)
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
    """
    Generate sample results for demo
    In production, replace with actual scraping
    """
    import random
    
    sites = ['Amazon', 'eBay', 'Walmart', 'BestBuy', 'Target']
    
    results = []
    for i in range(random.randint(5, 15)):
        price = round(random.uniform(50, 1500), 2)
        original_price = round(price * random.uniform(1.1, 1.5), 2)
        discount = round(((original_price - price) / original_price) * 100, 2)
        
        result = {
            'product_name': f'{query.title()} Product {i+1}',
            'price': price,
            'original_price': original_price,
            'discount_percentage': discount,
            'rating': round(random.uniform(3.5, 5.0), 1),
            'reviews_count': random.randint(10, 1000),
            'availability': random.choice(['In Stock', 'Limited Stock', 'Out of Stock']),
            'seller': random.choice(sites),
            'site': random.choice(sites),
            'url': f'https://example.com/product/{i}',
            'image_url': f'https://example.com/images/{i}.jpg'
        }
        results.append(result)
    
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("Web Scraper with Database Integration")
    print("=" * 60)
    print(f"\nDatabase: scraper_history.db")
    print(f"Starting Flask server...\n")
    
    app.run(debug=True, port=5000)
