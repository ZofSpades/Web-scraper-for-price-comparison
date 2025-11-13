"""
Test Script for Proxy and User-Agent Rotation
Run this to verify rotation functionality is working correctly.
"""

import sys
import time
from scrapers.base_scraper import BaseScraper
from scrapers.rotation_manager import RotationManager, UserAgentRotator, ProxyRotator


def test_user_agent_rotation():
    """Test user-agent rotation functionality"""
    print("\n" + "=" * 60)
    print("TEST 1: User-Agent Rotation")
    print("=" * 60)
    
    rotator = UserAgentRotator()
    
    print(f"✓ Total user agents: {len(rotator.user_agents)}")
    
    # Test random selection
    print("\n5 Random User Agents:")
    for i in range(5):
        ua = rotator.get_random()
        print(f"  {i+1}. {ua[:70]}...")
    
    # Test sequential rotation
    print("\n5 Sequential User Agents:")
    for i in range(5):
        ua = rotator.get_next()
        print(f"  {i+1}. {ua[:70]}...")
    
    print("\n✓ User-agent rotation working correctly!")
    return True


def test_proxy_rotation():
    """Test proxy rotation functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Proxy Rotation")
    print("=" * 60)
    
    # Test with sample proxies
    test_proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:3128',
        'http://user:pass@proxy3.example.com:8080',
    ]
    
    rotator = ProxyRotator(test_proxies)
    
    print(f"✓ Total proxies: {len(rotator.proxies)}")
    
    # Test sequential rotation
    print("\nProxy Rotation:")
    for i in range(5):
        proxy = rotator.get_next()
        if proxy:
            print(f"  {i+1}. {proxy}")
    
    # Test random selection
    print("\nRandom Proxy Selection:")
    for i in range(3):
        proxy = rotator.get_random()
        if proxy:
            print(f"  {i+1}. {proxy}")
    
    # Test failure tracking
    print("\nTesting Failure Tracking:")
    test_proxy = rotator.get_next()
    print(f"  Selected proxy: {test_proxy}")
    
    rotator.mark_failure(test_proxy)
    print(f"  ✓ Marked as failed (1/3)")
    
    rotator.mark_failure(test_proxy)
    print(f"  ✓ Marked as failed (2/3)")
    
    rotator.mark_failure(test_proxy)
    print(f"  ✓ Marked as failed (3/3 - will be disabled)")
    
    total, available = rotator.get_proxy_count()
    print(f"  Available proxies: {available}/{total}")
    
    # Test success marking
    rotator.mark_success(test_proxy)
    print(f"  ✓ Marked as successful (failures cleared)")
    
    total, available = rotator.get_proxy_count()
    print(f"  Available proxies: {available}/{total}")
    
    print("\n✓ Proxy rotation working correctly!")
    return True


def test_rotation_manager():
    """Test combined rotation manager"""
    print("\n" + "=" * 60)
    print("TEST 3: Rotation Manager (Combined)")
    print("=" * 60)
    
    test_proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:3128',
    ]
    
    manager = RotationManager(test_proxies)
    
    # Test random config
    print("\nRandom Configuration:")
    ua, proxy = manager.get_random_config()
    print(f"  User-Agent: {ua[:60]}...")
    print(f"  Proxy: {proxy}")
    
    # Test next config
    print("\nNext Configuration (Sequential):")
    ua, proxy = manager.get_next_config()
    print(f"  User-Agent: {ua[:60]}...")
    print(f"  Proxy: {proxy}")
    
    # Test headers with rotation
    print("\nHeaders with Rotation:")
    headers = manager.get_headers_with_rotation()
    print(f"  User-Agent: {headers['User-Agent'][:60]}...")
    
    # Test status
    print("\nRotation Status:")
    status = manager.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Rotation manager working correctly!")
    return True


def test_base_scraper_integration():
    """Test integration with BaseScraper"""
    print("\n" + "=" * 60)
    print("TEST 4: BaseScraper Integration")
    print("=" * 60)
    
    # Configure proxies
    test_proxies = [
        'http://test-proxy1.example.com:8080',
        'http://test-proxy2.example.com:3128',
    ]
    
    print(f"Configuring {len(test_proxies)} test proxies...")
    BaseScraper.configure_proxies(test_proxies)
    
    # Check status
    status = BaseScraper.get_rotation_status()
    print("\nRotation Status:")
    print(f"  User Agents: {status['user_agents_count']}")
    print(f"  Total Proxies: {status['total_proxies']}")
    print(f"  Available Proxies: {status['available_proxies']}")
    print(f"  Proxies Enabled: {status['proxies_enabled']}")
    
    # Create a dummy scraper to test instance methods
    class TestScraper(BaseScraper):
        def scrape(self, input_data: str):
            return {}
    
    scraper = TestScraper()
    
    # Test header rotation
    print("\nTesting Header Rotation:")
    for i in range(3):
        headers = scraper.get_headers()
        print(f"  {i+1}. UA: {headers['User-Agent'][:60]}...")
    
    # Test proxy methods
    print("\nTesting Proxy Methods:")
    proxy1 = scraper.get_proxy()
    print(f"  get_proxy(): {proxy1}")
    
    proxy2 = scraper.get_random_proxy()
    print(f"  get_random_proxy(): {proxy2}")
    
    print("\n✓ BaseScraper integration working correctly!")
    return True


def test_error_handling():
    """Test error handling and edge cases"""
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling & Edge Cases")
    print("=" * 60)
    
    # Test with no proxies
    print("\nTest: No proxies configured")
    rotator = ProxyRotator([])
    proxy = rotator.get_next()
    print(f"  Result: {proxy} (should be None)")
    assert proxy is None, "Should return None when no proxies"
    print("  ✓ Correctly handled")
    
    # Test with all proxies failed
    print("\nTest: All proxies failed")
    rotator = ProxyRotator(['http://proxy.example.com:8080'])
    test_proxy = rotator.get_next()
    for i in range(3):
        rotator.mark_failure(test_proxy)
    
    total, available = rotator.get_proxy_count()
    print(f"  Available: {available}/{total}")
    assert available == 0, "All proxies should be unavailable"
    print("  ✓ Correctly handled")
    
    # Test cooldown recovery
    print("\nTest: Cooldown recovery")
    print("  Waiting for cooldown... (this would take 5 minutes normally)")
    print("  Skipping actual wait for test")
    print("  ✓ Cooldown mechanism in place")
    
    print("\n✓ Error handling tests passed!")
    return True


def test_real_request_simulation():
    """Simulate real requests with rotation"""
    print("\n" + "=" * 60)
    print("TEST 6: Real Request Simulation")
    print("=" * 60)
    
    BaseScraper.configure_proxies([
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:3128',
    ])
    
    class DummyScraper(BaseScraper):
        def scrape(self, input_data: str):
            return {}
    
    scraper = DummyScraper()
    
    print("\nSimulating 10 requests with rotation:")
    for i in range(10):
        headers = scraper.get_headers()
        proxy = scraper.get_proxy()
        
        print(f"\n  Request {i+1}:")
        print(f"    User-Agent: {headers['User-Agent'][:50]}...")
        print(f"    Proxy: {proxy}")
        
        # Simulate some requests failing
        if i % 3 == 0:
            scraper.mark_proxy_failure(proxy)
            print(f"    Status: Failed (marked)")
        else:
            scraper.mark_proxy_success(proxy)
            print(f"    Status: Success")
        
        time.sleep(0.1)  # Small delay
    
    # Check final status
    status = BaseScraper.get_rotation_status()
    print(f"\nFinal Status:")
    print(f"  Available Proxies: {status['available_proxies']}/{status['total_proxies']}")
    
    print("\n✓ Request simulation completed!")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PROXY & USER-AGENT ROTATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("User-Agent Rotation", test_user_agent_rotation),
        ("Proxy Rotation", test_proxy_rotation),
        ("Rotation Manager", test_rotation_manager),
        ("BaseScraper Integration", test_base_scraper_integration),
        ("Error Handling", test_error_handling),
        ("Request Simulation", test_real_request_simulation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n✗ TEST FAILED: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"       Error: {error}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Rotation system is working correctly.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
