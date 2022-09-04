import os

IP_ADDRESS_INFO_ENDPOINT: str = "http://ip-api.com/json/"
ENVIRONMENT: str = "DEV" if os.getenv("ENV") is None else os.getenv("ENV")
