import json
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def test_data() -> dict[str, Any]:
    data_path = Path("data/test_data.json")

    with data_path.open(mode="r", encoding="utf-8") as data_file:
        return json.load(data_file)


@pytest.fixture
def browser_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        locale="en-US",
        viewport={
            "width": 1440,
            "height": 900,
        },
    )

    yield context

    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    page = browser_context.new_page()

    yield page

    page.close()
