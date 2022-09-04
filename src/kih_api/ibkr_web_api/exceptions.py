from kih_api.global_common import CustomException


class KeepAliveFailedException(CustomException):
    pass


class AuthenticationFailedException(CustomException):
    pass


class StockNotFoundException(CustomException):
    pass


class MarketDataSnapshotNotAvailableException(CustomException):
    pass


class MarketOrderOutsideRTHException(CustomException):
    pass


class StockDataNotAvailableException(CustomException):
    pass
