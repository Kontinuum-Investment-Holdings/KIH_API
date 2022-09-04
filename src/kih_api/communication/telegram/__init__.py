from kih_api.communication.telegram import constants
from kih_api.logger import logger

url = constants.telegram_url.replace("<token>", constants.telegram_bot_token) + constants.telegram_method_send_message


def send_message(username: str, message_text: str, is_html: bool = False) -> None:
    if username[0:1] != "@":
        username = "@" + username

    parameters = {"chat_id": username, "text": message_text}
    if is_html:
        parameters.update({"parse_mode": "HTML"})

    global url
    from kih_api import http_requests
    response = http_requests.post(url, parameters)

    if response.status_code >= 300:
        logger.error("Telegram message sending failed: " + response.json()["description"])
