import os

import kih_api.global_common.constants

DATABASE_URI: str = os.getenv("MONGO_DB_URI")
DATABASE_NAME: str = kih_api.global_common.constants.ENVIRONMENT
