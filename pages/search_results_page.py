import re
from urllib.parse import urlparse

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.price_parser import PriceParser


class SearchResultsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.search_input = page.locator("input[name='_nkw']").first
        self.search_button = page.locator("#gh-search-btn, input#gh-btn").first
        self.result_items = page.locator(
            "xpath=//li[contains(@class, 's-item') or contains(@class, 's-card')]"
        )
        self.maximum_price_input = page.locator(
            "input[aria-label*='Maximum']"
        ).first
        self.price_filter_submit = page.locator(
            "button[aria-label='Submit price range']"
        ).first
        self.next_page = page.locator(
            "a.pagination__next, "
            "a[aria-label='Next page'], "
            "a[aria-label='Go to next search page']"
        ).first

    def search_items_by_name_under_price(
        self,
        query: str,
        max_price: float,
        limit: int,
    ) -> list[str]:
        if limit <= 0:
            return []

        self._search_by_query(query)
        self._confirm_query_context(query)
        self._apply_maximum_price_filter(max_price)

        collected_urls: list[str] = []
        collected_set: set[str] = set()
        visited_pages: set[str] = set()

        while len(collected_urls) < limit:
            current_page_url = self.page.url

            if current_page_url in visited_pages:
                break

            visited_pages.add(current_page_url)
            self._collect_urls_from_current_page(
                max_price=max_price,
                limit=limit,
                collected_urls=collected_urls,
                collected_set=collected_set,
            )

            if len(collected_urls) >= limit:
                break

            if not self._go_to_next_page():
                break

        return collected_urls

    def _search_by_query(self, query: str) -> None:
        if self.search_input.count() == 0 or not self.search_input.is_visible():
            raise AssertionError("Search input is not visible on the current page")

        if self.search_button.count() == 0 or not self.search_button.is_visible():
            raise AssertionError("Search button is not visible on the current page")

        self.search_input.fill(query)
        self.search_button.click()
        self.page.wait_for_load_state("domcontentloaded")

    def _confirm_query_context(self, query: str) -> None:
        if self.search_input.count() == 0:
            return

        if not self.search_input.is_visible():
            return

        current_query = self.search_input.input_value()

        if query.lower() not in current_query.lower():
            raise AssertionError(
                f"Current search query '{current_query}' does not match '{query}'"
            )

    def _apply_maximum_price_filter(self, max_price: float) -> None:
        if self.maximum_price_input.count() == 0:
            return

        if not self.maximum_price_input.is_visible():
            return

        self.maximum_price_input.fill(str(max_price))

        if (
            self.price_filter_submit.count() > 0
            and self.price_filter_submit.is_visible()
            and self.price_filter_submit.is_enabled()
        ):
            self.price_filter_submit.click()
        else:
            self.maximum_price_input.press("Enter")

        self.page.wait_for_load_state("domcontentloaded")

    def _collect_urls_from_current_page(
        self,
        max_price: float,
        limit: int,
        collected_urls: list[str],
        collected_set: set[str],
    ) -> None:
        for index in range(self.result_items.count()):
            item = self.result_items.nth(index)

            if self._is_sponsored_item(item.inner_text()):
                continue

            price_locator = item.locator(".s-item__price, .s-card__price").first
            link_locator = item.locator(
                "a.s-item__link[href*='/itm/'], "
                "a.s-card__link[href*='/itm/']"
            ).first

            if price_locator.count() == 0 or link_locator.count() == 0:
                continue

            price_text = price_locator.text_content()
            product_url = link_locator.get_attribute("href")

            if not price_text or not product_url:
                continue

            try:
                item_price = PriceParser.parse(price_text)
            except ValueError:
                continue

            if item_price > max_price:
                continue

            normalized_product_url = self._normalize_product_url(product_url)

            if not self._is_valid_product_url(normalized_product_url):
                continue

            if normalized_product_url in collected_set:
                continue

            collected_urls.append(normalized_product_url)
            collected_set.add(normalized_product_url)

            if len(collected_urls) >= limit:
                break

    def _go_to_next_page(self) -> bool:
        if self.next_page.count() == 0:
            return False

        if not self.next_page.is_visible():
            return False

        if not self.next_page.is_enabled():
            return False

        if self.next_page.get_attribute("aria-disabled") == "true":
            return False

        previous_url = self.page.url
        next_page_url = self.next_page.get_attribute("href")

        if not next_page_url:
            return False

        self.page.goto(next_page_url, wait_until="domcontentloaded")

        return self.page.url != previous_url

    @staticmethod
    def _is_sponsored_item(item_text: str) -> bool:
        return "sponsored" in item_text.lower()

    @staticmethod
    def _normalize_product_url(product_url: str) -> str:
        parsed_url = urlparse(product_url)

        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    @staticmethod
    def _is_valid_product_url(product_url: str) -> bool:
        parsed_url = urlparse(product_url)
        host = parsed_url.netloc.lower()
        item_id_match = re.search(r"/itm/(?:[^/]+/)?(\d{9,})", parsed_url.path)

        return bool(
            parsed_url.scheme in {"http", "https"}
            and host.endswith("ebay.com")
            and item_id_match
        )
