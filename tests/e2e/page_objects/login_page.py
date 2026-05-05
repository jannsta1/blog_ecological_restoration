from selenium.webdriver.common.by import By

from tests.e2e.page_objects.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "id_username")
    PASSWORD_INPUT = (By.ID, "id_password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, '[data-testid="login-submit"]')

    def open(self):
        self.visit("/login/")

    def login(self, username, password):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
