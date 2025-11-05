"""
Streamlit Web Interface for User Input
Provides a minimal web interface with a search bar for product name or URL input.
"""

import streamlit as st
from utils.input_handler import validate_input


def main():
    """
    Main function for Streamlit web interface.
    Creates a search bar and handles user input submission.
    """
    # Page configuration
    st.set_page_config(
        page_title="Price Comparison Tool - Input",
        page_icon="🔍",
        layout="centered"
    )
    
    # Title and description
    st.title("🔍 Web Scraper Price Comparison Tool")
    st.markdown("---")
    st.subheader("Enter Product Information")
    st.markdown("Enter either a **product name** or a **product URL** to begin.")
    
    # Initialize session state for storing results
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    # Create input form
    with st.form(key='input_form'):
        st.markdown("#### Search Input")
        user_input = st.text_input(
            label="Product Name or URL",
            placeholder="e.g., 'iPhone 15 Pro' or 'https://example.com/product'",
            help="Enter a product name to search or paste a direct product URL",
            key='search_input'
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            label="Submit",
            type="primary",
            use_container_width=True
        )
        
        # Handle form submission
        if submit_button:
            if user_input:
                # Validate the input
                result = validate_input(user_input)
                st.session_state.last_result = result
            else:
                st.session_state.last_result = {
                    'valid': False,
                    'type': None,
                    'value': None
                }
    
    # Display results if available
    if st.session_state.last_result is not None:
        st.markdown("---")
        result = st.session_state.last_result
        
        if result['valid']:
            st.success("✓ Valid input received!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Input Type", value=result['type'].replace('_', ' ').title())
            with col2:
                st.metric(label="Status", value="Valid")
            
            st.info(f"**Input Value:** {result['value']}")
            
            # Display the result in a code block for easy copying
            st.code(result['value'], language=None)
            
        else:
            st.error("✗ Invalid input!")
            st.warning("Please enter a valid product name (at least 2 characters) or a valid URL.")
    
    # Instructions section
    st.markdown("---")
    with st.expander("ℹ️ Input Guidelines"):
        st.markdown("""
        **Valid Product Name Examples:**
        - iPhone 15 Pro
        - Samsung Galaxy S24
        - Sony WH-1000XM5 Headphones
        
        **Valid URL Examples:**
        - https://www.amazon.com/product/12345
        - https://www.flipkart.com/item/xyz
        - http://example.com/products/abc
        
        **Requirements:**
        - Product names must be at least 2 characters long
        - URLs must start with http:// or https://
        - URLs must have a valid domain
        """)


if __name__ == '__main__':
    main()
