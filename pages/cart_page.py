from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.price_parser import PriceParser


CART_HEADING_SELECTOR = "h1.cart-title"
CART_ITEM_TOTAL_SELECTOR = "[data-test-id='ITEM_TOTAL']"

class CartPage(BasePage):
    CART_URL = "https://cart.ebay.com/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.cart_heading = page.locator(CART_HEADING_SELECTOR).first
        self.cart_item_total = page.locator(CART_ITEM_TOTAL_SELECTOR).first

    def open_cart(self) -> None:
        self.navigate(self.CART_URL)
        expect(self.cart_heading).to_be_visible()

    def get_cart_total(self) -> float:
        try:
            expect(self.cart_item_total).to_be_visible()
        except AssertionError as error:
            raise AssertionError(
                "Cart item total element not found or not visible"
            ) from error

        return PriceParser.parse(self.cart_item_total.inner_text())

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
