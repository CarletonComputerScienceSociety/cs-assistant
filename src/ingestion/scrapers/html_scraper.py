import httpx
from bs4 import BeautifulSoup

def _extract_from_html(html: str) -> tuple[str, str | None]:
    cut_marker = "<!-- close main-wrapper"
    if cut_marker in html:
        html = html.split(cut_marker)[0]

    html = BeautifulSoup(html, "html.parser")
    # removing elements by class
    for el in html.select(
        ".footer, .global-nav, .navigation, "
        ".topbar, .content__meta, .visuallyhidden"
        ):
        el.decompose()

    # removing elements by tag
    for tag in html(["header","footer","nav"]):
        tag.decompose()

    # formatting links after clearing having cleared clutter
    for link in html.find_all('a'):
        href = link.get("href")
        if href and href[0] != '#':
            if href[-3:] == "pdf":
                link.string = f"{link.string} [PDF: {href}]"
            else:
                link.string = f"{link.string} [Link: {href}]"


    text = html.get_text("\n", strip=True)
    
    title = (html("title")[0]).get_text()

    return text, title


def scrape(url: str) -> tuple[str, str | None]:
    """Fetch a URL and extract clean text + title.

    Returns (text, title). Title may be None if not found.
    """
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        
    return _extract_from_html(response.text)
