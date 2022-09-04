import datetime
from decimal import Decimal
from typing import Dict, Tuple, Any, Union, List, Optional

from bson import SON
from mongoengine import Document, DateTimeField, EmbeddedDocument

from kih_api import database
from kih_api.global_common import timed

database.connect_to_database()


class DatabaseDocument(Document):
    modified_time: datetime.datetime = DateTimeField(default=datetime.datetime.utcnow)

    meta: Dict[str, Any] = {"abstract": True}

    @timed
    def save(self, *args: Tuple, **kwargs: Dict) -> None:
        self.modified_time = datetime.datetime.utcnow()
        self.__class__._get_collection().update_one({"_id": self.pk}, {"$set": self.__class__.get_raw_son(self)}, upsert=True)

    @staticmethod
    def get_raw_son(data: Union["DatabaseDocument", EmbeddedDocument, SON]) -> SON:
        all_data: SON = data.to_mongo() if isinstance(data, (DatabaseDocument, EmbeddedDocument)) else data

        for key, value in all_data.copy().items():
            if isinstance(value, (DatabaseDocument, EmbeddedDocument, SON)):
                all_data[key] = DatabaseDocument.get_raw_son(value)
            elif isinstance(value, List):
                new_list: List[Any] = []
                for item in value:
                    if isinstance(item, Decimal):
                        new_list.append(float(item))
                    else:
                        new_list.append(item)
                all_data[key] = new_list

        return all_data

    def get_primary_key_field_name(self) -> Optional[str]:
        for field in self._fields_ordered:
            if id(getattr(self, field)) == id(self.pk):
                return field
        return None
