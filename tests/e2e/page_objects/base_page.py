from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, base_url, timeout=10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def visit(self, path):
        self.driver.get(f"{self.base_url}{path}")

    def click(self, locator):
        self.wait.until(ec.element_to_be_clickable(locator)).click()

    def fill(self, locator, value):
        element = self.wait.until(ec.presence_of_element_located(locator))
        element.clear()
        element.send_keys(value)

    def text_of(self, locator):
        element = self.wait.until(ec.visibility_of_element_located(locator))
        return element.text

    def is_visible(self, locator):
        elements = self.driver.find_elements(*locator)
        return bool(elements) and elements[0].is_displayed()
