from dataclasses import dataclass
from typing import Optional

from requests import Response

import kih_api.http_requests.common
from kih_api import http_requests
from kih_api.global_common import constants
from kih_api.http_requests.models import ResponseObject


@dataclass
class IPAddressInfo(ResponseObject):
    zip: Optional[str] = None
    query: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    region_name: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    google_maps_link: Optional[str] = None
    endpoint: str = constants.IP_ADDRESS_INFO_ENDPOINT

    @classmethod
    def get(cls, ip_address: str) -> "IPAddressInfo":
        response: Response = http_requests.get(cls.endpoint + ip_address)
        ip_address_info: IPAddressInfo = kih_api.http_requests.common.get_model_from_response(response, cls)  # type: ignore
        ip_address_info.google_maps_link = f"https://maps.google.com/?q={ip_address_info.lat},{ip_address_info.lon}"
        return ip_address_info
