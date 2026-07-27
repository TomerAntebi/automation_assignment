import re

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.price_parser import PriceParser


class CartPage(BasePage):
    CART_URL = "https://cart.ebay.com/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.cart_heading = page.get_by_role("heading", name="Cart").first
        self.subtotal_candidates = page.locator(
            "[data-test-id='SUBTOTAL'], "
            "[data-test-id='CART_SUBTOTAL'], "
            "[data-test-id*='subtotal' i]"
        )
        self.total_candidates = page.locator(
            "[data-test-id='CART_TOTAL'], "
            "[data-test-id='ORDER_TOTAL'], "
            "[data-test-id='TOTAL'], "
            "[data-test-id*='total' i]"
        )

    def open_cart(self) -> None:
        self.navigate(self.CART_URL)
        expect(self.cart_heading).to_be_visible()

    def get_cart_total(self) -> float:
        amount_text = self._find_visible_amount_text(self.subtotal_candidates)

        if amount_text is None:
            amount_text = self._find_visible_amount_text(self.total_candidates)

        if amount_text is None:
            raise AssertionError("No visible cart subtotal or total amount was found")

        return PriceParser.parse(amount_text)

    def assert_cart_total_not_exceeds(
        self,
        budget_per_item: float,
        items_count: int,
    ) -> None:
        self.open_cart()

        actual_cart_total = self.get_cart_total()
        maximum_allowed_total = budget_per_item * items_count
        self.save_screenshot("cart_summary")

        assert actual_cart_total <= maximum_allowed_total, (
            f"Cart total {actual_cart_total} exceeds "
            f"maximum allowed total {maximum_allowed_total}"
        )

    def _find_visible_amount_text(self, candidates: Locator) -> str | None:
        for index in range(candidates.count()):
            candidate = candidates.nth(index)

            if not candidate.is_visible():
                continue

            amount_text = self._find_amount_text_inside(candidate)

            if amount_text:
                return amount_text

        return None

    @staticmethod
    def _find_amount_text_inside(candidate: Locator) -> str | None:
        amount_elements = candidate.locator(
            "xpath=.//*[contains(text(), '$') "
            "or contains(text(), '€') "
            "or contains(text(), '£') "
            "or contains(text(), '₪') "
            "or contains(text(), 'USD') "
            "or contains(text(), 'ILS') "
            "or contains(text(), 'EUR') "
            "or contains(text(), 'GBP')]"
        )

        for index in range(amount_elements.count()):
            amount_element = amount_elements.nth(index)

            if not amount_element.is_visible():
                continue

            amount_text = amount_element.text_content()

            if amount_text and re.search(r"\d", amount_text):
                return amount_text

        candidate_text = candidate.text_content()

        if candidate_text and re.search(r"\d", candidate_text):
            return candidate_text

        return None
