from selenium.webdriver.common.by import By

from tests.e2e.page_objects.base_page import BasePage


class UploadPostPage(BasePage):
    FORM = (By.CSS_SELECTOR, '[data-testid="upload-post-form"]')
    TITLE_INPUT = (By.ID, "id_title")
    DATE_INPUT = (By.ID, "id_date")
    CONTENT_INPUT = (By.ID, "id_content")
    ADD_GPS_BUTTON = (By.CSS_SELECTOR, '[data-testid="add-gps-btn"]')
    GPS_LAT_INPUT = (By.NAME, "gps-0-latitude")
    GPS_LON_INPUT = (By.NAME, "gps-0-longitude")
    GPS_ALT_INPUT = (By.NAME, "gps-0-altitude")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, '[data-testid="upload-submit"]')

    def open(self):
        self.visit("/upload-post/")

    def fill_required_fields(self, title, date, content):
        self.fill(self.TITLE_INPUT, title)
        self.fill(self.DATE_INPUT, date)
        self.fill(self.CONTENT_INPUT, content)

    def add_gps_row(self, latitude, longitude, altitude):
        self.click(self.ADD_GPS_BUTTON)
        self.fill(self.GPS_LAT_INPUT, latitude)
        self.fill(self.GPS_LON_INPUT, longitude)
        self.fill(self.GPS_ALT_INPUT, altitude)

    def submit(self):
        self.click(self.SUBMIT_BUTTON)
