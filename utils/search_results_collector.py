import re
from urllib.parse import urlparse

from playwright.sync_api import Locator

from utils.price_parser import PriceParser


PRICE_XPATH = "xpath=.//*[contains(@class, 'price')]"
PRODUCT_LINK_XPATH = "xpath=.//a[contains(@href, '/itm/')]"
ITEM_ID_PATTERN = re.compile(r"/itm/(?:[^/]+/)?(\d{9,})")


class SearchResultsCollector:
    def __init__(self, result_items: Locator) -> None:
        self.result_items = result_items

    def collect_current_page(
        self,
        urls: list[str],
        seen: set[str],
        max_price: float,
        limit: int,
    ) -> None:
        count = self.result_items.count()

        for i in range(count):
            item = self.result_items.nth(i)

            product = self._extract_product(item, max_price)
            if not product or product in seen:
                continue

            urls.append(product)
            seen.add(product)

            if len(urls) >= limit:
                return

    def _extract_product(self, item: Locator, max_price: float) -> str | None:
        text = item.text_content().lower() or ""
        if "sponsored" in text:
            return None

        price = self._get_price(item)
        if price is None or price > max_price:
            return None

        return self._get_valid_product_url(item)


    def _get_price(self, item: Locator) -> float | None:
        locator = item.locator(PRICE_XPATH).first
        text = locator.text_content()

        if not text:
            return None

        try:
            return PriceParser.parse(text)
        except ValueError:
            return None

    def _get_valid_product_url(self, item: Locator) -> str | None:
        locator = item.locator(PRODUCT_LINK_XPATH).first
        url = locator.get_attribute("href")

        if not url:
            return None

        parsed = urlparse(url)

        if not (
            parsed.scheme in {"http", "https"}
            and parsed.netloc.endswith("ebay.com")
            and "/itm/" in parsed.path
            and ITEM_ID_PATTERN.search(parsed.path)
        ):
            return None

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"