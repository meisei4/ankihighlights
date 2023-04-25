from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def connect_to_clippings(driver_injection, email, password):
    driver_injection.get("https://read.amazon.co.jp/notebook")

    email_field = driver_injection.find_element(By.ID, "ap_email")
    email_field.send_keys(email)

    password_field = driver_injection.find_element(By.ID, "ap_password")
    password_field.send_keys(password)

    signin_button = driver_injection.find_element(By.ID, "signInSubmit")
    signin_button.click()


def scrape_clippings(driver_injection):
    books = driver_injection.find_elements_by_xpath("//span[contains(@data-action, 'get-annotations-for-asin')]")

    for book in books:
        driver_injection.execute_script("arguments[0].click();", book)
        # wait for the annotations to become available
        # does this only check if a-row is the class or can it be "a-row aok-hidden"
        WebDriverWait(driver_injection, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='kp-notebook-annotations-pane'][contains(@class,'a-row')]")))

    annotations_div = driver_injection.find_element_by_id("kp-notebook-annotations")
    highlight_elements = annotations_div.find_elements_by_xpath(".//*[@id='highlight']")
    highlights = [highlight_element.text for highlight_element in highlight_elements]

    return highlights
