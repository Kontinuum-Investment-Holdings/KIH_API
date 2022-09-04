#   Telegram API
import os

telegram_url = "https://api.telegram.org/bot<token>/"
telegram_bot_token = os.getenv("KIH_API_TELEGRAM_BOT_TOKEN")
telegram_bot_username = "kontinuum_bot"
telegram_channel_username = os.getenv("TELEGRAM_BOT_USERNAME")
telegram_channel_development_username = os.getenv("TELEGRAM_BOT_DEV_USERNAME")
telegram_stocks_data_template = "${Stock}: ${Stock-Price} | ${Stock-PriceChange}"
telegram_currencies_data_template = "${CurrencyPair}: ${ExchangeRate} | ${ExchangeRateChange}"

#   Telegram API - Methods
telegram_method_get_chat_id = "getChat"
telegram_method_send_message = "sendMessage"
