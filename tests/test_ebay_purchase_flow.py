import logging
from pathlib import Path
from typing import Any

import allure
import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.cart_page import CartPage
from pages.product_page import ProductPage
from pages.products_page import ProductsPage


logger = logging.getLogger(__name__)


def add_items_to_cart(
    page: Page,
    product_page: ProductPage,
    product_urls: list[str],
) -> int:
    search_page_url = page.url
    added_items = 0

    for index, product_url in enumerate(product_urls, start=1):
        with allure.step(f"Add product {index} to cart"):
            logger.info(
                "Opening product %s/%s: %s",
                index,
                len(product_urls),
                product_url,
            )

            try:
                product_page.open_product(product_url)
                product_page.select_variants()
                product_page.add_to_cart()

            except (AssertionError, PlaywrightTimeoutError) as error:
                if product_page.is_product_unavailable():
                    logger.warning("Skipping unavailable product %s", index)

                    allure.attach(
                        "Product is unavailable",
                        name=f"product_{index}_skipped",
                        attachment_type=allure.attachment_type.TEXT,
                    )

                    page.goto(search_page_url, wait_until="domcontentloaded")
                    continue

                raise AssertionError(
                    f"Failed to add product {index} to cart: {error}"
                ) from error

            added_items += 1

            screenshot_path = product_page.save_screenshot(
                f"added_product_{index}"
            )

            logger.info("Product %s added successfully", index)

            allure.attach.file(
                str(screenshot_path),
                name=f"added_product_{index}",
                attachment_type=allure.attachment_type.PNG,
            )

            page.goto(search_page_url, wait_until="domcontentloaded")

    return added_items


def assert_cart_total_not_exceeds(
    cart_page: CartPage,
    budget_per_item: float,
    items_count: int,
) -> None:
    logger.info(
        "Opening cart. budget_per_item=%s, items_count=%s",
        budget_per_item,
        items_count,
    )

    try:
        cart_page.open_cart()
    except AssertionError as error:
        pytest.fail(f"Cart page did not load: {error}", pytrace=False)

    actual_total = cart_page.get_cart_total()
    expected_max = budget_per_item * items_count

    logger.info(
        "Cart total: actual=%s, expected_max=%s",
        actual_total,
        expected_max,
    )

    cart_page.save_screenshot("cart_summary")

    if actual_total > expected_max:
        pytest.fail(
            f"Cart total {actual_total} exceeds allowed {expected_max}",
            pytrace=False,
        )


@allure.feature("eBay shopping")
@allure.story("Search and add products under budget")
def test_ebay_purchase_flow(page: Page, test_data: dict[str, Any]) -> None:
    base_url = test_data["base_url"]
    search_query = test_data["search_query"]
    max_price = float(test_data["max_price"])
    items_limit = int(test_data["items_limit"])

    products_page = ProductsPage(page)
    product_page = ProductPage(page)
    cart_page = CartPage(page)

    with allure.step("Open eBay"):
        logger.info("Opening site: %s", base_url)
        products_page.navigate(base_url)

    with allure.step("Search products"):
        logger.info(
            "Searching query='%s', max_price=%s, limit=%s",
            search_query,
            max_price,
            items_limit,
        )

        product_urls = products_page.search_items_by_name_under_price(
            query=search_query,
            max_price=max_price,
            limit=items_limit,
        )

    with allure.step("Validate results"):
        if not product_urls:
            message = (
                f"No products found for query='{search_query}', "
                f"max_price={max_price}, limit={items_limit}"
            )
            logger.warning(message)
            pytest.skip(message)

    with allure.step("Add items to cart"):
        added_count = add_items_to_cart(
            page=page,
            product_page=product_page,
            product_urls=product_urls,
        )

        if added_count == 0:
            pytest.fail("No products were added to cart")

        logger.info("Added %s/%s products", added_count, len(product_urls))

    with allure.step("Validate cart total"):
        assert_cart_total_not_exceeds(
            cart_page=cart_page,
            budget_per_item=max_price,
            items_count=added_count,
        )

    with allure.step("Attach cart screenshot"):
        screenshot_path = Path("screenshots/cart_summary.png")

        allure.attach.file(
            str(screenshot_path),
            name="cart_summary",
            attachment_type=allure.attachment_type.PNG,
        )