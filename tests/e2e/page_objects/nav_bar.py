from selenium.webdriver.common.by import By

from tests.e2e.page_objects.base_page import BasePage


class NavBar(BasePage):
    BLOG_POSTS_LINK = (By.CSS_SELECTOR, '[data-testid="nav-blog-posts"]')
    CONTACT_LINK = (By.CSS_SELECTOR, '[data-testid="nav-contact"]')
    LOGIN_LINK = (By.CSS_SELECTOR, '[data-testid="nav-login"]')
    UPLOAD_LINK = (By.CSS_SELECTOR, '[data-testid="nav-upload-post"]')

    def go_to_blog_listing(self):
        self.click(self.BLOG_POSTS_LINK)

    def go_to_contact(self):
        self.click(self.CONTACT_LINK)

    def go_to_login(self):
        self.click(self.LOGIN_LINK)

    def go_to_upload(self):
        self.click(self.UPLOAD_LINK)
