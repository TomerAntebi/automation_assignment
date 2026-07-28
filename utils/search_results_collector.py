import re
from urllib.parse import urlparse

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from utils.price_parser import PriceParser


PRICE_XPATH = "xpath=.//*[contains(@class, 'price')]"
PRODUCT_LINK_XPATH = "xpath=.//a[contains(@href, '/itm/')]"
ITEM_ID_PATTERN = re.compile(r"/itm/(?:[^/]+/)?(\d{9,})")


class SearchResultsCollector:
    def __init__(self, page: Page, result_items: Locator, next_page: Locator) -> None:
        self.page = page
        self.result_items = result_items
        self.next_page = next_page

    def collect_urls(self, max_price: float, limit: int) -> list[str]:
        collected_urls: list[str] = []
        collected_set: set[str] = set()
        visited_pages: set[str] = set()

        while len(collected_urls) < limit:
            current_page_url = self.page.url
            if current_page_url in visited_pages:
                break

            visited_pages.add(current_page_url)
            self._collect_urls_from_current_page(limit, collected_urls, collected_set)
            if len(collected_urls) >= limit:
                break
            if not self._go_to_next_page():
                break

        return collected_urls

    def _collect_urls_from_current_page(
        self, limit: int, collected_urls: list[str], collected_set: set[str]
    ) -> None:
        for index in range(self.result_items.count()):
            item = self.result_items.nth(index)
            if self._is_sponsored_item(item.inner_text()):
                continue
            item_price = self._extract_item_price(item)
            if item_price is None:
                continue
            product_url = self._extract_product_url(item)
            if product_url is None:
                continue
            valid_product_url = self._normalize_valid_product_url(product_url)
            if valid_product_url is None:
                continue
            if valid_product_url in collected_set:
                continue

            collected_urls.append(valid_product_url)
            collected_set.add(valid_product_url)

            if len(collected_urls) >= limit:
                break

    def _go_to_next_page(self) -> bool:
        if not self.next_page.is_visible():
            return False
        if not self.next_page.is_enabled():
            return False
        if self.next_page.get_attribute("aria-disabled") == "true":
            return False

        previous_url = self.page.url
        self.next_page.click()
        try:
            self.page.wait_for_function(
                "previousUrl => window.location.href !== previousUrl",
                arg=previous_url,
                timeout=10000,
            )
        except PlaywrightTimeoutError:
            return False

        self.page.wait_for_load_state("domcontentloaded")
        return self.page.url != previous_url

    @staticmethod
    def _is_sponsored_item(item_text: str) -> bool:
        return "sponsored" in item_text.lower()

    @staticmethod
    def _extract_item_price(item: Locator) -> float | None:
        price_locator = item.locator(PRICE_XPATH).first
        if not price_locator.is_visible():
            return None
        price_text = price_locator.text_content()
        if not price_text:
            return None
        try:
            return PriceParser.parse(price_text)
        except ValueError:
            return None

    @staticmethod
    def _extract_product_url(item: Locator) -> str | None:
        link_locator = item.locator(PRODUCT_LINK_XPATH).first
        if not link_locator.is_visible():
            return None
        return link_locator.get_attribute("href")

    @staticmethod
    def _normalize_valid_product_url(product_url: str) -> str | None:
        parsed_url = urlparse(product_url)
        normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        if not SearchResultsCollector._is_valid_product_url(normalized_url):
            return None
        return normalized_url

    @staticmethod
    def _is_valid_product_url(product_url: str) -> bool:
        parsed_url = urlparse(product_url)
        host = parsed_url.netloc.lower()
        return bool(
            parsed_url.scheme in {"http", "https"}
            and (host == "ebay.com" or host.endswith(".ebay.com"))
            and "/itm/" in parsed_url.path
            and ITEM_ID_PATTERN.search(parsed_url.path)
        )
