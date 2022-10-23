import enum
from dataclasses import dataclass
from typing import Optional

from requests import Response


class MethodType(enum.Enum):
    GET: str = "GET"
    POST: str = "POST"
    PUT: str = "PUT"
    DELETE: str = "DELETE"


@dataclass
class ResponseObject:
    response: Optional[Response] = None
    is_successful: Optional[bool] = None
    endpoint: Optional[str] = None
