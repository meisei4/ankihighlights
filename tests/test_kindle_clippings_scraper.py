import json

from selenium import webdriver
import kindle_clippings_scraper

email = "example@gmail.com"
password = "something"


def init_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')  # Run Firefox in headless mode, without opening a window
    driver = webdriver.Firefox(options=options)
    return driver


def test_connect_to_clippings():
    driver = init_driver()
    kindle_clippings_scraper.connect_to_clippings(driver, email, password)
    expected_title = "Kindle: メモとハイライト"
    assert driver.title == expected_title


def test_scrape_all_annotations_per_book():
    driver = init_driver()
    kindle_clippings_scraper.connect_to_clippings(driver, email, password)
    annotations_per_book = kindle_clippings_scraper.scrape_all_annotations_per_book(driver)
    for annotations in annotations_per_book:
        pretty_str = json.dumps(annotations, indent=4, ensure_ascii=False)
        print(pretty_str + "\n")
    assert len(annotations_per_book) > 0
