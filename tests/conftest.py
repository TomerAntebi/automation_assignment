import json
import logging
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_data() -> dict[str, Any]:
    data_path = Path("data/test_data.json")

    with data_path.open(mode="r", encoding="utf-8") as data_file:
        return json.load(data_file)


@pytest.fixture
def browser_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        locale="en-US",
        timezone_id="America/New_York",  
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9"  
        },
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.passed:
        logger.info("TEST PASSED: %s", item.name)
    elif report.skipped:
        logger.warning("TEST SKIPPED: %s | %s", item.name, report.longrepr)
    elif report.failed:
        logger.error("TEST FAILED: %s", item.name)
