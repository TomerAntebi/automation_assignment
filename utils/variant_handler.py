import random
import re

from playwright.sync_api import Locator, expect


INVALID_TEXT_PATTERN = re.compile(
    r"select|choose|please|sold out|unavailable",
    re.IGNORECASE,
)


class VariantHandler:
    def __init__(self, variant_groups: Locator) -> None:
        self.variant_groups = variant_groups

    def select_variants(self) -> None:
        for index in range(self.variant_groups.count()):
            variant_group = self.variant_groups.nth(index)

            if not variant_group.is_visible():
                continue

            self._select_from_listbox(variant_group)

    def _select_from_listbox(self, variant_group: Locator) -> bool:
        listbox_button = variant_group.locator(
            "button.listbox-button__control:visible"
        ).first

        if not listbox_button.is_visible():
            return False

        if "select" not in listbox_button.inner_text().lower():
            return False

        listbox_button.click()

        options = variant_group.locator("[role='option']:visible")
        expect(options.first).to_be_visible()
        valid_options = self._get_valid_options(options)

        if not valid_options:
            return False

        random.choice(valid_options).click()

        return True

    @staticmethod
    def _get_valid_options(options: Locator) -> list[Locator]:
        valid_options: list[Locator] = []

        for index in range(options.count()):
            option = options.nth(index)
            option_text = option.text_content() or ""
            option_value = option.get_attribute("value")

            if VariantHandler._is_disabled(option):
                continue

            if VariantHandler._is_invalid_text(option_text):
                continue

            if option_value in {"", "-1", "0"}:
                continue

            valid_options.append(option)

        return valid_options

    @staticmethod
    def _is_invalid_text(text: str) -> bool:
        return bool(INVALID_TEXT_PATTERN.search(text))

    @staticmethod
    def _is_disabled(option: Locator) -> bool:
        return bool(
            option.is_disabled()
            or option.get_attribute("aria-disabled") == "true"
        )
