"""
Streamlit Web Interface for Results Display
Displays price comparison results in a web table with highlighting and pagination.
"""

import streamlit as st
import pandas as pd
from results_display import find_cheapest_item, paginate_results

# Sample data for demonstration
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


def highlight_cheapest_row(row, cheapest_idx, row_idx):
    """
    Apply styling to highlight the cheapest row.
    """
    if row_idx == cheapest_idx:
        return ['background-color: #d4edda; color: #155724; font-weight: bold'] * len(row)
    return [''] * len(row)


def main():
    """
    Main function for Streamlit results display.
    """
    # Page configuration
    st.set_page_config(
        page_title="Price Comparison Results",
        page_icon="🔍",
        layout="wide"
    )
    
    # Title and description
    st.title("🔍 Price Comparison Results")
    st.markdown("Compare prices across multiple retailers and find the best deal")
    st.markdown("---")
    
    # Initialize session state for pagination
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Pagination controls at top
    col1, col2, col3 = st.columns([1, 2, 1])
    
    items_per_page = 10
    pagination = paginate_results(SAMPLE_RESULTS, st.session_state.current_page, items_per_page)
    
    with col1:
        if st.button("← Previous", disabled=not pagination['has_prev']):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align: center; padding-top: 5px;'>Page {pagination['current_page']} of {pagination['total_pages']} | Showing {pagination['start_idx'] + 1}-{pagination['end_idx']} of {pagination['total_items']} results</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Next →", disabled=not pagination['has_next']):
            st.session_state.current_page += 1
            st.rerun()
    
    st.markdown("---")
    
    # Find cheapest item
    cheapest_idx = find_cheapest_item(SAMPLE_RESULTS)
    
    # Display results
    if pagination['page_results']:
        # Show cheapest item banner
        if cheapest_idx >= pagination['start_idx'] and cheapest_idx < pagination['end_idx']:
            page_cheapest_idx = cheapest_idx - pagination['start_idx']
            cheapest_item = pagination['page_results'][page_cheapest_idx]
            st.success(f"🏆 **Best Price:** {cheapest_item['site']} - {cheapest_item['price']}")
        
        # Create DataFrame
        df = pd.DataFrame(pagination['page_results'])
        
        # Apply styling
        def style_dataframe(df):
            # Find which row in this page is the cheapest
            styles = []
            for i in range(len(df)):
                global_idx = pagination['start_idx'] + i
                if global_idx == cheapest_idx:
                    styles.append(['background-color: #d4edda; color: #155724; font-weight: bold'] * len(df.columns))
                else:
                    styles.append([''] * len(df.columns))
            return styles
        
        # Display table with styling
        styled_df = df.style.apply(lambda row: style_dataframe(df)[row.name], axis=1)
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # Detailed view section
        st.markdown("---")
        st.subheader("Detailed View")
        
        selected_idx = st.selectbox(
            "Select an item to view details:",
            range(len(pagination['page_results'])),
            format_func=lambda i: f"{pagination['page_results'][i]['site']} - {pagination['page_results'][i]['price']}"
        )
        
        if selected_idx is not None:
            selected_item = pagination['page_results'][selected_idx]
            global_idx = pagination['start_idx'] + selected_idx
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Site", selected_item['site'])
                st.metric("Price", selected_item['price'])
                st.metric("Rating", f"⭐ {selected_item['rating']}")
            
            with col2:
                st.metric("Availability", selected_item['availability'])
                st.markdown(f"**Title:** {selected_item['title']}")
                st.markdown(f"**Link:** [{selected_item['link']}]({selected_item['link']})")
            
            if global_idx == cheapest_idx:
                st.success("🏆 This is the cheapest option!")
    
    else:
        st.warning("No results to display.")
    
    # Pagination controls at bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Prev", disabled=not pagination['has_prev'], key="prev_bottom"):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        # Page number selector
        page_num = st.number_input(
            "Go to page:",
            min_value=1,
            max_value=pagination['total_pages'],
            value=st.session_state.current_page,
            step=1,
            key="page_input"
        )
        if page_num != st.session_state.current_page:
            st.session_state.current_page = page_num
            st.rerun()
    
    with col3:
        if st.button("Next →", disabled=not pagination['has_next'], key="next_bottom"):
            st.session_state.current_page += 1
            st.rerun()


if __name__ == '__main__':
    main()
