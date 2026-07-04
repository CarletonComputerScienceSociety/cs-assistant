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

    # repeated footer / organization branding noise
    "email:",
    "© 2026 Carleton Computer Science Society",

    # icon-only or structural labels that sometimes leak through
    "Links and Sources",

]

#add pages
pages = [
    {
        "file": "courseTest.html",
        "title": "Courses and Registration (B.Cyber.) - School of Computer Science",
        "assertions": [
            "Electives and Prohibited Courses",
            "[PDF: https://carleton.ca/scs/wp-content/uploads/BCyber-Course-Map-202630-3.pdf]",
            "[PDF: https://carleton.ca/scs/wp-content/uploads/FINAL2-BCyber-Course-Map-202530.pdf]"
        ]
    },
    {
        "file":"faqTest.html",
        "title":"New Student FAQs - Registration",
        "assertions":[
            "How do I build a timetable?",
            "Log into Carleton Central",
            "How do I view my grades or exam schedule",
            "Information about how to view your grades or exam schedule"
        ]
    },
    {
        "file": "CCSS_faqTest.html",
        "title": "Carleton Computer Science Society | Do I have to take first year courses in a specific order?",
        "assertions": [
            "Do I Have to Take First Year Courses in a Specific Order?",
            "COMP 1405 and 1406 should be taken in Fall and Winter respectively.",
            "The First-Year Course Selection Guide",
            "MATH 1007",
            "COMP 1805",
            "Can I take second year courses in first year?",
            "Do we register for both fall and winter courses now?",
            "Who should I contact if I need help with registration?"
        ]
    },
    {
        "file": "CCSS_CourseReg.html",
        "title": "Carleton Computer Science Society | Course Registration",
        "assertions": [
            "Course Registration",
            "Resources",
            "Frequently Asked Questions",
            "Making a Balanced Course Schedule",
            "Which Electives Should You Take?",
            "Do I have to take first year courses in a specific order?",
            "What is the COMP 1405/1406-Z section?",
            "Can I switch courses after registering?",
            "How many courses should I take in a semester?"
        ]
    },
    {
        "file": "CCSS_ArticleTest.html",
        "title": "Carleton Computer Science Society | Making a Balanced Course Schedule",
        "assertions": [
            "Making a Balanced Course Schedule",
            "Careful planning can help you create a timetable that supports your academic goals, fits your lifestyle, and keeps your workload manageable.",
            "Consider all the Possibilities",
            "Class Timing",
            "Lunch Time",
            "Rate My Prof",
            "No Schedule is Perfect",
            "[PDF: https://carleton.ca/registration/course-selection-guide/bcs/]"

            "this [Link: https://carleton.ca/registration/course-selection-guide/bcs/]",
            "Time Tickets [Link: https://carleton.ca/registration/dates/timetickets/]",
            "Waitlists [Link: https://carleton.ca/registration/waitlisting/]",
            "Academic Dates and Deadlines [Link: https://students.carleton.ca/academic-dates/]"
        ]
    }
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

test_pages()