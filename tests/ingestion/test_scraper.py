from pathlib import Path

from src.ingestion.scrapers.html_scraper import _extract_from_html

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


junk = [
    # skip / accessibility links (very common in these pages)
    "Skip to Main Content",
    "Skip to Content",
    "Skip to main content",
    "Skip to navigation",
    # search / UI chrome
    "Search this website",
    "Search",
    "Menu",
    "Toggle submenu",
    "Close the search modal",
    "Close the site search",
    "Close the mobile menu",
    "Site Menu",
    "Footer",
    # cookie / consent banners
    "This site uses cookies to offer you a better browsing experience.",
    "Ok, got it!",
    # repeated footer / organization branding noise
    "email:",
    "© 2026 Carleton Computer Science Society",
    "Carleton University acknowledges the location of its campus on the traditional, unceded territories of the Algonquin Anishinàbeg nation",  # noqa: E501
    "Contact us by",
    "1125 Colonel By Drive, Ottawa, ON, K1S 5B6, Canada",
    "Short URL:",
    "Share:",
    # icon-only or structural labels that sometimes leak through
    "Links and Sources",
]

pages = [
    {
        "file": "CCSS_ArticleTest.html",
        "title": "Carleton Computer Science Society | Making a Balanced Course Schedule",
        "assertions": [
            "Making a Balanced Course Schedule",
            "Careful planning can help you create a timetable that supports your academic goals, fits your lifestyle, and keeps your workload manageable.",  # noqa: E501
            "Consider all the Possibilities",
            "Class Timing",
            "Lunch Time",
            "Time-Ticket Madness",
            "Rate My Prof",
            "No Schedule is Perfect",
            "COMP 1405",
            "MATH 1104",
            "Do I have to take first year courses in a specific order?",
            "Ways to Reduce Your Second Year Workload",
            "BCS first year course selection guide",
        ],
    },
    {
        "file": "CCSS_CourseReg.html",
        "title": "Carleton Computer Science Society | Course Registration",
        "assertions": [
            "Course Registration",
            "Find the answers to all your questions about course registration.",
            "Which Electives Should You Take?",
            "Should You Take COMP 1405/1406-Z?",
            "Why You Should Consider a Minor as a CS Student",
            "Frequently Asked Questions",
            "Which courses should I take in first year?",
            "Do I have to take first year courses in a specific order?",
            "What is a Breadth elective vs a Free elective?",
            "Do we register for both fall and winter courses now?",
            "Who should I contact if I need help with registration?",
            "Are COMP 1005/1006 and 1405/1406 different?",
        ],
    },
    {
        "file": "CCSS_faqTest.html",
        "title": "Carleton Computer Science Society | Do I have to take first year courses in a specific order?",  # noqa: E501
        "assertions": [
            "Do I Have to Take First Year Courses in a Specific Order?",
            "COMP 1405 and 1406 should be taken in Fall and Winter respectively.",
            "The First-Year Course Selection Guide",
            "MATH 1007",
            "COMP 1805",
            "Can I take second year courses in first year?",
            "Ways to Reduce Your Second Year Workload",
            "BCS First Year Course Selection Guide",
        ],
    },
    {
        "file": "courseTest.html",
        "title": "Courses and Registration (B.Cyber.) - School of Computer Science",
        "assertions": [
            "This page will help you plan your courses and academic career as you complete your Bachelor of Cybersecurity degree program.",  # noqa: E501
            "Course Descriptions and Outlines",
            "First Year Registration Guide",
            "Academic Audit",
            "Prerequisites and Restrictions",
            "Course Patterns",
            "Electives and Prohibited Courses",
            "Course Selection FAQs",
            "What is a prerequisite?",
            "What is a preclusion?",
            "Where are the CSEC courses on the Public Class Schedule?",
            "Do I have to follow the course pattern for my admit year?",
            "2026-27 Undergraduate Calendar Changes Summary",
            "Undergraduate Calendar Change Summaries",
        ],
    },
    {
        "file": "faqTest.html",
        "title": "New Student FAQs - Registration",
        "assertions": [
            "The following are frequently asked questions for new undergraduate students.",
            "I am a first year, where should I start?",
            "I have a lot of questions – do you have a starting-out guide?",
            "How do I build a timetable?",
            "Do you have more specific videos to assist with registration?",
            "Can someone walk me through all this?",
            "I am a returning student, where should I start?",
            "I’ve been told I have to satisfy a breadth requirement. What does this mean?",
            "I was admitted with an ESL Requirement (ESLR). Where can I get more information?",
            "How do I view my grades or exam schedule",
        ],
    },
]


def test_pages():
    for page in pages:
        html = load_fixture(page["file"])

        text, title = _extract_from_html(html)

        for element in junk:
            assert element not in text, f"Missing assertion:\n{element} {page["file"]}"

        for assertion in page["assertions"]:
            assert assertion in text, f"Missing assertion:\n{assertion} {page["file"]}"

        assert title == page["title"]


def test_pdf_and_link_markers():
    text, _ = _extract_from_html(load_fixture("courseTest.html"))

    pdf_url = "https://carleton.ca/scs/wp-content/uploads/BCyber-Course-Map-202630-3.pdf"
    assert f"[PDF: {pdf_url}]" in text
    assert "[Link:" in text
