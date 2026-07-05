from selenium.webdriver.common.by import By

from tests.e2e.page_objects.base_page import BasePage


class UploadPostPage(BasePage):
    FORM = (By.CSS_SELECTOR, '[data-testid="upload-post-form"]')
    TITLE_INPUT = (By.ID, "id_title")
    DATE_INPUT = (By.ID, "id_date")
    CONTENT_INPUT = (By.ID, "id_content")
    ADD_GPS_BUTTON = (By.CSS_SELECTOR, '[data-testid="add-gps-btn"]')
    STAGE_ONE_SUBMIT_BUTTON = (By.CSS_SELECTOR, '[data-testid="upload-stage-1-submit"]')
    STAGE_TWO_SUBMIT_BUTTON = (By.CSS_SELECTOR, '[data-testid="upload-stage-2-submit"]')
    STAGE_THREE_SUBMIT_BUTTON = (
        By.CSS_SELECTOR,
        '[data-testid="upload-stage-3-submit"]',
    )
    STAGE_FOUR_SUBMIT_BUTTON = (
        By.CSS_SELECTOR,
        '[data-testid="upload-stage-4-submit"]',
    )
    GPS_LAT_INPUT = (By.NAME, "gps-0-latitude")
    GPS_LON_INPUT = (By.NAME, "gps-0-longitude")
    GPS_ALT_INPUT = (By.NAME, "gps-0-altitude")

    def open(self):
        self.visit("/upload-post/")

    def fill_stage_one(self, title, date):
        self.fill(self.TITLE_INPUT, title)
        self.fill(self.DATE_INPUT, date)

    def fill_content(self, content):
        self.fill(self.CONTENT_INPUT, content)

    def save_stage_one(self):
        self.click(self.STAGE_ONE_SUBMIT_BUTTON)

    def save_content(self):
        self.click(self.STAGE_THREE_SUBMIT_BUTTON)

    def save_photos_and_locations(self):
        self.click(self.STAGE_FOUR_SUBMIT_BUTTON)

    def add_gps_row(self, latitude, longitude, altitude):
        self.click(self.ADD_GPS_BUTTON)
        self.fill(self.GPS_LAT_INPUT, latitude)
        self.fill(self.GPS_LON_INPUT, longitude)
        self.fill(self.GPS_ALT_INPUT, altitude)
