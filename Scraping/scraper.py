"""Simple, robust scraper example for the webscraper.io test site.

Features:
- requests.Session with retries and sensible headers
- polite rate limiting (delay) and optional limit
- parsing with BeautifulSoup into a list of dicts
- save results to CSV

This is a small, reusable script intended for learning and testing only.
Respect robots.txt and site terms before running on other sites.
"""
from __future__ import annotations

import argparse
import csv
import logging
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


LOG = logging.getLogger("scraper")


def create_session(user_agent: str | None = None, retries: int = 3, backoff: float = 0.3) -> requests.Session:
    session = requests.Session()
    ua = user_agent or (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    )
    session.headers.update({"User-Agent": ua, "Accept-Language": "en-US,en;q=0.9"})

    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch(url: str, session: requests.Session, timeout: int = 10) -> str:
    LOG.info("Fetching %s", url)
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_products(html: str, max_items: int | None = None) -> List[Dict[str, str]]:
    """Parse simple product data from the webscraper.io test site layout.

    Returns a list of dicts with keys: title, price, description, reviews, url
    """
    soup = BeautifulSoup(html, "lxml")
    # product containers on the test site are under div.thumbnail
    containers = soup.select("div.thumbnail")
    items: List[Dict[str, str]] = []
    for c in containers:
        title_tag = c.select_one("a.title") or c.select_one("a")
        title = title_tag.get_text(strip=True) if title_tag else ""
        link = title_tag.get("href") if title_tag else ""

        price_tag = c.select_one("h4.price") or c.select_one(".price")
        price = price_tag.get_text(strip=True) if price_tag else ""

        desc_tag = c.select_one("p.description") or c.select_one("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        reviews_tag = c.select_one("div.ratings p.pull-right") or c.select_one(".ratings")
        reviews = reviews_tag.get_text(strip=True) if reviews_tag else ""

        items.append({"title": title, "price": price, "description": description, "reviews": reviews, "url": link})
        if max_items and len(items) >= max_items:
            break
    return items


def save_csv(items: List[Dict[str, str]], filename: str) -> None:
    if not items:
        LOG.warning("No items to save")
        return
    keys = list(items[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        for it in items:
            writer.writerow(it)
    LOG.info("Saved %d items to %s", len(items), filename)


def main() -> None:
    parser = argparse.ArgumentParser(description="Small scraper example (webscraper.io test site)")
    parser.add_argument("--url", default="https://webscraper.io/test-sites/e-commerce/allinone", help="URL to scrape")
    parser.add_argument("--output", default="products.csv", help="CSV output file")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of items to retrieve (0 = no limit)")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests (seconds)")
    parser.add_argument("--user-agent", default=None, help="Custom User-Agent header")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    session = create_session(user_agent=args.user_agent)

    html = fetch(args.url, session)
    items = parse_products(html, max_items=(args.limit or None))
    save_csv(items, args.output)
    # polite pause
    time.sleep(args.delay)


if __name__ == "__main__":
    main()
