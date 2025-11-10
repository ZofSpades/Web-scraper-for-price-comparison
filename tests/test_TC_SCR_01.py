from scrapers.base_scraper import BaseScraper
from scrapers.scraper_manager import ScraperManager


def test_TC_SCR_01():
    manager = ScraperManager()

    class DummyScraper(BaseScraper):
        def scrape(self, input_data):
            return {
                "site": "SiteA",
                "title": "Prod",
                "price": "₹1000",
                "rating": "4.5",
                "availability": "In Stock",
                "link": "https://sitea/item",
            }

        def get_site_name(self):
            return "SiteA"

    manager.registry.clear()
    manager.registry.register(DummyScraper())
    res = manager.search_product("Prod")
    assert any(r["seller"] == "SiteA" for r in res)
