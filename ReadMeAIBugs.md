# AI Generated Code Review

This document reviews the problematic AI-generated automation example from the assignment and shows focused corrections using Playwright synchronous API only.

## Issue 1: Selenium import mixes frameworks

Problematic code:

```python
from selenium import webdriver
```

Explanation:

The implementation uses Playwright, so importing Selenium is unused and mixes two separate browser automation frameworks. The assignment explicitly requires Playwright and does not require Selenium.

Corrected code:

```python
from playwright.sync_api import expect, sync_playwright
```

## Issue 2: Playwright lifecycle is not managed correctly

Problematic code:

```python
playwright = sync_playwright().start()
browser = playwright.chromium.launch()
```

Explanation:

Starting Playwright manually without a context manager requires explicitly stopping the Playwright instance. If the code closes only the browser, the Playwright process is left unmanaged.

Corrected code:

```python
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    browser.close()
```

## Issue 3: Manually started Playwright instance is never stopped

Problematic code:

```python
playwright = sync_playwright().start()
browser = playwright.chromium.launch()
browser.close()
```

Explanation:

The browser is closed, but `playwright.stop()` is never called. A context manager avoids this cleanup problem.

Corrected code:

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()

    try:
        page = browser.new_page()
    finally:
        browser.close()
```

## Issue 4: Fixed sleeps make the test unreliable

Problematic code:

```python
time.sleep(3)
```

Explanation:

A fixed wait can be too short on a slow page and unnecessarily slow on a fast page. Playwright should wait for a specific page condition.

Corrected code:

```python
results = page.locator(".result-item")
expect(results.first).to_be_visible()
```

## Issue 5: Generic button locator may click the wrong element

Problematic code:

```python
page.locator("button").click()
```

Explanation:

A generic button selector may match any button on the page. The test should target the intended action with a stable role, name, or attribute.

Corrected code:

```python
search_button = page.get_by_role("button", name="Search")
search_button.click()
```

## Issue 6: Result locator is created but not validated

Problematic code:

```python
results = page.locator(".result-item")
```

Explanation:

Creating a locator does not validate anything. The test can pass even when no results are shown.

Corrected code:

```python
results = page.locator(".result-item")
expect(results.first).to_be_visible()
assert results.count() > 0
```

## Issue 7: Test has no meaningful assertion

Problematic code:

```python
page.fill("#search", "shoes")
page.locator("button").click()
```

Explanation:

The code performs actions but does not verify the expected result. A test must assert the outcome that matters.

Corrected code:

```python
results = page.locator(".result-item")
expect(results.first).to_be_visible()
assert results.count() > 0
```

## Issue 8: Browser cleanup is not protected

Problematic code:

```python
browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("https://example.com")
browser.close()
```

Explanation:

If navigation or an assertion fails, `browser.close()` may never run. Cleanup should be protected with `try` and `finally`, or handled by a context manager and test fixtures.

Corrected code:

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()

    try:
        page = browser.new_page()
        page.goto("https://example.com")
    finally:
        browser.close()
```

## Issue 9: Example site may not contain the referenced elements

Problematic code:

```python
page.goto("https://example.com")
page.fill("#search", "shoes")
```

Explanation:

`example.com` is a placeholder page and may not contain a search field. The test should navigate to the actual website under test or use selectors that exist on the chosen page.

Corrected code:

```python
page.goto("https://www.ebay.com", wait_until="domcontentloaded")
search_input = page.locator("input[name='_nkw']")
expect(search_input).to_be_visible()
search_input.fill("shoes")
```

## Corrected minimal Playwright example

```python
from playwright.sync_api import expect, sync_playwright


def test_search_functionality() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto("https://example.com")
        page.fill("#search", "shoes")
        page.locator("button").click()

        results = page.locator(".result-item")
        expect(results.first).to_be_visible()
        assert results.count() > 0

        browser.close()
```
