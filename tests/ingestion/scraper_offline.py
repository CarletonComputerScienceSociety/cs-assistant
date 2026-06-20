from pathlib import Path

from src.ingestion.scrapers.html_scraper import _extract_from_html

FIXTURES = Path(__file__).parent / "fixtures"

# run with python -m tests.ingestion.scraper_offline


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_bcyber_page():
    html = load_fixture("courseTest.html")

    text, title = _extract_from_html(html)

    assert title == "Courses and Registration (B.Cyber.) - School of Computer Science"
    assert "Electives and Prohibited Courses" in text
    assert "Skip to Main Content" not in text

    # Optional if your extraction removes nav correctly
    assert "Search this website" not in text

    assert "[PDF:" in text

    assert (
        "[PDF: https://carleton.ca/scs/wp-content/uploads/BCyber-Course-Map-202630-3.pdf]" in text
    )

    assert (
        "[PDF: https://carleton.ca/scs/wp-content/uploads/FINAL2-BCyber-Course-Map-202530.pdf]"
        in text
    )


def test_new_student_faq():
    html = load_fixture("faqTest.html")

    text, title = _extract_from_html(html)

    question = "How do I build a timetable?"
    answer = "Log into Carleton Central"
    assert question in text
    assert answer in text

    question = "How do I build a timetable?"
    answer = "Log into Carleton Central"
    assert text.index(question) < text.index(answer)

    assert "How do I view my grades or exam schedule" in text

    # Use a phrase that appears in that answer block
    assert "Information about how to view your grades or exam schedule" in text
    assert "Skip to Main Content" not in text


test_new_student_faq()
test_bcyber_page()
