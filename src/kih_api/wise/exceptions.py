from kih_api.global_common import CustomException


class MultipleUserProfilesWithSameTypeException(CustomException):
    pass


class MultipleRecipientsWithSameAccountNumberException(CustomException):
    pass


class TransferringMoneyToNonSelfOwnedAccountsException(CustomException):
    pass


class ReserveAccountNotFoundException(CustomException):
    pass


class UnImplementedException(CustomException):
    pass
