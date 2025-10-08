import requests
from scraper import parse_products, create_session, fetch


def test_parse_products_returns_list():
    session = create_session()
    html = fetch("https://webscraper.io/test-sites/e-commerce/allinone", session)
    items = parse_products(html, max_items=5)
    assert isinstance(items, list)
    assert len(items) <= 5
    if items:
        first = items[0]
        assert "title" in first
        assert "price" in first
        assert "description" in first
