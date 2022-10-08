#   Telegram API
import os

from kih_api import global_common

telegram_url = "https://api.telegram.org/bot<token>/"
telegram_bot_token = global_common.get_environment_variable("KIH_API_TELEGRAM_BOT_TOKEN")
telegram_bot_username = "kontinuum_bot"
telegram_channel_username = global_common.get_environment_variable("TELEGRAM_CHANNEL_USERNAME") if global_common.get_environment() == global_common.Environment.PROD else global_common.get_environment_variable("TELEGRAM_CHANNEL_DEBUG_USERNAME")
telegram_debug_channel_username = global_common.get_environment_variable("TELEGRAM_CHANNEL_DEBUG_USERNAME")
telegram_stocks_data_template = "${Stock}: ${Stock-Price} | ${Stock-PriceChange}"
telegram_currencies_data_template = "${CurrencyPair}: ${ExchangeRate} | ${ExchangeRateChange}"

#   Telegram API - Methods
telegram_method_get_chat_id = "getChat"
telegram_method_send_message = "sendMessage"
