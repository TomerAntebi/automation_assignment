# eBay E2E Automation Assignment

## Overview

This project contains a Python Playwright end-to-end test for an eBay purchase flow.

The test opens eBay, searches for products under a configured maximum price, collects product URLs, adds available products to the cart, and validates that the cart total does not exceed the configured budget.

## Technologies

- Python
- Playwright synchronous API
- Pytest
- pytest-playwright
- Allure Pytest
- JSON test data

## Project Structure

```text
data/
  test_data.json

pages/
  base_page.py
  products_page.py
  product_page.py
  cart_page.py

utils/
  assertions.py
  price_parser.py
  search_results_collector.py
  variant_handler.py

tests/
  conftest.py
  test_ebay_purchase_flow.py

reports/
  allure-results/

screenshots/

pytest.ini
requirements.txt
README.md
ReadMeAIBugs.md
```

## Architecture

The project uses a small Page Object Model:

- `BasePage` stores the shared Playwright `page`, base URL, navigation, and screenshot behavior.
- `ProductsPage` builds the eBay search URL, navigates search results, and collects product URLs.
- `ProductPage` opens a product, selects variants, adds the product to the cart, and exposes unavailable-product state.
- `CartPage` opens the cart and reads the cart total.

Utility modules keep parsing and selection logic outside the page objects:

- `assertions.py` wraps selected Playwright assertions with short error messages.
- `search_results_collector.py` extracts valid eBay product URLs from result cards.
- `price_parser.py` parses numeric prices from UI text.
- `variant_handler.py` selects available product variants.

The test file owns the end-to-end scenario, Allure steps, logging, screenshots, and final test assertions.

## Main Test Flow

1. Open eBay.
2. Search for products using `search_query`, `max_price`, and `items_limit` from `data/test_data.json`.
3. Validate that at least one product URL was collected, otherwise skip the test.
4. Open each collected product URL.
5. Select required product variants.
6. Add available products to the cart.
7. Skip products that become unavailable.
8. Save screenshots for successfully added products.
9. Validate that the cart total does not exceed:

   ```text
   max_price * number_of_collected_urls
   ```

10. Attach the cart screenshot to the Allure report.

## Test Data

The test input is stored in `data/test_data.json`:

```json
{
  "base_url": "https://www.ebay.com",
  "search_query": "",
  "max_price": 100,
  "items_limit": 1
}
```

Update `search_query`, `max_price`, and `items_limit` to control the products collected by the test.

## Pytest Fixtures

`tests/conftest.py` provides:

- `test_data`: loads `data/test_data.json`.
- `browser_context`: creates a Playwright browser context with `en-US` locale and `1440x900` viewport.
- `page`: creates and closes a Playwright page for each test.
- `pytest_runtest_makereport`: logs passed, skipped, and failed test results.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run Tests

```bash
pytest
```

Run with a visible browser:

```bash
pytest --headed
```

`pytest.ini` configures:

- test discovery under `tests`
- verbose test output
- Allure result output to `reports/allure-results`
- live CLI logs at `INFO` level

## Allure Report

Pytest writes Allure results to:

```text
reports/allure-results
```

Open the report locally:

```bash
allure serve reports/allure-results
```

## Screenshots And Logs

- Successful add-to-cart product screenshots are saved under `screenshots/`.
- The final cart screenshot is saved as `screenshots/cart_summary.png`.
- Screenshots are attached to the Allure report.
- Logs include search parameters, collected URL count, unavailable products, added products, cart total values, and test status.

## Assumptions

- The flow runs as a guest user.
- No login credentials are required.
- Cart validation uses the item total visible in the cart.
- Shipping, taxes, checkout, and payment are not validated.
- Product prices and availability can change because eBay is a live external site.
- Some products may become unavailable after being collected from search results.

## Limitations

- eBay DOM structure, experiments, prices, and availability may change.
- eBay may show human verification or regional dialogs.
- Variant selection depends on visible eBay listbox controls.
- The test is intended for an automation assignment, not production monitoring.
