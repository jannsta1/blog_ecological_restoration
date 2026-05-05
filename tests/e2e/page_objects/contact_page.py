from selenium.webdriver.common.by import By

from tests.e2e.page_objects.base_page import BasePage


class ContactPage(BasePage):
    EMAIL_INPUT = (By.ID, "id_email")
    SUBJECT_INPUT = (By.ID, "id_subject")
    MESSAGE_INPUT = (By.ID, "id_message")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, '[data-testid="contact-submit"]')
    SUCCESS_TITLE = (By.CSS_SELECTOR, '[data-testid="contact-success-title"]')
    CONTACT_TITLE = (By.CSS_SELECTOR, '[data-testid="contact-title"]')

    def open(self):
        self.visit("/contact/")

    def submit(self, email, subject, message):
        self.fill(self.EMAIL_INPUT, email)
        self.fill(self.SUBJECT_INPUT, subject)
        self.fill(self.MESSAGE_INPUT, message)
        self.click(self.SUBMIT_BUTTON)
