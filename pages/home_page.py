from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from pages.base_page import SEARCH_INPUT_SELECTOR, SEARCH_BUTTON_SELECTOR

class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.search_input = page.locator(SEARCH_INPUT_SELECTOR)
        self.search_button = page.locator(SEARCH_BUTTON_SELECTOR).first

    def authenticate_as_guest(self) -> None:
        expect(self.search_input).to_be_visible()
        expect(self.search_input).to_be_enabled()

    def search(self, query: str) -> None:
        expect(self.search_input).to_be_visible()
        self.search_input.fill(query)
        self.search_button.click()
        self.page.wait_for_load_state("domcontentloaded")
