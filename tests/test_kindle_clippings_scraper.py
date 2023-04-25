from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver

import kindle_clippings_scraper


def init_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')  # Run Firefox in headless mode, without opening a window
    driver = FirefoxWebDriver(options=options)
    return driver


def test_connect_to_clippings():
    driver = init_driver()
    kindle_clippings_scraper.connect_to_clippings(driver, "ha", "ha")
    expected_title = "Kindle: メモとハイライト"
    assert driver.title == expected_title


def test_scrape_clippings():
    driver = init_driver()
    kindle_clippings_scraper.connect_to_clippings(driver, "ha", "ha")
    highlights = kindle_clippings_scraper.scrape_clippings(driver)
    print(highlights)
    assert len(highlights) > 0
