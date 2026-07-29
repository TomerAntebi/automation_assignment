from playwright.sync_api import expect


def expect_visible(locator, message: str, timeout: int = 5000):
    try:
        expect(locator).to_be_visible(timeout=timeout)
    except AssertionError as e:
        raise AssertionError(message) from e

def expect_enabled(locator, message: str, timeout: int = 5000):
    try:
        expect(locator).to_be_enabled(timeout=timeout)
    except AssertionError as e:
        raise AssertionError(message) from e


def expect_text(locator, expected_text: str, message: str, timeout: int = 5000):
    try:
        expect(locator).to_contain_text(expected_text, timeout=timeout)
    except AssertionError as e:
        raise AssertionError(message) from e


def expect_url(page, expected: str, message: str, timeout: int = 5000):
    try:
        expect(page).to_have_url(expected, timeout=timeout)
    except AssertionError as e:
        raise AssertionError(message) from e
