import threading
from decimal import Decimal
from typing import Dict, Any, Optional

threads: Dict[Any, threading.Thread] = {}


def get_number_from_text_with_suffixes(number: str) -> Optional[Decimal]:
    if number.replace(".", "").isnumeric():
        return Decimal(number)

    value: Decimal = Decimal(number.replace(number[-1], "").replace(",", ""))
    if number.upper().endswith("K"):
        return value * Decimal("1000")
    elif number.upper().endswith("M"):
        return value * Decimal("1000") * Decimal("1000")
    elif number.upper().endswith("B"):
        return value * Decimal("1000") * Decimal("1000") * Decimal("1000")
    elif number.upper().endswith("T"):
        return value * Decimal("1000") * Decimal("1000") * Decimal("1000")

    return None


def get_html_commented(error_html: str) -> str:
    if "<!DOCTYPE".lower() in error_html.lower():
        return "<!--" + error_html + "-->"
    else:
        return error_html
