from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


# TODO this is unusable because it doesnt actually have vocab data, only highlights

def connect_to_clippings(driver_injection, email, password):
    driver_injection.get("https://read.amazon.co.jp/notebook")

    email_field = driver_injection.find_element(By.ID, "ap_email")
    email_field.send_keys(email)

    password_field = driver_injection.find_element(By.ID, "ap_password")
    password_field.send_keys(password)

    signin_button = driver_injection.find_element(By.ID, "signInSubmit")
    signin_button.click()


def scrape_book_titles(driver_injection):
    return driver_injection.find_elements(By.XPATH, "//span[contains(@data-action, 'get-annotations-for-asin')]")


def click_on_a_book_and_wait_for_annotations_to_show_up(driver_injection, book):
    driver_injection.execute_script("arguments[0].click();", book)
    pane_class = "aok-hidden"
    WebDriverWait(driver_injection, 10).until(
        lambda driver: pane_class in driver.find_element(By.ID, "kp-notebook-annotations-pane").get_attribute(
            "class"))
    WebDriverWait(driver_injection, 10).until(
        lambda driver: pane_class not in driver.find_element(By.ID, "kp-notebook-annotations-pane").get_attribute(
            "class"))


def scrape_all_annotations_per_book(driver_injection):
    books = scrape_book_titles(driver_injection)
    annotations_per_book = []
    for book in books:
        try:
            click_on_a_book_and_wait_for_annotations_to_show_up(driver_injection, book)
        except TimeoutException:
            print(f"Timeout occurred while waiting for annotations to show up for book {book.text}, skipping...")
            continue
        annotations_div = driver_injection.find_elements(By.ID, "kp-notebook-annotations")
        annotations = annotations_div[0].find_elements(By.XPATH, ".//*[@id='highlight']")
        annotations_per_book.append({book.text: [annotation.text for annotation in annotations]})

    return annotations_per_book
