from kih_api import global_common
from kih_api.wise import constants


def override_api_key(api_key_environmental_variable_key: str) -> None:
    constants.API_KEY = global_common.get_environment_variable(api_key_environmental_variable_key)
    constants.HEADERS = {"Authorization": f"Bearer {constants.API_KEY}"}