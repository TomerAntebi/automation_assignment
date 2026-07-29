import logging
import time 
from pathlib import Path
from typing import Any

import allure
import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage


logger = logging.getLogger(__name__)


def add_items_to_cart(page: Page, product_page: ProductPage, product_urls: list[str]) -> None:
    search_page_url = page.url

    for index, product_url in enumerate(product_urls, start=1):
        with allure.step(f"Add product {index} to cart"):
            logger.info("Opening product %s/%s: %s", index, len(product_urls), product_url)

            try:
                product_page.open_product(product_url)
                product_page.select_variants()
                product_page.add_to_cart()
            except AssertionError as error:
                if "unavailable" not in str(error).lower():
                    raise

                logger.warning("Skipping product %s: %s", index, error)
                allure.attach(
                    str(error),
                    name=f"product_{index}_not_added",
                    attachment_type=allure.attachment_type.TEXT,
                )
                page.goto(search_page_url, wait_until="domcontentloaded")
                continue

            screenshot_path = product_page.save_screenshot(f"added_product_{index}")
            logger.info("Product %s added to cart successfully", index)

            allure.attach.file(
                str(screenshot_path),
                name=f"added_product_{index}",
                attachment_type=allure.attachment_type.PNG,
            )

            page.goto(search_page_url, wait_until="domcontentloaded")


@allure.feature("eBay shopping")
@allure.story("Search and add products under budget")
def test_ebay_purchase_flow(page: Page, test_data: dict[str, Any]) -> None:
    base_url = str(test_data["base_url"])
    search_query = str(test_data["search_query"])
    max_price = float(test_data["max_price"])
    items_limit = int(test_data["items_limit"])

    home_page = HomePage(page)
    search_results_page = SearchResultsPage(page)
    product_page = ProductPage(page)
    cart_page = CartPage(page)

    with allure.step("Open eBay"):
        logger.info("Opening eBay: %s", base_url)
        home_page.navigate(base_url)

    with allure.step("Continue as guest"):
        logger.info("Continuing as guest")
        home_page.authenticate_as_guest()

    with allure.step(f"Search for {search_query} and collect products under {max_price}"):
        logger.info("Searching query='%s', max_price=%s, limit=%s", search_query, max_price, items_limit)
        product_urls = search_results_page.search_items_by_name_under_price(query=search_query, max_price=max_price, limit=items_limit)
        logger.info("Collected %s product URLs", len(product_urls))

    if not product_urls:
        skip_reason = f"No matching products found for query='{search_query}', max_price={max_price}, limit={items_limit}"
        logger.warning(skip_reason)
        pytest.skip(skip_reason)

    add_items_to_cart(page=page, product_page=product_page, product_urls=product_urls)
    time.sleep(10)

    with allure.step("Validate cart total"):
        logger.info("Validating cart total with budget_per_item=%s, items_count=%s", max_price, len(product_urls))
        cart_page.assert_cart_total_not_exceeds(budget_per_item=max_price, items_count=len(product_urls))

    with allure.step("Attach cart screenshot"):
        cart_screenshot = Path("screenshots/cart_summary.png")
        logger.info("Attaching cart screenshot: %s", cart_screenshot)

        allure.attach.file(
            str(cart_screenshot),
            name="cart_summary",
            attachment_type=allure.attachment_type.PNG,
        )
