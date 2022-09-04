import os
import sys
from typing import Dict

from kih_api import global_common

environment_variables: Dict[str, str] = {"KIH_API_TELEGRAM_BOT_TOKEN": "telegram bot token",
                                         "TELEGRAM_BOT_USERNAME": "Telegram bot username",
                                         "KIH_API_EMAIL_ACCOUNT": "outgoing email address",
                                         "KIH_API_EMAIL_ACCOUNT_PASSWORD": "email address' password",
                                         "TRANSFER_WISE_API_KEY": "TransferWise API Key",
                                         "ALPACA_API_KEY": "Alpaca API Key",
                                         "ALPACA_API_SECRET": "Alpaca API Secret",
                                         "MONGO_DB_URI": "The Mongo DB URL",
                                         "ENV": "The current environment"}


def set_environment_variable(key: str, value: str) -> None:
    if value == "":
        return
    elif sys.platform == "win32":
        global_common.run_command(["setx " + key + " \"" + value.replace("\"", "") + "\""])
    elif sys.platform == "linux":
        global_common.run_command([f"echo \"export {key}=\"{value}\" >> ~/.bash_profile"])
        global_common.run_command(["source ~/.bash_profile"])


if __name__ == "__main__":
    set_environment_variable("PYTHONPATH", os.getcwd())
    for key in environment_variables.keys():
        value: str = input("Enter the " + environment_variables[key] + ":")
        set_environment_variable(key, value)

print("\n\n----------------------------------------------------------------------------------")
print("Setup completed")
print("----------------------------------------------------------------------------------")
