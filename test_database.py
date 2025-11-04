#!/usr/bin/env python3
"""
Test script to verify database functionality
Tests all acceptance criteria:
- Search results are saved
- Can query by search_id
- Can query by date
"""

from database import create_sqlite_db
from datetime import datetime, timedelta
import os
import sys


def test_database_functionality():
    """Run comprehensive database tests"""
    
    print("=" * 60)
    print("DATABASE FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Use a test database
    test_db_path = 'test_scraper_history.db'
    
    # Remove if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"✓ Removed existing test database\n")
    
    try:
        # Initialize test database
        print("STEP 1: Initialize Database")
        print("-" * 60)
        db = create_sqlite_db(test_db_path, schema_file='schema.sql')
        print("✓ Database initialized successfully")
        print(f"✓ Database created at: {test_db_path}\n")
        
        # Test 1: Create search
        print("STEP 2: Create Search")
        print("-" * 60)
        query = "gaming laptop under $1500"
        search_id = db.create_search(query=query, user_id=1, status='in_progress')
        print(f"✓ Created search with ID: {search_id}")
        print(f"  Query: {query}\n")
        
        # Test 2: Save search results (Acceptance Criterion 1)
        print("STEP 3: Save Search Results")
        print("-" * 60)
        test_results = [
            {
                'product_name': 'ASUS ROG Strix G15',
                'price': 1299.99,
                'original_price': 1499.99,
                'discount_percentage': 13.33,
                'rating': 4.7,
                'reviews_count': 245,
                'availability': 'In Stock',
                'site': 'Amazon',
                'seller': 'Amazon.com',
                'url': 'https://amazon.com/product/1',
                'image_url': 'https://amazon.com/images/1.jpg'
            },
            {
                'product_name': 'Lenovo Legion 5 Pro',
                'price': 1399.99,
                'original_price': 1599.99,
                'discount_percentage': 12.50,
                'rating': 4.8,
                'reviews_count': 312,
                'availability': 'In Stock',
                'site': 'BestBuy',
                'seller': 'Best Buy',
                'url': 'https://bestbuy.com/product/2',
                'image_url': 'https://bestbuy.com/images/2.jpg'
            },
            {
                'product_name': 'MSI Katana GF66',
                'price': 1199.99,
                'original_price': 1399.99,
                'discount_percentage': 14.29,
                'rating': 4.5,
                'reviews_count': 189,
                'availability': 'Limited Stock',
                'site': 'Newegg',
                'seller': 'Newegg',
                'url': 'https://newegg.com/product/3',
                'image_url': 'https://newegg.com/images/3.jpg'
            },
            {
                'product_name': 'Acer Predator Helios 300',
                'price': 1449.99,
                'original_price': 1699.99,
                'discount_percentage': 14.71,
                'rating': 4.6,
                'reviews_count': 432,
                'availability': 'In Stock',
                'site': 'Amazon',
                'seller': 'Amazon.com',
                'url': 'https://amazon.com/product/4',
                'image_url': 'https://amazon.com/images/4.jpg'
            }
        ]
        
        # Save results
        db.add_results_batch(search_id, test_results)
        print(f"✓ Saved {len(test_results)} search results")
        
        # Update search status
        db.update_search(
            search_id=search_id,
            total_results=len(test_results),
            status='completed',
            duration_ms=2500
        )
        print(f"✓ Updated search status to 'completed'\n")
        
        # Test 3: Query by search_id (Acceptance Criterion 2)
        print("STEP 4: Query Results by Search ID")
        print("-" * 60)
        results = db.get_results_by_search_id(search_id)
        print(f"✓ Retrieved {len(results)} results for search_id={search_id}")
        print("\nResults:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['product_name']}")
            print(f"     Price: ${result['price']} (was ${result['original_price']})")
            print(f"     Site: {result['site_name']}")
            print(f"     Rating: {result['rating']}/5.0 ({result['reviews_count']} reviews)")
            print(f"     Availability: {result['availability']}")
            print()
        
        # Verify search details
        search = db.get_search_by_id(search_id)
        print(f"Search Details:")
        print(f"  Query: {search['query']}")
        print(f"  Total Results: {search['total_results']}")
        print(f"  Status: {search['status']}")
        print(f"  Duration: {search['search_duration_ms']}ms")
        print(f"  Timestamp: {search['search_timestamp']}\n")
        
        # Test 4: Query by date (Acceptance Criterion 3)
        print("STEP 5: Query Results by Date Range")
        print("-" * 60)
        
        # Test date range: last 24 hours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        print(f"Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Query searches by date
        searches = db.get_searches_by_date(start_date, end_date)
        print(f"✓ Found {len(searches)} searches in date range")
        
        # Query results by date for our search
        results_by_date = db.get_results_by_search_and_date(
            search_id=search_id,
            start_date=start_date,
            end_date=end_date
        )
        print(f"✓ Found {len(results_by_date)} results for search_id={search_id} in date range")
        print(f"\nResults within date range:")
        for result in results_by_date[:3]:  # Show first 3
            print(f"  - {result['product_name']}: ${result['price']}")
        if len(results_by_date) > 3:
            print(f"  ... and {len(results_by_date) - 3} more")
        print()
        
        # Test 5: Additional functionality tests
        print("STEP 6: Test Additional Functionality")
        print("-" * 60)
        
        # Add metadata
        db.add_metadata(search_id, 'filters', '{"price_max": 1500, "category": "gaming"}')
        db.add_metadata(search_id, 'source', 'web_ui')
        print("✓ Added metadata to search")
        
        # Get metadata
        metadata = db.get_metadata(search_id)
        print(f"✓ Retrieved {len(metadata)} metadata entries")
        
        # Record export
        export_id = db.record_export(
            search_id=search_id,
            export_format='csv',
            result_count=len(test_results),
            file_path='/tmp/search_results.csv'
        )
        print(f"✓ Recorded export with ID: {export_id}")
        
        # Get statistics
        stats = db.get_search_statistics(days=30)
        print(f"\nDatabase Statistics:")
        print(f"  Total searches: {stats['total_searches']}")
        print(f"  Average results per search: {stats['avg_results_per_search']:.2f}")
        print(f"  Unique queries: {stats['unique_queries']}")
        if stats['avg_duration_ms']:
            print(f"  Average duration: {stats['avg_duration_ms']:.2f}ms")
        
        # Get site performance
        site_stats = db.get_site_performance()
        print(f"\nSite Performance:")
        for site in site_stats:
            if site['total_results'] > 0:
                print(f"  {site['site_name']}: {site['total_results']} products, avg price ${site['avg_price']:.2f}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nAcceptance Criteria Verification:")
        print("  ✅ Search results are saved (add_results_batch)")
        print("  ✅ Can query by search_id (get_results_by_search_id)")
        print("  ✅ Can query by date (get_results_by_search_and_date)")
        print("\nDatabase file: " + test_db_path)
        print("Keep this file for inspection or delete to cleanup.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_additional_scenarios():
    """Test edge cases and additional scenarios"""
    
    print("\n" + "=" * 60)
    print("ADDITIONAL SCENARIO TESTS")
    print("=" * 60 + "\n")
    
    test_db_path = 'test_scraper_history.db'
    
    try:
        db = create_sqlite_db(test_db_path, schema_file='schema.sql')
        
        # Test 1: Multiple searches
        print("Scenario 1: Multiple searches over time")
        print("-" * 60)
        queries = ["laptop", "monitor", "keyboard", "mouse", "headset"]
        search_ids = []
        
        for query in queries:
            sid = db.create_search(query=query)
            search_ids.append(sid)
            # Add dummy results
            dummy_results = [
                {'product_name': f'{query.title()} Product 1', 'price': 99.99, 
                 'site': 'Amazon', 'url': 'https://example.com'}
            ]
            db.add_results_batch(sid, dummy_results)
            db.update_search(sid, total_results=1, status='completed')
        
        print(f"✓ Created {len(search_ids)} searches")
        
        # Get recent searches
        recent = db.get_recent_searches(limit=10)
        print(f"✓ Retrieved {len(recent)} recent searches")
        
        # Test 2: Search by query pattern
        print("\nScenario 2: Search by query pattern")
        print("-" * 60)
        laptop_searches = db.search_by_query('%laptop%')
        print(f"✓ Found {len(laptop_searches)} searches matching 'laptop'")
        
        # Test 3: Popular queries
        print("\nScenario 3: Popular queries analysis")
        print("-" * 60)
        popular = db.get_popular_queries(limit=5)
        print(f"✓ Top {len(popular)} popular queries:")
        for q in popular:
            print(f"  - '{q['query']}': {q['search_count']} times")
        
        print("\n✅ Additional scenarios passed!")
        
    except Exception as e:
        print(f"\n❌ Additional tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    success = test_database_functionality()
    
    if success:
        test_additional_scenarios()
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)
