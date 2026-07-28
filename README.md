# eBay E2E Automation Assignment

## Overview

This project implements an end-to-end automation scenario for eBay.

The test searches for products by name, applies a maximum price filter, collects product URLs, adds available products to the cart, and validates that the cart item total does not exceed the configured budget.

## Assignment Requirements Covered

- Playwright automation with Python
- Object Oriented Programming
- Page Object Model
- Data-driven input from JSON
- Allure reporting
- Product search with max price condition
- Paging support when fewer results are found on the current page
- Random available variant selection
- Add items to cart flow
- Cart total validation
- Screenshots and runtime logs

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
  home_page.py
  search_results_page.py
  product_page.py
  cart_page.py

utils/
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

The project follows the Page Object Model and keeps responsibilities separated:

- `HomePage` handles opening eBay and continuing as guest.
- `SearchResultsPage` handles search and filter URL building.
- `SearchResultsCollector` collects product URLs from search result pages.
- `ProductPage` opens products, selects variants, and adds items to the cart.
- `VariantHandler` selects available eBay listbox variants.
- `CartPage` reads and validates the cart item total.
- `PriceParser` extracts numeric prices from UI text.

The test file owns the end-to-end flow, Allure steps, logging, screenshots, and final assertions.

## Main Test Flow

1. Open eBay.
2. Continue as guest.
3. Search for the configured product query.
4. Apply max price and Buy It Now filters.
5. Collect up to `items_limit` product URLs.
6. Open each product page.
7. Select required variants randomly from available options.
8. Click `Add to cart`.
9. Validate that the cart item total does not exceed:

   ```text
   max_price * number_of_collected_urls
   ```

10. Attach screenshots and Allure report artifacts.

## Test Data

The test is data-driven. Input is stored in `data/test_data.json`:

```json
{
  "base_url": "https://www.ebay.com",
  "search_query": "puma shoes",
  "max_price": 400,
  "items_limit": 2
}
```

## Prerequisites

- Python 3.11 or newer
- Chromium installed through Playwright
- Allure command-line tool to open reports locally

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

Run with visible browser:

```bash
pytest --headed
```

The project enables live pytest logs through `pytest.ini`.

## Allure Report

Pytest writes Allure results to:

```text
reports/allure-results
```

Open the report:

```bash
allure serve reports/allure-results
```

## Screenshots And Logs

- Product screenshots are saved after successful add-to-cart actions.
- Cart screenshot is attached during final cart validation.
- Pytest logs show search input, collected URLs count, skipped products, added products, and final test status.

## Assumptions

- Guest mode is used.
- No real login credentials are required.
- The cart item total is validated without shipping costs.
- No currency conversion is performed.
- Variant selection uses eBay's visible listbox dropdown.
- Some products can become unavailable between search collection and add-to-cart.

## Limitations

- eBay is a live external website, so DOM structure, prices, experiments, dialogs, and product availability may change.
- eBay may request human verification. This should be treated as an external blocker, not an automation failure.
- The test does not validate checkout, payment, shipping address, taxes, product titles, or inventory.
- The test is intended for an automation assignment scenario, not production monitoring of eBay.
