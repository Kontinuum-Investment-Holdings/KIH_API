import os

from kih_api import global_common

IP_ADDRESS_INFO_ENDPOINT: str = "http://ip-api.com/json/"
ENVIRONMENT: str = "DEV" if global_common.get_environment_variable("ENV") is None else global_common.get_environment_variable("ENV")
