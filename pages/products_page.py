from urllib.parse import urlencode

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.assertions import expect_visible
from utils.search_results_collector import SearchResultsCollector


RESULT_ITEMS_SELECTOR = "xpath=//li[contains(@class, 's-item') or contains(@class, 's-card')]"
NEXT_PAGE_SELECTOR = "xpath=//a[contains(@class, 'pagination__next')]"


class ProductsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.product_cards = page.locator(RESULT_ITEMS_SELECTOR)
        self.next_page = page.locator(NEXT_PAGE_SELECTOR).first
        self.results_collector = SearchResultsCollector(product_cards=self.product_cards)

    def search_items_by_name_under_price(self, query: str, max_price: float, limit: int = 5) -> list[str]:
        if limit <= 0 or max_price <= 0:
            return []

        url = self._build_search_url(query, max_price)

        self.page.goto(url, wait_until="domcontentloaded")
        expect_visible(self.product_cards.first, "Search results did not load", timeout=10000)

        product_urls: list[str] = []

        while len(product_urls) < limit:
            self.results_collector.collect_product_urls_from_current_page(product_urls, max_price, limit)
            if len(product_urls) >= limit or not self._go_to_next_page():
                break

        return product_urls

    def _build_search_url(self, query: str, max_price: float) -> str:
        params = {
            "_nkw": query,
            "_udhi": f"{max_price:g}",  # max price
            "LH_BIN": "1",              # buy it now only
            "_currency": "USD",         # force USD (best effort)
        }

        return f"{self.base_url}/sch/i.html?{urlencode(params)}"

    def _go_to_next_page(self) -> bool:
        if not self.next_page.is_visible():
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

        return True
