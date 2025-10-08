# Simple Scraper Example

Files added:

- `scraper.py` - example scraper using requests + BeautifulSoup with retries and CSV output.
- `requirements.txt` - Python dependencies.

How to run (Windows PowerShell):

1. Create a venv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -r requirements.txt
```

2. Run the scraper against the test site:

```powershell
python scraper.py --url "https://webscraper.io/test-sites/e-commerce/allinone" --output products.csv --limit 20
```

Notes:
- This example is intended for education and testing only (the test site `webscraper.io` is allowed for scraping).
- Always check `robots.txt` and the site's terms before scraping other websites.
- For JavaScript-heavy sites, consider using a headless browser (Playwright, Selenium) instead.
