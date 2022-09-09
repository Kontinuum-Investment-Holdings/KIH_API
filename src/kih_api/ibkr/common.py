from typing import Callable, Any

import kih_api
from kih_api import global_common, communication
from kih_api.communication import telegram
from kih_api.ibkr.models import IBKR


def job(job_name: str, is_run_only_when_market_is_open: bool = False, symbol_to_check_market_open: str = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        @global_common.job(job_name)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            if not is_run_only_when_market_is_open or (is_run_only_when_market_is_open and IBKR.is_market_open(symbol_to_check_market_open)):
                func(*args, **kwargs)
            else:
                telegram.send_message(
                    telegram.constants.telegram_channel_username, f"Market is not open; job skipped: <i>{job_name}</i>", True)

        return wrapper

    return decorator
