"""
Real-time scraping integration
Coordinates scraping across multiple e-commerce sites with advanced pricing utilities
"""

from scrapers.scraper_registry import ScraperRegistry
from scrapers.scraper_controller import ScraperController
from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from typing import List, Dict
import concurrent.futures

# Import pricing utilities for advanced price parsing and comparison
from pricing.parser import parse_monetary, normalize_numeric_string, detect_currency
from pricing.currency import CurrencyConverter
from pricing.compare import rank_offers
from pricing.types import ProductOffer, RawPrice, ParsedMonetary
from pricing.normalize import normalize as normalize_price
from decimal import Decimal


class ScraperManager:
    """
    Manages real-time scraping from multiple e-commerce sites
    """
    
    def __init__(self):
        """Initialize scraper registry and register all scrapers"""
        self.registry = ScraperRegistry()
        self.controller = ScraperController(self.registry)
        
        # Register scrapers
        self.registry.register(AmazonScraper())
        self.registry.register(FlipkartScraper())
        
        # Initialize currency converter with INR as base
        self.currency_converter = CurrencyConverter(base_currency="INR")
    
    def search_product(self, query: str, sites: List[str] = None) -> List[Dict]:
        """
        Search for product across multiple sites
        
        Args:
            query: Product name or search query
            sites: List of site names to search (None = all sites)
            
        Returns:
            List of product results from all sites
        """
        if sites is None or 'all' in sites:
            # Search all registered sites
            results = self.controller.scrape_all(query)
        else:
            # Search specific sites
            results = []
            for site in sites:
                scraper = self.registry.get_scraper(site.lower())
                if scraper:
                    try:
                        result = scraper.scrape(query)
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'site': site,
                            'title': 'Error',
                            'price': 'N/A',
                            'rating': 'N/A',
                            'availability': 'Error',
                            'link': '#',
                            'error': str(e)
                        })
        
        return self._format_results(results)
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """
        Format results using advanced pricing utilities
        - Parse prices with multi-currency support
        - Normalize prices to common currency (INR)
        - Rank by best effective price
        """
        offers = []
        
        for result in results:
            # Skip if error occurred
            if 'error' in result and result['title'] == 'Error':
                continue
            
            try:
                # Create RawPrice object for pricing pipeline
                raw_price = RawPrice(
                    site=result.get('site', 'Unknown'),
                    price_text=result.get('price', '₹0'),
                    currency_hint='INR',  # Most Indian e-commerce sites use INR
                    title=result.get('title', 'N/A'),
                    url=result.get('link', '#'),
                    rating=self._parse_rating(result.get('rating', 'N/A')),
                    in_stock='in stock' in str(result.get('availability', '')).lower()
                )
                
                # Normalize price using pricing utilities
                normalized = normalize_price(raw_price, self.currency_converter, target_ccy='INR')
                
                # Create ProductOffer
                offer = ProductOffer(
                    site=result.get('site', 'Unknown'),
                    title=result.get('title', 'N/A'),
                    url=result.get('link', '#'),
                    normalized=normalized,
                    rating=raw_price.rating,
                    in_stock=raw_price.in_stock,
                    raw=raw_price
                )
                
                offers.append(offer)
                
            except Exception as e:
                print(f"[PRICING ERROR] Failed to process {result.get('site')}: {str(e)}")
                # Fallback to basic formatting
                price_value = self._extract_price_value(result.get('price', '0'))
                offers.append(self._create_fallback_offer(result, price_value))
        
        # Rank offers using compare.py (best price first)
        if offers:
            ranked_offers = rank_offers(offers)
        else:
            ranked_offers = []
        
        # Convert ProductOffer objects to frontend format
        formatted = []
        for offer in ranked_offers:
            formatted.append({
                'product_name': offer.title or 'N/A',
                'price': float(offer.normalized.effective.amount),
                'price_display': f"₹{offer.normalized.effective.amount:,.2f}",
                'price_breakdown': self._format_breakdown(offer.normalized),
                'rating': str(offer.rating) if offer.rating else 'N/A',
                'reviews_count': offer.reviews or 0,
                'availability': 'In Stock' if offer.in_stock else 'Out of Stock',
                'seller': offer.site,
                'url': offer.url or '#',
                'scraped_at': self._get_timestamp(),
                'currency': offer.normalized.target_currency
            })
        
        return formatted
    
    def _parse_rating(self, rating_str: str) -> float:
        """Parse rating string to float"""
        try:
            if rating_str and rating_str != 'N/A':
                return float(str(rating_str).strip())
        except ValueError:
            pass
        return None
    
    def _format_breakdown(self, normalized) -> str:
        """Format price breakdown for display"""
        parts = []
        if normalized.base.amount > 0:
            parts.append(f"Base: ₹{normalized.base.amount:,.2f}")
        if normalized.discount.amount > 0:
            parts.append(f"Discount: -₹{normalized.discount.amount:,.2f}")
        if normalized.shipping.amount > 0:
            parts.append(f"Shipping: +₹{normalized.shipping.amount:,.2f}")
        if normalized.tax.amount > 0:
            parts.append(f"Tax: +₹{normalized.tax.amount:,.2f}")
        return " | ".join(parts) if parts else "Base price"
    
    def _create_fallback_offer(self, result: Dict, price_value: float) -> ProductOffer:
        """Create a basic ProductOffer when pricing pipeline fails"""
        from pricing.types import NormalizedPrice
        
        parsed_price = ParsedMonetary(
            amount=Decimal(str(price_value)),
            currency='INR',
            raw_text=result.get('price', '0')
        )
        
        normalized = NormalizedPrice(
            base=parsed_price,
            shipping=ParsedMonetary(amount=Decimal('0'), currency='INR'),
            tax=ParsedMonetary(amount=Decimal('0'), currency='INR'),
            discount=ParsedMonetary(amount=Decimal('0'), currency='INR'),
            effective=parsed_price,
            target_currency='INR'
        )
        
        return ProductOffer(
            site=result.get('site', 'Unknown'),
            title=result.get('title', 'N/A'),
            url=result.get('link', '#'),
            normalized=normalized,
            rating=self._parse_rating(result.get('rating', 'N/A')),
            in_stock='in stock' in str(result.get('availability', '')).lower()
        )
    
    def _extract_price_value(self, price_str: str) -> float:
        """Extract numeric price value from string"""
        import re
        
        if not price_str or price_str == 'N/A' or price_str == 'Price not available':
            return 0.0
        
        # Remove currency symbols and commas
        clean_price = re.sub(r'[₹$,]', '', price_str)
        
        # Extract first number
        match = re.search(r'(\d+\.?\d*)', clean_price)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_available_sites(self) -> List[str]:
        """Get list of available scraper sites"""
        return [name.capitalize() for name in self.registry.list_scrapers()]
    
    def convert_price(self, amount: float, from_currency: str, to_currency: str = 'INR') -> Dict:
        """
        Convert price between currencies
        
        Args:
            amount: Price amount
            from_currency: Source currency code (USD, EUR, GBP, etc.)
            to_currency: Target currency code (default: INR)
            
        Returns:
            Dictionary with converted amount and rate
        """
        try:
            from_amount = Decimal(str(amount))
            converted = self.currency_converter.convert(from_amount, from_currency, to_currency)
            rate = converted / from_amount if from_amount > 0 else Decimal('1')
            
            return {
                'original_amount': float(from_amount),
                'original_currency': from_currency,
                'converted_amount': float(converted),
                'converted_currency': to_currency,
                'exchange_rate': float(rate),
                'display': f"{from_currency} {from_amount:,.2f} = {to_currency} {converted:,.2f}"
            }
        except Exception as e:
            return {
                'error': str(e),
                'original_amount': amount,
                'original_currency': from_currency,
                'converted_amount': 0,
                'converted_currency': to_currency
            }
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return ['INR', 'USD', 'EUR', 'GBP', 'JPY', 'AED', 'CAD', 'AUD']


# Create global instance
scraper_manager = ScraperManager()
