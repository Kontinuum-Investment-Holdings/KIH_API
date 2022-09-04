from typing import Dict, Any, List, Union, Type

import dacite
from requests import Response

from kih_api.http_requests.models import ResponseObject


def get_response_object_data_from_response(response: Response, data: Dict[str, Any] = None) -> Dict[str, Any]:
    if data is None:
        data = response.json()
    data.update({"response": response, "is_successful": 200 <= response.status_code <= 299, "endpoint": response.url})
    return data


def get_model_from_response(response: Response, data_class: Type[Any]) -> Union[List[ResponseObject], ResponseObject]:
    if isinstance(response.json(), Dict):
        return dacite.from_dict(data_class=data_class, data=get_response_object_data_from_response(response))
    elif isinstance(response.json(), List):
        data_list: List[ResponseObject] = []
        for data in response.json():
            data_list.append(dacite.from_dict(data_class=data_class, data=get_response_object_data_from_response(response, data)))
        return data_list
    return None
