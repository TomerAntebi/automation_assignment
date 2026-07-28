import random
import re

from playwright.sync_api import Locator, expect


INVALID_TEXT_PATTERN = re.compile(
    r"select|choose|please|sold out|unavailable",
    re.IGNORECASE,
)
INVALID_OPTION_VALUES = {"", "-1", "0"}
VARIANT_DROPDOWN_BUTTON_SELECTOR = "button.listbox-button__control:visible"
VARIANT_OPTION_SELECTOR = "[role='option']:visible"


class VariantHandler:
    def __init__(self, variant_groups: Locator) -> None:
        self.variant_groups = variant_groups

    def select_variants(self) -> None:
        for index in range(self.variant_groups.count()):
            variant_group = self.variant_groups.nth(index)

            if not variant_group.is_visible():
                continue

            dropdown_button = variant_group.locator(
                VARIANT_DROPDOWN_BUTTON_SELECTOR
            ).first

            if not dropdown_button.is_visible():
                continue

            if "select" not in dropdown_button.inner_text().lower():
                continue

            dropdown_button.click()

            options = variant_group.locator(VARIANT_OPTION_SELECTOR)
            expect(options.first).to_be_visible()
            valid_options = self._get_valid_options(options)

            if not valid_options:
                continue

            random.choice(valid_options).click()

    @staticmethod
    def _get_valid_options(options: Locator) -> list[Locator]:
        valid_options: list[Locator] = []

        for index in range(options.count()):
            option = options.nth(index)
            option_text = option.text_content() or ""
            option_value = option.get_attribute("value")

            if option.is_disabled() or option.get_attribute("aria-disabled") == "true":
                continue

            if INVALID_TEXT_PATTERN.search(option_text):
                continue

            if option_value in INVALID_OPTION_VALUES:
                continue

            valid_options.append(option)

        return valid_options
