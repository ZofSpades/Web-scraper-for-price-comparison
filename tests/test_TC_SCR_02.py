from scrapers.scraper_manager import ScraperManager


def test_TC_SCR_02():
    manager = ScraperManager()
    manager.registry.clear()
    res = manager.search_product("Anything")
    assert isinstance(res, list)
