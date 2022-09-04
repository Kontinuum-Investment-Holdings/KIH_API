import datetime
import os
import shutil
import tempfile

import requests
import validators
from dateutil.relativedelta import relativedelta

from kih_api.finance_database.exceptions import ExcelFileOpenedByAnotherApplication


def get_temp_file_path(file_path: str) -> str:
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, 'temp_file_name')
    try:
        if validators.url(file_path):
            open(temp_file_path, 'wb').write(requests.get(file_path).content)
        else:
            shutil.copy(file_path, temp_file_path)
    except PermissionError:
        raise ExcelFileOpenedByAnotherApplication()
    return temp_file_path


def get_next_month_text() -> str:
    today: datetime.date = datetime.date.today()
    start_of_this_month: datetime.date = datetime.date(today.year, today.month, 1)
    start_of_next_month: datetime.date = start_of_this_month + relativedelta(months=1)
    return start_of_next_month.strftime("%B, %Y")
