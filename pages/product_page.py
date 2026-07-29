import re

from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

from pages.base_page import BasePage
from utils.variant_handler import VariantHandler

ADD_TO_CART_BUTTON_SELECTOR = "xpath=//*[@id='atcBtn_btn_1']"
VARIANT_GROUP_SELECTOR = "xpath=//*[contains(@class, 'vim') and contains(@class, 'x-sku')]"


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.variant_handler = VariantHandler(page.locator(VARIANT_GROUP_SELECTOR))
        self.add_to_cart_button = page.locator(ADD_TO_CART_BUTTON_SELECTOR).first
        self.unavailable_message = page.get_by_text(
            re.compile(r"out of stock|unavailable|sold out", re.IGNORECASE)
        )

    def open_product(self, product_url: str) -> None:
        self.navigate(product_url)

    def select_variants(self) -> None:
        self.variant_handler.select_variants()

    def add_to_cart(self) -> None:
        try:
            expect(self.add_to_cart_button).to_be_visible()
            expect(self.add_to_cart_button).to_be_enabled()

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
        except (AssertionError, PlaywrightTimeoutError) as error:
            if self._product_is_unavailable():
                raise AssertionError(
                    "Product cannot be added because it is unavailable"
                ) from error

            raise AssertionError(
                "Add to cart did not reach a cart state or confirmation"
            ) from error

    def _product_is_unavailable(self) -> bool:
        return self.unavailable_message.first.is_visible()
