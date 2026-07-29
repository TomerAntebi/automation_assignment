import re
from urllib.parse import urlparse

from playwright.sync_api import Locator

from utils.price_parser import parse_price


PRODUCT_PRICE_XPATH = "xpath=.//*[contains(@class, 'price')]"
PRODUCT_LINK_XPATH = "xpath=.//a[contains(@href, '/itm/')]"
EBAY_ITEM_ID_PATTERN = re.compile(r"/itm/(?:[^/]+/)?(\d{9,})")


class SearchResultsCollector:
    def __init__(self, product_cards: Locator) -> None:
        self.product_cards = product_cards

    def collect_product_urls_from_current_page(
        self,
        collected_product_urls: list[str],
        maximum_price: float,
        product_limit: int,
    ) -> None:
        product_card_count = self.product_cards.count()

        for card_index in range(product_card_count):
            product_card = self.product_cards.nth(card_index)

            product_url = self._extract_valid_product_url(product_card, maximum_price)
            if not product_url or product_url in collected_product_urls:
                continue

            collected_product_urls.append(product_url)

            if len(collected_product_urls) >= product_limit:
                return

    def _extract_valid_product_url(self, product_card: Locator, maximum_price: float) -> str | None:
        product_card_text = product_card.text_content().lower() or ""
        if "sponsored" in product_card_text:
            return None

        product_price = self._extract_product_price(product_card)
        if product_price is None or product_price > maximum_price:
            return None

        return self._extract_ebay_product_url(product_card)


    def _extract_product_price(self, product_card: Locator) -> float | None:
        price_locator = product_card.locator(PRODUCT_PRICE_XPATH).first
        price_text = price_locator.text_content()

        if not price_text:
            return None

        try:
            return parse_price(price_text)
        except ValueError:
            return None

    def _extract_ebay_product_url(self, product_card: Locator) -> str | None:
        link_locator = product_card.locator(PRODUCT_LINK_XPATH).first
        raw_product_url = link_locator.get_attribute("href")

        if not raw_product_url:
            return None

        parsed_url = urlparse(raw_product_url)

        if not (
            parsed_url.scheme in {"http", "https"}
            and parsed_url.netloc.endswith("ebay.com")
            and "/itm/" in parsed_url.path
            and EBAY_ITEM_ID_PATTERN.search(parsed_url.path)
        ):
            return None

        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"