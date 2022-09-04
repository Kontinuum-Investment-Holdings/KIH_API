from kih_api.global_common import CustomException


class DataNotFoundException(CustomException):
    pass


class ExcelFileOpenedByAnotherApplication(CustomException):
    pass


class AccountForCurrencyNotFoundException(CustomException):
    pass


class InsufficientFundsException(CustomException):
    pass
