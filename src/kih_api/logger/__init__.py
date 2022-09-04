import logging as python_logging
import time

logger = python_logging.getLogger()
python_logging.basicConfig(level=python_logging.DEBUG, format="%(asctime)s | %(levelname)s | %(message)s")


def performance(execution_type: str, execution_subtype: str, execution_command: str, start_time: float, description: str = None) -> None:
    time_taken: int = int((time.time() - start_time) * 1000)
    log_message: str = str(time_taken) + "ms || Execution Type: " + execution_type + " | Execution Subtype:  " + execution_subtype

    if description is not None:
        log_message = log_message + " | " + description

    logger.debug(log_message)
