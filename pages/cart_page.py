from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.price_parser import PriceParser

CART_URL = "https://cart.ebay.com/"

CART_ORDER_SUMMARY_SELECTOR = ("xpath=//div[@data-test-id='cart-summary']")
CART_ITEM_TOTAL_SELECTOR = "xpath=.//*[@data-test-id='ITEM_TOTAL']"


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.cart_order_summary = page.locator(CART_ORDER_SUMMARY_SELECTOR).first
        self.cart_item_total = page.locator(CART_ITEM_TOTAL_SELECTOR).first

    def open_cart(self) -> None:
        self.navigate(self.CART_URL)
        expect(self.cart_order_summary).to_be_visible()

    def get_cart_total(self) -> float:
        try:
            expect(self.cart_item_total).to_be_visible()
        except AssertionError as error:
            raise AssertionError(
                "Cart item total element not found or not visible"
            ) from error

        return PriceParser.parse(self.cart_item_total.inner_text())

    def assert_cart_total_not_exceeds(self, budget_per_item: float, items_count: int) -> None:
        self.open_cart()

        actual_cart_total = self.get_cart_total()
        maximum_allowed_total = budget_per_item * items_count
        self.save_screenshot("cart_summary")

        assert actual_cart_total <= maximum_allowed_total, (
            f"Cart total {actual_cart_total} exceeds "
            f"maximum allowed total {maximum_allowed_total}"
        )
