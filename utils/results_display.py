"""
Results Display Module
Renders price comparison results in a table format with highlighting and pagination.
"""


def render_table_cli(results, page=1, items_per_page=10):
    """
    Renders results in a CLI table format with pagination.
    
    Args:
        results (list): List of dictionaries with keys: site, title, price, rating, availability, link
        page (int): Current page number (1-indexed)
        items_per_page (int): Number of items to display per page
        
    Returns:
        str: Formatted table string
    """
    if not results:
        return "No results to display."
    
    # Find the cheapest item
    cheapest_idx = find_cheapest_item(results)
    
    # Calculate pagination
    total_items = len(results)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get page results
    page_results = results[start_idx:end_idx]
    
    # Table header
    output = []
    output.append("=" * 150)
    output.append("PRICE COMPARISON RESULTS")
    output.append("=" * 150)
    
    # Column headers
    header = f"{'#':<4} {'Site':<15} {'Title':<30} {'Price':<12} {'Rating':<8} {'Availability':<15} {'Link':<30}"
    output.append(header)
    output.append("-" * 150)
    
    # Rows
    for i, item in enumerate(page_results):
        global_idx = start_idx + i
        row_num = global_idx + 1
        
        # Truncate long strings
        site = str(item.get('site', 'N/A'))[:14]
        title = str(item.get('title', 'N/A'))[:29]
        price = str(item.get('price', 'N/A'))[:11]
        rating = str(item.get('rating', 'N/A'))[:7]
        availability = str(item.get('availability', 'N/A'))[:14]
        link = str(item.get('link', 'N/A'))[:29]
        
        row = f"{row_num:<4} {site:<15} {title:<30} {price:<12} {rating:<8} {availability:<15} {link:<30}"
        
        # Highlight cheapest item
        if global_idx == cheapest_idx:
            output.append(">>> " + row + " <<<  ** CHEAPEST **")
        else:
            output.append("    " + row)
    
    output.append("-" * 150)
    output.append(f"Page {page} of {total_pages} | Showing {start_idx + 1}-{end_idx} of {total_items} results")
    output.append("=" * 150)
    
    return "\n".join(output)


def find_cheapest_item(results):
    """
    Finds the index of the item with the lowest price.
    
    Args:
        results (list): List of result dictionaries
        
    Returns:
        int: Index of the cheapest item, or -1 if no valid prices
    """
    if not results:
        return -1
    
    cheapest_idx = -1
    cheapest_price = float('inf')
    
    for i, item in enumerate(results):
        price_str = str(item.get('price', ''))
        
        # Extract numeric value from price string
        try:
            # Remove currency symbols, commas, and whitespace
            # Keep only digits and decimal point
            import re
            price_clean = re.sub(r'[^\d.]', '', price_str)
            
            if price_clean and price_clean != '.':
                price_value = float(price_clean)
                if price_value > 0 and price_value < cheapest_price:
                    cheapest_price = price_value
                    cheapest_idx = i
        except (ValueError, AttributeError):
            continue
    
    return cheapest_idx


def format_results_for_display(results):
    """
    Validates and formats results data for display.
    
    Args:
        results (list): List of result dictionaries
        
    Returns:
        list: Formatted results ready for display
    """
    formatted = []
    
    for item in results:
        formatted_item = {
            'site': item.get('site', 'Unknown'),
            'title': item.get('title', 'No Title'),
            'price': item.get('price', 'N/A'),
            'rating': item.get('rating', 'N/A'),
            'availability': item.get('availability', 'Unknown'),
            'link': item.get('link', '#')
        }
        formatted.append(formatted_item)
    
    return formatted


def paginate_results(results, page=1, items_per_page=10):
    """
    Paginates results and returns page information.
    
    Args:
        results (list): List of result dictionaries
        page (int): Current page number (1-indexed)
        items_per_page (int): Number of items per page
        
    Returns:
        dict: Contains page_results, total_pages, has_next, has_prev
    """
    total_items = len(results)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    page_results = results[start_idx:end_idx]
    
    return {
        'page_results': page_results,
        'current_page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'start_idx': start_idx,
        'end_idx': end_idx,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }
