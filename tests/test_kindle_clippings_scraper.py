import json
import pytest
import kindle_clippings_scraper
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver


email = "example@gmail.com"
password = "something"


@pytest.fixture(scope='module')
def test_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')  # Run Firefox in headless mode, without opening a window
    driver = webdriver.Firefox(options=options)
    yield driver


@pytest.mark.skip(reason="to run this test you must update the email and password to be valid login creds")
def test_scrape_all_annotations_per_book(test_driver: WebDriver):
    kindle_clippings_scraper.connect_to_clippings(test_driver, email, password)
    expected_title = "Kindle: メモとハイライト"
    assert test_driver.title == expected_title

    annotations_per_book = kindle_clippings_scraper.scrape_all_annotations_per_book(test_driver)
    for annotations in annotations_per_book:
        pretty_str = json.dumps(annotations, indent=4, ensure_ascii=False)
        print(pretty_str + "\n")
    assert len(annotations_per_book) > 0
