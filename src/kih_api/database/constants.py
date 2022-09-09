import os

import kih_api.global_common.constants
from kih_api import global_common

DATABASE_URI: str = global_common.get_environment_variable("MONGO_DB_URI")
DATABASE_NAME: str = kih_api.global_common.constants.ENVIRONMENT
