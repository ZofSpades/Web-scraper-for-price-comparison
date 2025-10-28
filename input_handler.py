"""
User Input Handler Module
Provides functions for handling user input via CLI and web interfaces
with validation for URLs vs product names.
"""

import re
from urllib.parse import urlparse


def is_valid_url(input_string):
    """
    Validates if the input string is a valid URL.
    
    Args:
        input_string (str): The input string to validate
        
    Returns:
        bool: True if the input is a valid URL, False otherwise
    """
    if not input_string or not isinstance(input_string, str):
        return False
    
    # Remove leading/trailing whitespace
    input_string = input_string.strip()
    
    # Basic URL pattern check
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    # Check if it matches the URL pattern
    if url_pattern.match(input_string):
        try:
            result = urlparse(input_string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    return False


def validate_input(input_string):
    """
    Validates and categorizes the input as either a URL or a product name.
    
    Args:
        input_string (str): The input string to validate
        
    Returns:
        dict: A dictionary containing:
            - 'type': 'url' or 'product_name'
            - 'value': The validated input value
            - 'valid': Boolean indicating if input is valid
    """
    if not input_string or not isinstance(input_string, str):
        return {
            'type': None,
            'value': None,
            'valid': False
        }
    
    # Remove leading/trailing whitespace
    input_string = input_string.strip()
    
    # Check if input is empty after stripping
    if not input_string:
        return {
            'type': None,
            'value': None,
            'valid': False
        }
    
    # Check if it's a valid URL
    if is_valid_url(input_string):
        return {
            'type': 'url',
            'value': input_string,
            'valid': True
        }
    else:
        # Treat as product name
        # Basic validation: at least 2 characters
        if len(input_string) >= 2:
            return {
                'type': 'product_name',
                'value': input_string,
                'valid': True
            }
        else:
            return {
                'type': 'product_name',
                'value': input_string,
                'valid': False
            }


def cli_input_prompt():
    """
    Command-line interface for user input.
    Prompts the user to enter either a product name or a URL.
    Performs validation and returns the input value only.
    
    Returns:
        dict: A dictionary containing the validated input information:
            - 'type': 'url' or 'product_name'
            - 'value': The user input
            - 'valid': Boolean indicating if input is valid
    """
    print("=" * 60)
    print("Web Scraper Price Comparison Tool - Input")
    print("=" * 60)
    print("\nPlease enter one of the following:")
    print("  1. A product name (e.g., 'iPhone 15 Pro')")
    print("  2. A product URL (e.g., 'https://example.com/product')")
    print("\nType 'quit' or 'exit' to close the program.")
    print("-" * 60)
    
    while True:
        user_input = input("\nEnter product name or URL: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit']:
            print("\nExiting the program. Goodbye!")
            return {
                'type': 'exit',
                'value': None,
                'valid': True
            }
        
        # Validate the input
        result = validate_input(user_input)
        
        if result['valid']:
            print(f"\n✓ Valid input detected!")
            print(f"  Type: {result['type'].replace('_', ' ').title()}")
            print(f"  Value: {result['value']}")
            return result
        else:
            print("\n✗ Invalid input! Please enter a valid product name (at least 2 characters) or URL.")
            print("  Try again or type 'quit' to exit.")


def get_cli_input():
    """
    Simplified CLI input function that returns only the validated input value.
    
    Returns:
        str or None: The validated input string, or None if invalid/exit
    """
    result = cli_input_prompt()
    
    if result['valid'] and result['type'] != 'exit':
        return result['value']
    
    return None
