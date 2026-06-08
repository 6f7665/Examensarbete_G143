#!/usr/bin/env python3

import sys
import re
import csv
from html.parser import HTMLParser
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse
from collections import deque


# -----------------------------
# LIX-funktion
# -----------------------------

def lix(text: str) -> float:
    meningar = re.split(r'[.!?]+', text)
    meningar = [m for m in meningar if m.strip()]

    ord_lista = re.findall(r'\b\w+\b', text, re.UNICODE)

    antal_ord = len(ord_lista)
    antal_meningar = len(meningar)

    if antal_ord == 0 or antal_meningar == 0:
        return 0.0

    långa_ord = sum(1 for ord in ord_lista if len(ord) > 6)

    lix_värde = (
        (antal_ord / antal_meningar)
        + (långa_ord * 100 / antal_ord)
    )

    return round(lix_värde, 2)


# -----------------------------
# HTML-parser
# -----------------------------

class LinkAndTextParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.links = []

        self.in_p = False
        self.in_tr = False
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a":
            href = attrs.get("href")
            if href:
                self.links.append(href)

        if tag == "p":
            self.in_p = True
        if tag == "tr":
            self.in_tr = True

        # Gör <br> till punkt
        if tag == "br" and self.in_p:
            self.text_parts.append(". ")

    def handle_endtag(self, tag):
        if tag == "p":
            self.in_p = False
            if self.in_tr == True:
                self.text_parts.append(". ")
        if tag == "tr":
            self.in_tr = False

    def handle_data(self, data):
        if self.in_p:
            self.text_parts.append(data)

    def get_text(self):
        return " ".join(self.text_parts)

# -----------------------------
# Hjälpfunktioner
# -----------------------------

def normalize_url(url):
    parsed = urlparse(url)

    # Ta bort fragment (#...)
    cleaned = parsed._replace(fragment="")

    # Ta bort trailing slash
    normalized = cleaned.geturl().rstrip("/")

    return normalized


def is_subpage(base_url, candidate_url):
    """
    Tillåt endast URL:er som ligger under bas-URL:ens path.
    """

    base = urlparse(base_url)
    candidate = urlparse(candidate_url)

    # Samma domän krävs
    if base.netloc != candidate.netloc:
        return False

    base_path = base.path.rstrip("/")
    candidate_path = candidate.path.rstrip("/")

    return candidate_path.startswith(base_path)


def fetch_page(url):
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urlopen(req, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "")

            if "text/html" not in content_type:
                return None

            charset = response.headers.get_content_charset() or "utf-8"

            html = response.read().decode(charset, errors="ignore")

            return html

    except Exception:
        return None


# -----------------------------
# Crawling
# -----------------------------

def crawl(base_url):
    visited = set()
    queue = deque([base_url])

    writer = csv.writer(sys.stdout)

    while queue:
        url = normalize_url(queue.popleft())

        if url in visited:
            continue

        visited.add(url)

        html = fetch_page(url)

        if not html:
            continue

        parser = LinkAndTextParser()
        parser.feed(html)

        text = parser.get_text()
        #print(text) #debug

        lix_value = lix(text)

        # CSV-utskrift
        writer.writerow([url, lix_value])

        # Hitta nya undersidor
        for link in parser.links:
            absolute = urljoin(url, link)
            absolute = normalize_url(absolute)

            if is_subpage(base_url, absolute):
                if absolute not in visited:
                    queue.append(absolute)


# -----------------------------
# Main
# -----------------------------

def main():
    if len(sys.argv) != 2:
        print(
            f"Användning: {sys.argv[0]} <url>",
            file=sys.stderr
        )
        sys.exit(1)

    base_url = normalize_url(sys.argv[1])

    crawl(base_url)


if __name__ == "__main__":
    main()
