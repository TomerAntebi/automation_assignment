import re

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.assertions import expect_visible, expect_enabled
from utils.variant_handler import select_variants

ADD_TO_CART_BUTTON_SELECTOR = "xpath=//*[@id='atcBtn_btn_1']"
VARIANT_GROUP_SELECTOR = "xpath=//*[contains(@class, 'vim') and contains(@class, 'x-sku')]"


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.variant_groups = page.locator(VARIANT_GROUP_SELECTOR)
        self.add_to_cart_button = page.locator(ADD_TO_CART_BUTTON_SELECTOR).first
        self.unavailable_message = page.get_by_text(re.compile(r"out of stock|unavailable|sold out", re.IGNORECASE))

    def open_product(self, product_url: str) -> None:
        self.navigate(product_url)

    def select_variants(self) -> None:
        select_variants(self.variant_groups)

    def add_to_cart(self) -> None:
        expect_visible(self.add_to_cart_button, "Add to cart button is not visible")
        expect_enabled(self.add_to_cart_button, "Add to cart button is not enabled")

        self.add_to_cart_button.click()
        self.page.wait_for_function(
            """
            () => {
                const pageText = document.body.innerText.toLowerCase();
                const currentUrl = window.location.href.toLowerCase();

                return currentUrl.includes("cart")
                    || pageText.includes("added to cart")
                    || pageText.includes("successfully added");
            }
            """,
            timeout=15000,
        )

    def is_product_unavailable(self) -> bool:
        return self.unavailable_message.first.is_visible()
