import random
import re

from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.variant_selects = page.locator("select:visible")
        self.variant_containers = page.locator(".vim.x-sku")
        self.add_to_cart_button = page.locator(
            "#atcBtn_btn_1, "
            "a[role='button']:has-text('Add to cart'), "
            "button:has-text('Add to cart')"
        ).first
        self.unavailable_message = page.get_by_text(
            re.compile(r"out of stock|unavailable|sold out", re.IGNORECASE)
        )

    def open_product(self, product_url: str) -> None:
        self.navigate(product_url)

    def select_available_variants(self) -> None:
        self._select_standard_select_variants()
        self._select_ebay_listbox_variants()
        self._select_button_variant_groups()

    def _select_standard_select_variants(self) -> None:
        for index in range(self.variant_selects.count()):
            variant_select = self.variant_selects.nth(index)

            if variant_select.is_disabled():
                continue

            if not self._is_product_variant_select(variant_select):
                continue

            available_values = self._get_available_option_values(variant_select)

            if available_values:
                variant_select.select_option(value=random.choice(available_values))

    def _select_ebay_listbox_variants(self) -> None:
        for index in range(self.variant_containers.count()):
            variant_container = self.variant_containers.nth(index)

            if not variant_container.is_visible():
                continue

            listbox_button = variant_container.locator(
                "button.listbox-button__control:visible"
            ).first

            if listbox_button.count() == 0:
                continue

            if "select" not in (listbox_button.inner_text()).lower():
                continue

            listbox_button.click()

            option = self._get_random_visible_listbox_option()

            if option is not None:
                option.click()

    def _select_button_variant_groups(self) -> None:
        for index in range(self.variant_containers.count()):
            variant_container = self.variant_containers.nth(index)

            if not variant_container.is_visible():
                continue

            if variant_container.locator(
                "button.listbox-button__control"
            ).count() > 0:
                continue

            option_buttons = variant_container.locator(
                "button[aria-pressed='false']:visible, "
                "[role='radio']:visible"
            )
            available_options: list[Locator] = []

            for option_index in range(option_buttons.count()):
                option_button = option_buttons.nth(option_index)

                if self._is_unavailable_button_option(option_button):
                    continue

                available_options.append(option_button)

            if available_options:
                random.choice(available_options).click()

    def add_to_cart(self) -> None:
        expect(self.add_to_cart_button).to_be_visible()
        expect(self.add_to_cart_button).to_be_enabled()

        self.add_to_cart_button.click()

        try:
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
        except PlaywrightTimeoutError as error:
            if self._product_is_unavailable():
                raise AssertionError(
                    "Product cannot be added because it is unavailable"
                ) from error

            raise AssertionError(
                "Add to cart did not reach a cart state or confirmation"
            ) from error

    @staticmethod
    def _is_product_variant_select(variant_select: Locator) -> bool:
        select_id = variant_select.get_attribute("id") or ""
        select_name = variant_select.get_attribute("name") or ""
        aria_label = variant_select.get_attribute("aria-label") or ""

        ignored_identifiers = (
            "gh-cat",
            "_sacat",
            "feedbackFilterDropdown",
            "Select a category for search",
        )

        return not any(
            ignored_identifier in {select_id, select_name, aria_label}
            for ignored_identifier in ignored_identifiers
        )

    @staticmethod
    def _get_available_option_values(variant_select: Locator) -> list[str]:
        available_values: list[str] = []
        options = variant_select.locator("option")

        for option_index in range(options.count()):
            option = options.nth(option_index)
            value = option.get_attribute("value")
            text = option.text_content() or ""

            if option.is_disabled():
                continue

            if not value:
                continue

            if value in {"-1", "0"}:
                continue

            if re.search(r"select|choose|please", text, flags=re.IGNORECASE):
                continue

            available_values.append(value)

        return available_values

    def _get_random_visible_listbox_option(self) -> Locator | None:
        visible_options = self.page.locator("[role='option']:visible")
        available_options: list[Locator] = []

        for index in range(visible_options.count()):
            option = visible_options.nth(index)

            if self._is_unavailable_listbox_option(option):
                continue

            available_options.append(option)

        if not available_options:
            return None

        return random.choice(available_options)

    @staticmethod
    def _is_unavailable_listbox_option(option: Locator) -> bool:
        option_text = option.inner_text()
        aria_disabled = option.get_attribute("aria-disabled")

        return bool(
            aria_disabled == "true"
            or re.search(
                r"select|choose|please|selected",
                option_text,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _is_unavailable_button_option(option_button: Locator) -> bool:
        option_text = option_button.inner_text()
        aria_disabled = option_button.get_attribute("aria-disabled")

        return bool(
            aria_disabled == "true"
            or option_button.is_disabled()
            or re.search(
                r"select|choose|please|sold out|unavailable",
                option_text,
                flags=re.IGNORECASE,
            )
        )

    def _product_is_unavailable(self) -> bool:
        if self.unavailable_message.count() == 0:
            return False

        return self.unavailable_message.first.is_visible()
