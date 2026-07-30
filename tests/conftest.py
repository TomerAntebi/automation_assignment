import json
import logging
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


logger = logging.getLogger(__name__)


# -------------------------
# Test Data
# -------------------------
@pytest.fixture(scope="session")
def test_data() -> dict[str, Any]:
    data_path = Path("data/test_data.json")

    with data_path.open(mode="r", encoding="utf-8") as data_file:
        return json.load(data_file)


# -------------------------
# Browser Context
# -------------------------
@pytest.fixture
def browser_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        locale="en-US",
        viewport={"width": 1440, "height": 900},
    )

    try:
        yield context
    finally:
        context.close()


# -------------------------
# Page Fixture
# -------------------------
@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    page = browser_context.new_page()

    try:
        yield page
    finally:
        page.close()


# -------------------------
# Pytest Hook - Reporting
# -------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    test_name = item.name

    if report.passed:
        logger.info("TEST PASSED: %s", test_name)

    elif report.skipped:
        logger.warning(
            "TEST SKIPPED: %s | %s",
            test_name,
            report.longrepr,
        )

    elif report.failed:
        logger.error(
            "TEST FAILED: %s | %s",
            test_name,
            report.longrepr,
        )

        # -------------------------
        # Capture Screenshot
        # -------------------------
        page = item.funcargs.get("page", None)

        if page:
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)

            screenshot_path = screenshots_dir / f"{test_name}.png"

            try:
                page.screenshot(path=str(screenshot_path))
                logger.info("Screenshot saved: %s", screenshot_path)
            except Exception as e:
                logger.error("Failed to capture screenshot: %s", e)