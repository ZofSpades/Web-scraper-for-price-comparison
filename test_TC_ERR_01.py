from scrapers.base_scraper import BaseScraper
from scrapers.scraper_controller import ScraperController


def test_TC_ERR_01():
    controller = ScraperController()

    class BadScraper(BaseScraper):
        def scrape(self, input_data):
            raise RuntimeError("fail")

    controller.registry.clear()
    controller.registry.register(BadScraper())
    res = controller.scrape_all("X")
    assert any(r.get("title") == "Error" for r in res)
