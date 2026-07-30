# 📄 AI Generated Code Review

This document reviews the provided AI-generated Playwright test and highlights **four key issues**, including explanation and corrected code.

---

## Issue 1: Usage of `time.sleep()` causes unstable tests

### Problematic code:

```python
time.sleep(2)
time.sleep(3)
```

### Explanation:

Using fixed delays makes the test **flaky and non-deterministic**.
If the page loads slower than expected, the test may fail.
If it loads faster, the test becomes unnecessarily slow.

Playwright provides built-in waiting mechanisms, so manual sleeps should not be used.

### Corrected code:

```python
from playwright.sync_api import expect

results = page.locator(".result-item")
expect(results.first).to_be_visible()
```

---

## Issue 2: Missing assertions – test does not validate behavior

### Problematic code:

```python
results = page.locator(".result-item")
```

### Explanation:

The code creates a locator but **does not verify anything**.
This means the test will pass even if no results are displayed.

A valid test must assert expected behavior. Without assertions, this is not a real test but only a script.

### Corrected code:

```python
results = page.locator(".result-item")

expect(results.first).to_be_visible()
assert results.count() > 0
```

---

## Issue 3: Incorrect Playwright lifecycle management

### Problematic code:

```python
browser = sync_playwright().start().chromium.launch()
page = browser.new_page()
```

### Explanation:

Playwright is started manually but **never properly stopped**.
Only the browser is closed, while the Playwright process remains unmanaged.

This can lead to resource leaks and unstable execution.

### Corrected code:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.goto("https://example.com")

    browser.close()
```

---

## Issue 4: Button locator is too generic and unreliable

### Problematic code:

```python
page.locator(".button").click()
```

### Explanation:

The selector is too generic and may match multiple elements.
This can lead to clicking the wrong button and cause flaky or incorrect test behavior.

Selectors should be **specific and stable**, ideally based on role, name, or unique attributes.

### Corrected code:

```python
search_button = page.get_by_role("button", name="Search")
search_button.click()
```

---

# 🏆 Corrected Full Code

```python
from playwright.sync_api import expect, sync_playwright


def test_search_functionality() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto("https://example.com")

        search_box = page.locator("#search")
        expect(search_box).to_be_visible()
        search_box.fill("playwright testing")

        search_button = page.get_by_role("button", name="Search")
        search_button.click()

        results = page.locator(".result-item")
        expect(results.first).to_be_visible()
        assert results.count() > 0

        browser.close()
```

---
