"""
Flask Web Interface for Results Display
Displays price comparison results in a web table with highlighting and pagination.
"""

from flask import Flask, render_template, request, jsonify
from utils.results_display import find_cheapest_item, paginate_results

app = Flask(__name__, template_folder='../templates')

# Sample data for demonstration (in real app, this would come from scraping)
SAMPLE_RESULTS = [
    {'site': 'Amazon', 'title': 'iPhone 15 Pro 128GB', 'price': '$999.00', 'rating': '4.5', 'availability': 'In Stock', 'link': 'https://amazon.com/item1'},
    {'site': 'BestBuy', 'title': 'iPhone 15 Pro 128GB', 'price': '$989.99', 'rating': '4.7', 'availability': 'In Stock', 'link': 'https://bestbuy.com/item1'},
    {'site': 'Walmart', 'title': 'iPhone 15 Pro 128GB', 'price': '$995.00', 'rating': '4.3', 'availability': 'Limited Stock', 'link': 'https://walmart.com/item1'},
    {'site': 'Target', 'title': 'iPhone 15 Pro 128GB', 'price': '$999.00', 'rating': '4.6', 'availability': 'In Stock', 'link': 'https://target.com/item1'},
    {'site': 'eBay', 'title': 'iPhone 15 Pro 128GB', 'price': '$979.00', 'rating': '4.2', 'availability': 'In Stock', 'link': 'https://ebay.com/item1'},
    {'site': 'Newegg', 'title': 'iPhone 15 Pro 128GB', 'price': '$1,005.00', 'rating': '4.4', 'availability': 'In Stock', 'link': 'https://newegg.com/item1'},
    {'site': 'B&H Photo', 'title': 'iPhone 15 Pro 128GB', 'price': '$999.99', 'rating': '4.8', 'availability': 'In Stock', 'link': 'https://bhphoto.com/item1'},
    {'site': 'Costco', 'title': 'iPhone 15 Pro 128GB', 'price': '$985.00', 'rating': '4.7', 'availability': 'Members Only', 'link': 'https://costco.com/item1'},
    {'site': 'Apple Store', 'title': 'iPhone 15 Pro 128GB', 'price': '$999.00', 'rating': '4.9', 'availability': 'In Stock', 'link': 'https://apple.com/item1'},
    {'site': 'Samsung', 'title': 'iPhone 15 Pro 128GB', 'price': '$999.00', 'rating': '4.5', 'availability': 'In Stock', 'link': 'https://samsung.com/item1'},
    {'site': 'Microsoft', 'title': 'iPhone 15 Pro 128GB', 'price': '$999.00', 'rating': '4.6', 'availability': 'In Stock', 'link': 'https://microsoft.com/item1'},
    {'site': 'GameStop', 'title': 'iPhone 15 Pro 128GB', 'price': '$1,010.00', 'rating': '4.1', 'availability': 'In Stock', 'link': 'https://gamestop.com/item1'},
]


@app.route('/results')
def show_results():
    """
    Renders the results page with pagination.
    """
    page = request.args.get('page', 1, type=int)
    items_per_page = request.args.get('per_page', 10, type=int)
    
    # Get pagination info
    pagination = paginate_results(SAMPLE_RESULTS, page, items_per_page)
    
    # Find cheapest item index in full results
    cheapest_idx = find_cheapest_item(SAMPLE_RESULTS)
    
    return render_template(
        'results.html',
        results=pagination['page_results'],
        cheapest_idx=cheapest_idx,
        start_idx=pagination['start_idx'],
        pagination=pagination
    )


@app.route('/api/results')
def api_results():
    """
    API endpoint to get results as JSON with pagination.
    """
    page = request.args.get('page', 1, type=int)
    items_per_page = request.args.get('per_page', 10, type=int)
    
    pagination = paginate_results(SAMPLE_RESULTS, page, items_per_page)
    cheapest_idx = find_cheapest_item(SAMPLE_RESULTS)
    
    return jsonify({
        'results': pagination['page_results'],
        'cheapest_idx': cheapest_idx,
        'pagination': {
            'current_page': pagination['current_page'],
            'total_pages': pagination['total_pages'],
            'total_items': pagination['total_items'],
            'has_next': pagination['has_next'],
            'has_prev': pagination['has_prev']
        }
    })


if __name__ == '__main__':
    print("Starting Flask results display server...")
    print("Access the results at: http://127.0.0.1:5000/results")
    app.run(debug=True, host='0.0.0.0', port=5000)
