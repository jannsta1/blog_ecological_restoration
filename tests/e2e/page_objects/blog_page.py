from selenium.webdriver.common.by import By

from tests.e2e.page_objects.base_page import BasePage


class BlogPage(BasePage):
    PAGE_TITLE = (By.CSS_SELECTOR, '[data-testid="blog-listing-title"]')
    POST_CARDS = (By.CSS_SELECTOR, '[data-testid="post-card"]')
    FIRST_POST_LINK = (
        By.CSS_SELECTOR,
        '[data-testid="post-card"] [data-testid="post-detail-link"]',
    )

    def open(self):
        self.visit("/blog-listing/")

    def post_count(self):
        self.wait.until(lambda d: d.find_elements(*self.POST_CARDS))
        return len(self.driver.find_elements(*self.POST_CARDS))

    def open_first_post(self):
        self.click(self.FIRST_POST_LINK)
