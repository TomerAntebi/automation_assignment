# Project overview

This project implements one end-to-end automation scenario for eBay. The test searches for products, applies a maximum price condition, collects matching product URLs, adds available products to the cart, and validates that the displayed cart amount does not exceed the configured budget.

# Technologies

- Python
- Playwright synchronous API
- Pytest
- pytest-playwright
- Allure Pytest
- JSON

# Project structure

```text
data/
  test_data.json
pages/
  base_page.py
  home_page.py
  search_results_page.py
  product_page.py
  cart_page.py
tests/
  conftest.py
  test_ebay_purchase_flow.py
utils/
  price_parser.py
screenshots/
  .gitkeep
reports/
  .gitkeep
requirements.txt
pytest.ini
README.md
ReadMeAIBugs.md
.gitignore
```

# Prerequisites

- Python 3.11 or newer
- Chromium browser installed through Playwright
- Allure command-line tool installed locally to open the report with `allure serve`

# Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

# Execution

```bash
pytest
pytest --headed
```

# Allure report

Pytest writes Allure results to `reports/allure-results`.

```bash
allure serve reports/allure-results
```

# Architecture

The project uses Object Oriented Programming and the Page Object Model. Page classes contain locators and page-specific actions. The test file contains the end-to-end flow, test data usage, Allure steps, screenshot attachments, and final assertions.

# Test data

External data driven input is stored in `data/test_data.json`.

The file contains:

- `base_url`
- `search_query`
- `max_price`
- `items_limit`
- `currency`

# Assumptions

- Guest mode is used.
- No real authentication credentials are required.
- The Guest mode authentication method confirms that the shopping flow can continue without signing in.
- Cart subtotal is used when shipping and taxes are displayed separately.
- No currency conversion is performed.
- Random variant selection is required by the assignment.

# Limitations

- eBay is a live external website, so DOM structure, experiments, regional behavior, dialogs, prices, and product availability may change.
- Some collected products may become unavailable before they are added to the cart.
- The test does not validate checkout, payment, shipping, taxes, product titles, inventory, or currency conversion.
