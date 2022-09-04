import mongoengine
from pymongo import MongoClient

from kih_api.database import constants
from kih_api.global_common import timed

mongo_client: MongoClient = None


@timed
def connect_to_database() -> None:
    global mongo_client
    if mongo_client is None:
        mongo_client = mongoengine.connect(host=constants.DATABASE_URI, db=constants.DATABASE_NAME)
