import os

from kih_api import global_common

ENDPOINT_BASE: str = "https://paper-api.alpaca.markets"
API_KEY: str = global_common.get_environment_variable("ALPACA_API_KEY")
API_SECRET: str = global_common.get_environment_variable("ALPACA_API_SECRET")
