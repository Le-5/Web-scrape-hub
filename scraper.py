import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

HEADERS = {
    "User-Agent": "WebScrapeHub/1.0 (educational scraper)"
}


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(
            "Enter a valid URL starting with http:// or https://"
        )


def clean(text):
    return " ".join(text.split())


def scrape_url(url, options):
    validate_url(url)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove unnecessary elements
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Page title
    title = ""

    if soup.title:
        title = clean(
            soup.title.get_text()
        )

    # Headings
    headings = [
        clean(x.get_text(" ", strip=True))
        for x in soup.find_all(["h1", "h2", "h3"])
    ]

    # Paragraphs
    paragraphs = [
        clean(x.get_text(" ", strip=True))
        for x in soup.find_all("p")
        if clean(x.get_text(" ", strip=True))
    ]

    # Links
    links = []

    for a in soup.find_all("a", href=True):

        text = clean(
            a.get_text(" ", strip=True)
        )

        href = urljoin(
            url,
            a["href"]
        )

        if href.startswith(("http://", "https://")):
            links.append({
                "text": text,
                "url": href
            })

    # Images
    images = []

    for img in soup.find_all("img", src=True):

        images.append({
            "alt": clean(img.get("alt", "")),
            "url": urljoin(url, img["src"])
        })

    # Tables
    tables = []

    for table in soup.find_all("table"):

        rows = []

        for tr in table.find_all("tr"):

            cells = [
                clean(
                    c.get_text(" ", strip=True)
                )
                for c in tr.find_all(["th", "td"])
            ]

            if cells:
                rows.append(cells)

        if rows:
            tables.append(rows)

    # Final result
    return {
        "url": url,

        "scraped_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "title": title,

        "headings": (
            headings
            if options.get("headings", True)
            else []
        ),

        "paragraphs": (
            paragraphs
            if options.get("paragraphs", True)
            else []
        ),

        "links": (
            links
            if options.get("links", True)
            else []
        ),

        "images": (
            images
            if options.get("images", True)
            else []
        ),

        "tables": (
            tables
            if options.get("tables", True)
            else []
        )
    }