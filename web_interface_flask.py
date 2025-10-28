"""
Flask Web Interface for User Input
Provides a minimal web interface with a search bar for product name or URL input.
"""

from flask import Flask, render_template, request, jsonify
from input_handler import validate_input

app = Flask(__name__)


@app.route('/')
def index():
    """
    Renders the main page with the search bar input form.
    """
    return render_template('index.html')


@app.route('/submit_input', methods=['POST'])
def submit_input():
    """
    Handles form submission from the web search bar.
    Accepts either a product name or a URL and returns validation result.
    
    Returns:
        JSON response with validation results
    """
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


@app.route('/api/validate', methods=['POST'])
def validate_api():
    """
    API endpoint for input validation.
    Accepts JSON input and returns validation result.
    
    Returns:
        JSON response with validation results
    """
    data = request.get_json()
    user_input = data.get('input', '').strip()
    
    # Validate the input
    result = validate_input(user_input)
    
    return jsonify(result)


if __name__ == '__main__':
    print("Starting Flask web server...")
    print("Access the application at: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
