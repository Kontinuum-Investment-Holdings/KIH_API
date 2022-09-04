import alpaca_trade_api

from kih_api.alpaca import constants

alpaca_api = alpaca_trade_api.REST(
    constants.API_KEY,
    constants.API_SECRET,
    constants.ENDPOINT_BASE
)
