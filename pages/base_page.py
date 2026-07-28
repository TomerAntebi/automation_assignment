from pathlib import Path

from playwright.sync_api import Page

SEARCH_INPUT_SELECTOR = "input[name='_nkw']"
SEARCH_BUTTON_SELECTOR = "#gh-search-btn, input#gh-btn"
class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def save_screenshot(self, name: str) -> Path:
        screenshot_directory = Path("screenshots")
        screenshot_directory.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_directory / f"{name}.png"

        self.page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        return screenshot_path
