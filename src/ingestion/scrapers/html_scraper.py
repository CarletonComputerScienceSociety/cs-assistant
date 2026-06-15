import httpx
from bs4 import BeautifulSoup

def scrape(url: str) -> tuple[str, str | None]:
    """Fetch a URL and extract clean text + title.

    Returns (text, title). Title may be None if not found.
    """
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        
    html = response.text

    cut_marker = "<!-- close main-wrapper"
    if cut_marker in html:
        html = html.split(cut_marker)[0]

    html = BeautifulSoup(html, "html.parser")

    for el in html.select(".footer, .global-nav, .navigation, .topbar, .content__meta"): # removing elements by class
        el.decompose()

    for tag in html(["header","footer"]): # removing elements by tag
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
    
    title = str(html("title")[0])

    return text, title

_url = "https://carleton.ca/registration/new-ug/new-student-faqs/"
_url2 = "https://carleton.ca/scs/current-students/bachelor-of-cybersecurity/bcyber-courses-and-registration/"

with open("output.txt", "w", encoding="utf-8") as file:
    for i in scrape(_url2):
        file.write(i)