import enum
import inspect
import os
import subprocess
import threading
from decimal import Decimal
from typing import Any, Dict, Type, Optional, List, Union, Callable

from logger import logger


class Currency(enum.Enum):
    USD: str = "USD"
    EUR: str = "EUR"
    GBP: str = "GBP"
    AUD: str = "AUD"
    NZD: str = "NZD"
    SGD: str = "SGD"
    LKR: str = "LKR"


class CustomException(Exception):
    pass


class EnumNotFoundException(CustomException):
    pass


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
        output_list.extend(subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n"))

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
            import communication.telegram
            try:
                communication.telegram.send_message(communication.telegram.constants.telegram_channel_development_username, f"Running job: <i>{job_name}</i>", True)
                logger.debug(f"Running job: {job_name}")
                func(*args, **kwargs)
                logger.debug(f"Job ended: {job_name}")
                communication.telegram.send_message(communication.telegram.constants.telegram_channel_development_username, f"Job ended: <i>{job_name}</i>", True)
            except Exception as e:
                message = f"<b><u>ERROR</u></b>\n\nJob Name: <i>{job_name}</i>\nError Type: <i>{type(e).__name__}</i>"
                if str(e) != "":
                    message = message + f"\nError Message: <i>{str(e).replace('<', '').replace('>', '')}</i>"
                communication.telegram.send_message(communication.telegram.constants.telegram_channel_username, message, True)
                raise Exception(e)

        return wrapper

    return decorator
