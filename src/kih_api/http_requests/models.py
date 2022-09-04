import enum
from dataclasses import dataclass

from requests import Response


class MethodType(enum.Enum):
    GET: str = "GET"
    POST: str = "POST"
    PUT: str = "PUT"
    DELETE: str = "DELETE"


@dataclass
class ResponseObject:
    response: Response
    is_successful: bool
    endpoint: str
