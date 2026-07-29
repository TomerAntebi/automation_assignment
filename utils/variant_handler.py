import random
import re

from playwright.sync_api import Locator, expect


INVALID_TEXT_PATTERN = re.compile(r"select|choose|please|sold out|unavailable", re.IGNORECASE)
INVALID_OPTION_VALUES = {"", "-1", "0"}
VARIANT_CONTROL_SELECTOR = "xpath=.//button[contains(@class, 'listbox-button__control')]"
VARIANT_OPTION_SELECTOR = "xpath=.//*[@role='option']"


def select_variants(variant_groups: Locator) -> None:
    variant_groups_length = variant_groups.count()
    for index in range(variant_groups_length):
        variant_group = variant_groups.nth(index)

        if not variant_group.is_visible():
            continue

        variant_control = variant_group.locator(VARIANT_CONTROL_SELECTOR).first

        if not variant_control.is_visible():
            continue

        variant_control.click()

        options = variant_group.locator(VARIANT_OPTION_SELECTOR)
        expect(options.first).to_be_visible()
        valid_options = _get_valid_options(options)

        if not valid_options:
            continue

        random.choice(valid_options).click()


def _get_valid_options(options: Locator) -> list[Locator]:
    valid_options: list[Locator] = []
    options_length = options.count()
    for index in range(options_length):
        option = options.nth(index)

        if not _is_valid_option(option):
            continue

        valid_options.append(option)

    return valid_options


def _is_valid_option(option: Locator) -> bool:
    option_text = option.text_content() or ""

    if option.is_disabled() or option.get_attribute("aria-disabled") == "true":
        return False

    if INVALID_TEXT_PATTERN.search(option_text):
        return False

    return True
