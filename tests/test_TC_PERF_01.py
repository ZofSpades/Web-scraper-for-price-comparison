import time

from scrapers.base_scraper import BaseScraper
from scrapers.scraper_controller import ScraperController


def test_TC_PERF_01():
    controller = ScraperController()

    class FastScraper(BaseScraper):
        def scrape(self, input_data):
            return {
                "site": "Fast",
                "title": "P",
                "price": "₹10",
                "rating": "5",
                "availability": "In Stock",
                "link": "#",
            }

    controller.registry.clear()
    controller.registry.register(FastScraper())
    start = time.time()
    results = controller.scrape_all("P")
    duration = time.time() - start
    assert duration < 5 and isinstance(results, list)
