from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.search_results_collector import SearchResultsCollector


BUY_IT_NOW_FILTER_PARAMETER = "LH_BIN"
BUY_IT_NOW_FILTER_VALUE = "1"
MAXIMUM_PRICE_FILTER_PARAMETER = "_udhi"
SEARCH_FILTER_PARAMETERS = {MAXIMUM_PRICE_FILTER_PARAMETER,BUY_IT_NOW_FILTER_PARAMETER}


class SearchResultsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.search_input = page.locator("input[name='_nkw']").first
        self.search_button = page.locator("#gh-search-btn, input#gh-btn").first
        self.result_items = page.locator(
            "xpath=//li[contains(@class, 's-item') or contains(@class, 's-card')]"
        )
        self.next_page = page.locator("a.pagination__next").first
        self.search_results_collector = SearchResultsCollector(
            page=page,
            result_items=self.result_items,
            next_page=self.next_page,
        )

    def search_items_by_name_under_price(
        self,
        query: str,
        max_price: float,
        limit: int = 5,
    ) -> list[str]:
        if limit <= 0:
            return []

        self._search_by_query(query)
        self._confirm_query_context(query)
        self.page.goto(
            self.build_query_url(max_price),
            wait_until="domcontentloaded",
        )

        return self.search_results_collector.collect_urls(
            max_price=max_price,
            limit=limit,
        )

    def _search_by_query(self, query: str) -> None:
        expect(self.search_input).to_be_visible()
        expect(self.search_button).to_be_visible()

        self.search_input.fill(query)
        self.search_button.click()
        self.page.wait_for_load_state("domcontentloaded")

    def _confirm_query_context(self, query: str) -> None:
        if not self.search_input.is_visible():
            return

        current_query = self.search_input.input_value()

        if query.lower() not in current_query.lower():
            raise AssertionError(
                f"Current search query '{current_query}' does not match '{query}'"
            )

    def build_query_url(self, max_price: float) -> str:
        parsed_url = urlparse(self.page.url)
        existing_parameters = parse_qsl(
            parsed_url.query,
            keep_blank_values=True,
        )

        filtered_parameters = [
            parameter
            for parameter in existing_parameters
            if parameter[0] not in SEARCH_FILTER_PARAMETERS
        ]
        filtered_parameters.extend(
            [
                (MAXIMUM_PRICE_FILTER_PARAMETER, f"{max_price:g}"),
                (BUY_IT_NOW_FILTER_PARAMETER, BUY_IT_NOW_FILTER_VALUE),
            ]
        )

        return urlunparse(
            parsed_url._replace(query=urlencode(filtered_parameters))
        )
