import re
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup

from src.config.logger import get_logger

log = get_logger(__name__)

_BOILERPLATE_TAGS = ["header", "footer", "nav", "script", "style", "noscript"]
_BOILERPLATE_SELECTORS = (
    ".navbar-container, .navbar, .footer, .global-nav, "
    ".navigation, .topbar, .content__meta, .visuallyhidden, "
    ".resource__contributors-list, #on-this-page, .resource__sources__heading"
)
_BLOCK_TAGS = [
    "p",
    "div",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "tr",
    "section",
    "article",
    "ul",
    "ol",
    "table",
    "br",
    "blockquote",
]


def _extract_from_html(html: str) -> tuple[str, str | None]:
    log.info("html_extract_start", html_len=len(html))

    soup = BeautifulSoup(html, "html.parser")

    root = soup.select_one("main, [role=main], #main-content")
    if root is None:  # CCSS-style pages have no <main>
        root = soup.body or soup

    # strip boilerplate from within the extracted region
    for t in root(_BOILERPLATE_TAGS):
        t.decompose()
    for el in root.select(_BOILERPLATE_SELECTORS):
        el.decompose()

    log.info("boilerplate_removed")

    # format links after removing boilerplate
    for link in root.find_all("a"):
        href = (link.get("href") or "").strip()
        if href and not href.startswith("#"):
            text = link.get_text(" ", strip=True)
            is_pdf = urlsplit(href).path.lower().endswith(".pdf")
            marker = "PDF" if is_pdf else "Link"
            link.replace_with(f"{text} [{marker}: {href}] ")

    log.info("links_parsed")

    for tag in root.find_all(_BLOCK_TAGS):
        tag.append("\n")

    text = root.get_text(" ", strip=False)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    title = soup.title.get_text(strip=True) if soup.title else None

    log.info("html_extract_complete", text_len=len(text), has_title=title is not None)
    return text, title


def scrape(url: str) -> tuple[str, str | None]:
    """Fetch a URL and extract clean text + title.

    Returns (text, title). Title may be None if not found.
    """
    log.info("scrape_called", url=url)

    log.info("http_request_start", url=url)
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()

    log.info(
        "http_request_success",
        url=url,
        status_code=response.status_code,
        bytes=len(response.text),
    )

    log.info("html_parsing_start", url=url)
    text, title = _extract_from_html(response.text)
    log.info("scrape_complete", url=url, chars=len(text), title=title)
    return text, title
