import enum
import inspect
import os
import subprocess
import threading
import time
from decimal import Decimal
from typing import Any, Dict, Type, Optional, List, Union, Callable

from dataclass_csv import DataclassWriter

from kih_api.logger import logger


class Currency(enum.Enum):
    USD: str = "USD"
    EUR: str = "EUR"
    GBP: str = "GBP"
    AUD: str = "AUD"
    NZD: str = "NZD"
    SGD: str = "SGD"
    LKR: str = "LKR"
    IDR: str = "IDR"

class Environment(enum.Enum):
    PROD: str = "Production"
    DEV: str = "Development"


class CustomException(Exception):
    pass


class EnumNotFoundException(CustomException):
    pass


def get_environment() -> Environment:
    try:
        if get_environment_variable("ENVIRONMENT") == Environment.PROD.value:
            return Environment.PROD
        else:
            return Environment.DEV
    except CustomException:
        return Environment.DEV

def get_environment_variable(key: str) -> str:
    value: str = os.getenv(key)
    if value is not None:
        return value
    else:
        raise CustomException(f"Environment variable not setup: {key}")

def convert_string_to_dict(string: str) -> Dict[Any, Any]:
    parameters_list = string.split(",")

    return_dict = {}
    for parameter in parameters_list:
        key_value_pair = parameter.split("=")
        key = key_value_pair[0]
        value = key_value_pair[1]

        return_dict[key] = value

    return return_dict


def get_enum_from_value(value: Any, enum: Type[enum.Enum]) -> Optional[Any]:
    for enum_value in enum:
        if enum_value.value == value:
            return enum_value

    raise EnumNotFoundException()


def get_formatted_string_from_decimal(number: Decimal, decimal_places: int = 2) -> str:
    return f'{number.quantize(Decimal(10) ** -decimal_places):,}'


def threaded(func: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> threading.Thread:
        thread: threading.Thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        logger.debug(f"Thread started for function: {os.path.abspath(inspect.getfile(func))} | {func.__name__}")
        return thread

    return wrapper


def run_command(command_list: List[str]) -> Union[List[str], None]:
    output_list: List[str] = []

    for command in command_list:
        logger.info("Running command: " + command)
        output_list.extend(
            subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n"))

    for output in output_list:
        logger.info(output)

    return output_list


def get_running_processes(command: str) -> List[Dict[str, str]]:
    results_list: List[str] = run_command([f"sudo pgrep -a {command}"])

    processes_list: List[Dict[str, str]] = []
    for result in results_list:
        if command in result:
            processes_list.append({"PID": result.split(" ")[0], "Command": result.replace(result.split(" ")[0], "")})

    return processes_list


def kill_process(keyword: str, command: str) -> bool:
    processes_list: List[Dict[str, str]] = get_running_processes(command)
    is_process_found_and_killed = False

    for process in processes_list:
        if keyword in process["Command"]:
            run_command([f"kill -9 {process['PID']}"])
            is_process_found_and_killed = True

    return is_process_found_and_killed


def update_code_base(project_directory: str, main_branch_name: str = "main") -> None:
    os.chdir(project_directory)

    run_command([f"git reset --hard origin/{main_branch_name}"])
    run_command([f"git pull origin {main_branch_name}"])

    if "requirements.txt" in os.listdir(project_directory):
        run_command([f"pip install -r requirements.txt"])


def job(job_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> None:
            from kih_api.communication import telegram
            try:
                telegram.send_message(
                    telegram.constants.telegram_debug_channel_username,
                    f"Running job: <i>{job_name}</i>", True)
                logger.debug(f"Running job: {job_name}")
                func(*args, **kwargs)
            except Exception as e:
                message = f"<b><u>ERROR</u></b>\n\nJob Name: <i>{job_name}</i>\nError Type: <i>{type(e).__name__}</i>"
                if str(e) != "":
                    message = message + f"\nError Message: <i>{str(e).replace('<', '').replace('>', '')}</i>"
                telegram.send_message(telegram.constants.telegram_channel_username, message,
                                                    True)
                raise Exception(e)
            finally:
                logger.debug(f"Job ended: {job_name}")
                telegram.send_message(
                    telegram.constants.telegram_debug_channel_username,
                    f"Job ended: <i>{job_name}</i>", True)

        return wrapper

    return decorator


def create_csv(data_class_list: List[Any], location: str) -> None:
    for data in data_class_list:
        if not isinstance(data, type(data_class_list[0])):
            raise Exception("Different objects types in data class list")

    with open(location, "w", newline="\n") as f:
        w = DataclassWriter(f, data_class_list, type(data_class_list[0]))
        w.write()


def timed(func: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time: Decimal = Decimal(time.time_ns())
        return_data: Any = func(*args, **kwargs)
        end_time: Decimal = Decimal(time.time_ns())
        logger.debug(
            f"\n---------------------------------------------------------------------------------------------------"
            f"\nFunction: {func.__name__}"
            f"\nArguments: {args}"
            f"\nKey word arguments: {kwargs}"
            f"\nTime taken: {get_formatted_string_from_decimal(Decimal(end_time - start_time) / Decimal('1000_0000'))}ms"
            f"\n\t\t\t{get_formatted_string_from_decimal(Decimal(end_time - start_time) / Decimal('1000'))}ns"
            f"\n---------------------------------------------------------------------------------------------------")
        return return_data

    return wrapper
