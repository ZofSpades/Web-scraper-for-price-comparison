"""
Real-time scraping integration with asynchronous support
Coordinates scraping across multiple e-commerce sites with advanced pricing utilities
Uses async scraping for improved performance (target: ≤10-15s for 5 websites)
"""

from scrapers.scraper_registry import ScraperRegistry
from scrapers.async_scraper_controller import AsyncScraperController  # Use async controller
from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from scrapers.snapdeal_scraper import SnapdealScraper
from scrapers.myntra_scraper import MyntraScraper
from scrapers.croma_scraper import CromaScraper
from typing import List, Dict
import time

# Import pricing utilities for advanced price parsing and comparison
from pricing.currency import CurrencyConverter
from pricing.compare import rank_offers
from pricing.types import ProductOffer, RawPrice, ParsedMonetary
from pricing.normalize import normalize as normalize_price
from decimal import Decimal


class ScraperManager:
    """
    Manages real-time scraping from multiple e-commerce sites
    Uses asynchronous scraping for improved performance
    """
    
    def __init__(self):
        """Initialize scraper registry and register all scrapers"""
        self.registry = ScraperRegistry()
        self.controller = AsyncScraperController(self.registry)  # Use async controller
        
        # Set optimized timeouts for async scraping (target: ≤15s total)
        # Per-site timeout: 10s - Maximum time allowed for a single scraper
        # Total timeout: 15s - Overall deadline for all concurrent scrapers
        # Buffer: 5s - Allows for asyncio overhead, initialization, and result processing
        # Since scrapers run concurrently, total time ≈ max(individual_times) + overhead
        self.controller.set_timeout(10)  # 10 seconds per site
        self.controller.set_total_timeout(15)  # 15 seconds total for all sites (5s buffer)
        self.controller.set_max_retries(2)
        
        # Register scrapers
        self.registry.register(AmazonScraper())
        self.registry.register(FlipkartScraper())
        self.registry.register(SnapdealScraper())
        self.registry.register(MyntraScraper())
        self.registry.register(CromaScraper())
        
        # Initialize currency converter with INR as base
        self.currency_converter = CurrencyConverter(base_currency="INR")
    
    def search_product(self, query: str, sites: List[str] = None) -> List[Dict]:
        """
        Search for product across multiple sites using async scraping
        
        Args:
            query: Product name or search query
            sites: List of site names to search (None = all sites)
            
        Returns:
            List of product results from all sites
        """
        print(f"[SCRAPER_MANAGER] search_product called with query='{query}', sites={sites}")
        
        start_time = time.time()
        
        if sites is None or 'all' in sites or len(sites) == 0:
            # Search all registered sites using async controller
            print(f"[SCRAPER_MANAGER] Searching ALL registered sites: {self.registry.get_registered_sites()}")
            results = self.controller.scrape_all(query)
            print(f"[SCRAPER_MANAGER] Raw results from async scrape_all: {len(results)} results")
        else:
            # Search specific sites using async controller
            print(f"[SCRAPER_MANAGER] Searching specific sites: {sites}")
            results = self.controller.scrape_all(query, specific_sites=sites)
        
        elapsed_time = time.time() - start_time
        print(f"[SCRAPER_MANAGER] Total scraping time: {elapsed_time:.2f}s")
        
        formatted = self._format_results(results)
        print(f"[SCRAPER_MANAGER] Formatted results: {len(formatted)} results")
        
        return formatted
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """
        Format results using advanced pricing utilities
        - Parse prices with multi-currency support
        - Normalize prices to common currency (INR)
        - Rank by best effective price
        """
        offers = []
        
        for result in results:
            site = result.get('site', 'Unknown')
            print(f"[FORMAT] Processing result from {site}: title={result.get('title', 'N/A')}, price={result.get('price', 'N/A')}")
            
            # Skip if error occurred
            if 'error' in result and result['title'] == 'Error':
                print(f"[FORMAT] Skipping {site} - error result: {result.get('error')}")
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
                'reviews': offer.reviews or 0,
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
            # Invalid rating format, will return None below
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
        return self.registry.get_registered_sites()
    
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
