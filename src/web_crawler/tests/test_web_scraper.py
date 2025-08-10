import pytest

pytest.skip("requires Chrome driver and network access", allow_module_level=True)

from web_crawler.web_scraper import WebScraper

scraper = WebScraper()

scraper.navigate_sync("https://mweiden.github.io")


def test_extract_raw_data():
    raw_data = scraper.extract_raw_data()
    assert "title" in raw_data
    assert len(raw_data) > 0


def test_extract_rendered_text():
    text = scraper.extract_rendered_text()
    assert (
        text
        == """
Matt Weiden
info
code
projects
learning
writing
About me
I’m an Engineering Manager at Cruise Automation on the Machine Learning Platform team.""".lstrip()
    )


def test_find_element():
    link = scraper.find_element("a")
    assert link.text == "Matt Weiden"


def test_find_all_links():
    links = scraper.find_all_links()
    expected = [
        "https://getcruise.com/",
        "https://github.com/mweiden",
        "https://mweiden.github.io/",
        "https://mweiden.github.io/#",
        "https://mweiden.github.io/pages/code/closed_source/",
        "https://mweiden.github.io/pages/code/open_source/",
        "https://mweiden.github.io/pages/info/pgp/",
        "https://mweiden.github.io/pages/learning/reads/",
        "https://mweiden.github.io/pages/learning/research/",
        "https://mweiden.github.io/pages/projects/arbeit/",
        "https://mweiden.github.io/pages/projects/p5.js",
        "https://mweiden.github.io/pages/projects/reclaimed_spaces/",
        "https://mweiden.github.io/pages/projects/tree.js",
        "https://mweiden.github.io/pages/projects/tree/",
        "https://mweiden.github.io/pages/writing/2017-09-27-deliver-software-faster/",
        "https://www.linkedin.com/in/matt-weiden/",
    ]
    assert set(links) == set(expected)
    assert len(links) == len(expected)
