import time
from typing import Dict, Optional, Any

import requests
import urllib3
from requests import Response

from kih_api.global_common import CustomException
from kih_api.http_requests import constants
from kih_api.http_requests.models import MethodType
from kih_api.logger import logger

is_ssl_certificate_verification_used: bool = True
urllib3.disable_warnings()


class ServerErrorException(CustomException):
    pass


class ClientErrorException(CustomException):
    pass


def get(url: str, parameters: Optional[Dict[str, Any]] = None, headers: Dict[str, str] = None) -> Response:
    return request(url, parameters, MethodType.GET, headers=headers)


def post(url: str, parameters: Optional[Dict[str, Any]] = None, headers: Dict[str, str] = None) -> Response:
    return request(url, parameters, MethodType.POST, headers=headers)


def put(url: str, parameters: Optional[Dict[str, Any]] = None, headers: Dict[str, str] = None) -> Response:
    return request(url, parameters, MethodType.PUT, headers=headers)


def delete(url: str, parameters: Optional[Dict[str, Any]] = None, headers: Dict[str, str] = None) -> Response:
    return request(url, parameters, MethodType.DELETE, headers=headers)


def request(url: str, parameters: Optional[Dict[str, Any]], method_type: MethodType, server_error_retry_times: int = 0, headers: Dict[str, str] = None) -> Response:
    global is_ssl_certificate_verification_used
    start_time: float = time.time()

    response: Response = None
    if method_type == MethodType.GET:
        response = requests.get(url=url, params=parameters, verify=is_ssl_certificate_verification_used, headers=headers)
    elif method_type == MethodType.POST:
        response = requests.post(url=url, json=parameters, verify=is_ssl_certificate_verification_used, headers=headers)
    elif method_type == MethodType.PUT:
        response = requests.put(url=url, params=parameters, verify=is_ssl_certificate_verification_used, headers=headers)
    elif method_type == MethodType.DELETE:
        response = requests.delete(url=url, params=parameters, verify=is_ssl_certificate_verification_used, headers=headers)

    if 400 <= response.status_code <= 499:
        logger.error("Response code: " + str(response.status_code))
        raise ClientErrorException(response.text)
    elif 500 <= response.status_code <= 599:
        logger.error("Response code: " + str(response.status_code))
        if server_error_retry_times < constants.SERVER_ERROR_RETRY_TIMES:
            logger.info("Retrying")
            response = request(url, parameters, method_type, server_error_retry_times + 1)
        else:
            raise ServerErrorException(response.text)

    logger.debug(
        constants.EXECUTION_TYPE_API_Call + " | " + method_type.value + " | " + response.url + " | " + str(time.time() - start_time) + " | " + url + " | " + str(response.status_code))
    logger.debug(response.text)

    return response
