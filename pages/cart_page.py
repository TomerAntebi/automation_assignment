from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.assertions import expect_visible
from utils.price_parser import parse_price

CART_URL = "https://cart.ebay.com/"

CART_ORDER_SUMMARY_SELECTOR = ("xpath=//div[@data-test-id='cart-summary']")
CART_ITEM_TOTAL_SELECTOR = "xpath=.//*[@data-test-id='ITEM_TOTAL']"


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.cart_order_summary = page.locator(CART_ORDER_SUMMARY_SELECTOR).first
        self.cart_item_total = page.locator(CART_ITEM_TOTAL_SELECTOR).first

    def open_cart(self) -> None:
        self.navigate(CART_URL)
        expect_visible(self.cart_order_summary, "Cart page did not load")

    def get_cart_total(self) -> float:
        expect_visible(self.cart_item_total, "Cart subtotal is not visible")

        cart_total = parse_price(self.cart_item_total.inner_text())
        return cart_total
