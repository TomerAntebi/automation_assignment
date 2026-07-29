import re


def parse_price(price_text: str) -> float:
    if not price_text:
        raise ValueError("Price text cannot be empty")

    normalized_text = price_text.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", normalized_text)

    if match is None:
        raise ValueError(f"Could not parse price from: {price_text}")

    return float(match.group())
