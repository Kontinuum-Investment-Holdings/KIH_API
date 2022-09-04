import datetime
import enum
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Union, Optional

import ibapi.common
import ibapi.contract
import ibapi.order
import ibapi.order_state

import kih_api
from kih_api import global_common, communication
from kih_api.communication import telegram
from kih_api.ibkr import constants, IBKR_API
from kih_api.ibkr.exceptions import MarketDataNotAvailableException
from kih_api.ibkr.helper import IBKR_Helper


class OrderType(enum.Enum):
    MARKET: str = "MKT"
    LIMIT: str = "LMT"


class OrderAction(enum.Enum):
    BUY: str = "BUY"
    SELL: str = "SELL"


class HistoricalDataType(enum.Enum):
    TRADES: str = "TRADES"
    MIDPOINT: str = "MIDPOINT"
    BID: str = "BID"
    ASK: str = "ASK"
    BID_ASK: str = "BID_ASK"
    ADJUSTED_LAST: str = "ADJUSTED_LAST"
    HISTORICAL_VOLATILITY: str = "HISTORICAL_VOLATILITY"
    OPTION_IMPLIED_VOLATILITY: str = "OPTION_IMPLIED_VOLATILITY"
    REBATE_RATE: str = "REBATE_RATE"
    FEE_RATE: str = "FEE_RATE"
    YIELD_BID: str = "YIELD_BID"
    YIELD_ASK: str = "YIELD_ASK"
    YIELD_BID_ASK: str = "YIELD_BID_ASK"
    YIELD_LAST: str = "YIELD_LAST"


class Exchange(enum.Enum):
    SMART: str = "SMART"
    NASDAQ: str = "NASDAQ"
    AMEX: str = "AMEX"
    NYSE: str = "NYSE"
    CBOE: str = "CBOE"
    NO_EXCHANGE: str = ""


class OrderStatus(enum.Enum):
    PENDING_SUBMIT: str = "PendingSubmit"
    PENDING_CANCEL: str = "PendingCancel"
    PRE_SUBMITTED: str = "PreSubmitted"
    SUBMITTED: str = "Submitted"
    API_CANCELLED: str = "ApiCancelled"
    CANCELLED: str = "Cancelled"
    FILLED: str = "Filled"
    INACTIVE: str = "Inactive"


class SecurityType(enum.Enum):
    STOCK: str = "STK"
    CFD: str = "CFD"
    INDEX: str = "IND"
    FUTURE: str = "FUT"
    OPTION: str = "OPT"
    FUTURES_OPTION: str = "FOP"
    BONDS: str = "BOND"
    MUTUAL_FUND: str = "FUND"
    COMMODITY: str = "CMDTY"
    STANDARD_WARRANT: str = "WAR"
    STRUCTURED_PRODUCT_AND_DUTCH_WARRANT: str = "IOPT"


class HistoricalDataBarSize(enum.Enum):
    SECOND_1: str = "1 secs"
    SECOND_5: str = "5 secs"
    SECOND_10: str = "10 secs"
    SECOND_15: str = "15 secs"
    SECOND_30: str = "30 secs"
    MINUTE_1: str = "1 min"
    MINUTE_2: str = "2 min"
    MINUTE_3: str = "3 min"
    MINUTE_5: str = "5 min"
    MINUTE_10: str = "10 min"
    MINUTE_15: str = "15 min"
    MINUTE_20: str = "20 min"
    MINUTE_30: str = "30 min"
    HOUR_1: str = "1 hour"
    HOUR_2: str = "2 hours"
    HOUR_3: str = "3 hours"
    HOUR_4: str = "4 hours"
    HOUR_8: str = "8 hours"
    DAY_1: str = "1 day"
    WEEK_1: str = "1 week"
    MONTH_1: str = "1 month"


class IBKR:
    @staticmethod
    def write_historical_data(symbol: str, location: str, bar_size: HistoricalDataBarSize = HistoricalDataBarSize.DAY_1, historical_data_type: HistoricalDataType = HistoricalDataType.TRADES) -> None:
        historical_data: List["HistoricalData"] = IBKR.get_historical_data(symbol, bar_size, historical_data_type)
        global_common.create_csv(historical_data, location)

    @staticmethod
    def get_historical_data(symbol: str, bar_size: HistoricalDataBarSize = HistoricalDataBarSize.DAY_1, historical_data_type: HistoricalDataType = HistoricalDataType.TRADES) -> List["HistoricalData"]:
        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.reqHistoricalData(ibkr_api.next_order_id, IBKR_Helper.get_contract_object(symbol, SecurityType.STOCK), (datetime.datetime.today()).strftime("%Y%m%d %H:%M:%S"), "30 Y", bar_size.value, historical_data_type.value, 1, 1, False, [])
        raw_historical_data_list: List[Dict[str, Any]] = IBKR_Helper.get_data_from_ibkr(ibkr_api, "historical_data_end", "historical_data")

        historical_data: List[HistoricalData] = []
        for raw_historical_data in raw_historical_data_list:
            historical_data.append(HistoricalData(raw_historical_data.get("bar")))
        return historical_data

    @staticmethod
    def is_market_open(symbol: str) -> bool:
        # try:
        #     IBKR.get_current_ask_price(symbol)
        #     return True
        # except MarketNotOpenException:
        #     return False
        return True

    @staticmethod
    def get_current_ask_price(symbol: str, number_of_tries: int = 0) -> Union[Decimal, None]:
        contract = IBKR_Helper.get_contract_object(symbol, SecurityType.STOCK)

        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.reqMktData(ibkr_api.next_order_id, contract, '', False, False, [])
        data_list: List[Dict[str, Any]] = IBKR_Helper.get_data_from_ibkr(ibkr_api, "ask_price")
        for data in data_list:
            if data.get("price") != -1:
                return Decimal(str(data.get("price")))

        if number_of_tries < 3:
            return IBKR.get_current_ask_price(symbol, number_of_tries + 1)
        else:
            raise MarketDataNotAvailableException()

    @staticmethod
    def place_order(symbol: str, quantity: Decimal, limit_price: Decimal, order_action: OrderAction, order_type: OrderType, security_type: SecurityType) -> "Order":
        telegram.send_message(telegram.constants.telegram_channel_username,
                                            f"<u><b>Placing a new order</b></u>\n\nSymbol: <i>{symbol}</i>"
                                            f"\nOrder Type: <i>{order_type.value}</i>"
                                            f"\nOrder Action: <i>{order_action.value}</i>"
                                            f"\nQuantity: <i>{str(quantity)}</i>"
                                            f"\nPrice: <i>{str(limit_price)}</i>", True)

        order: ibapi.order.Order = IBKR_Helper.get_order_object(quantity, limit_price, order_action, order_type)
        contract: ibapi.contract.Contract = IBKR_Helper.get_contract_object(symbol, security_type)

        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.placeOrder(ibkr_api.next_order_id, contract, order)

        data_list: List[Dict[str, Any]] = IBKR_Helper.get_data_from_ibkr(ibkr_api, "order_status")

        return Order(data_list[0]["orderId"], data_list[1]["status"], data_list[1]["filled"], data_list[1]["remaining"], data_list[1]["avgFillPrice"], data_list[0]["contract"], data_list[0]["order"], data_list[0]["orderState"])

    @staticmethod
    def close_all_positions() -> List["Order"]:
        IBKR.cancel_all_orders()

        positions_list: List[Position] = IBKR.get_positions()
        orders_list: List["Order"] = []
        for position in positions_list:
            if position.quantity > 0:
                telegram.send_message(telegram.constants.telegram_channel_username,
                                                    f"<u><b>Closing all positions</b></u>"
                                                    f"\n\nSymbol: <i>{position.symbol}</i>"
                                                    f"\nQuantity: <i>{str(position.quantity)}</i>", True)

                orders_list.append(IBKR.place_order(position.symbol, position.quantity, None, OrderAction.SELL, OrderType.MARKET, position.security_type))
        return orders_list

    @staticmethod
    def request_account_summary(currency: global_common.Currency = None) -> "Account":
        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()

        if currency is None:
            ibkr_api.reqAccountSummary(2, "All", "$LEDGER")
        else:
            ibkr_api.reqAccountSummary(2, "All", f"$LEDGER:{currency.value}")

        return Account(IBKR_Helper.get_data_from_ibkr(ibkr_api, "account_summary_end", "account_summary"))

    @staticmethod
    def get_positions() -> List["Position"]:
        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.reqPositions()

        data_list: List[Dict[str, Any]] = IBKR_Helper.get_data_from_ibkr(ibkr_api, "positions_end", "positions")
        position_list: List["Position"] = []

        if data_list is not None:
            for data in data_list:
                position_list.append(Position(data.get("account"), data.get("contract"), data.get("position"), data.get("avgCost")))

        return position_list

    @staticmethod
    def get_all_order_status() -> List[Any]:
        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.reqAllOpenOrders()

        return IBKR_Helper.get_data_from_ibkr(ibkr_api, "order_status_end", "order_status")

    @staticmethod
    def cancel_all_orders() -> None:
        telegram.send_message(telegram.constants.telegram_channel_username, "<u><b>Cancelling all orders</b></u>", True)

        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.reqGlobalCancel()
        time.sleep(constants.WAIT_TIME_IN_SECONDS)
        ibkr_api.disconnect()

    @staticmethod
    def get_all_managed_accounts() -> List[str]:
        ibkr_api: IBKR_API = IBKR_Helper.get_IBKR_connection()
        ibkr_api.reqManagedAccts()

        data_list: List[Any] = IBKR_Helper.get_data_from_ibkr(ibkr_api, "managed_accounts")
        return_data: List[str] = []
        for data in data_list:
            return_data.append(data.get("accountsList"))
        return return_data

    @staticmethod
    def is_connection_successful() -> bool:
        try:
            IBKR.get_current_ask_price("QQQ")
            return True
        except:
            return False


@dataclass
class HistoricalData:
    timestamp: datetime.datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    average: Decimal
    volume: Decimal

    def __init__(self, bar_data: ibapi.common.BarData):
        self.average = Decimal(str(bar_data.average))
        self.close = Decimal(str(bar_data.close))
        self.high = Decimal(str(bar_data.high))
        self.low = Decimal(str(bar_data.low))
        self.open = Decimal(str(bar_data.open))
        self.volume = Decimal(str(bar_data.volume))

        format_str: str = "%Y%m%d" if len(bar_data.date) == 8 else "%Y%m%d %H:%M:%S"
        self.timestamp = datetime.datetime.strptime(bar_data.date, format_str)

    @staticmethod
    def get_from_date(historical_data_list: List[HistoricalData], date: datetime.datetime, is_get_next_date_if_unavailable: bool = True) -> Optional[HistoricalData]:
        end_date_filter: datetime.datetime = date + datetime.timedelta(days=5 if is_get_next_date_if_unavailable else 0)
        filtered_historical_data_list: List[HistoricalData] = list(filter(lambda data: date <= data.timestamp <= end_date_filter, historical_data_list))
        sorted_historical_data_list: List[HistoricalData] = sorted(filtered_historical_data_list, key=lambda data: data.timestamp)

        if len(sorted_historical_data_list) != 0:
            return sorted_historical_data_list[0]
        else:
            return None


@dataclass
class Position:
    account: str
    symbol: str
    contract: "Contract"
    quantity: Decimal
    average_cost: Decimal
    security_type: SecurityType

    def __init__(self, account: str, contract: ibapi.contract.Contract, quantity: float, average_cost: float):
        self.account = account
        self.contract = Contract(contract.conId, contract.currency, contract.symbol, contract.exchange)
        self.symbol = self.contract.symbol
        self.quantity = Decimal(str(quantity))
        self.average_cost = Decimal(str(average_cost))
        self.security_type = global_common.get_enum_from_value(contract.secType, SecurityType)


@dataclass
class Contract:
    contract_id: int
    currency: global_common.Currency
    symbol: str
    exchange: Exchange

    def __init__(self, contract_id: int, currency: str, symbol: str, exchange: str):
        self.contract_id = contract_id
        self.currency = global_common.get_enum_from_value(currency, global_common.Currency)
        self.symbol = symbol
        self.exchange = global_common.get_enum_from_value(exchange, Exchange)


@dataclass
class Order:
    order_id: int
    status: OrderStatus
    quantity_filled: Decimal
    remaining_to_fill: Decimal
    average_fill_price: Decimal
    contract: Contract
    order: ibapi.order.Order
    order_state: ibapi.order_state.OrderState

    def __init__(self, order_id: int, status: str, quantity_filled: float, remaining_to_fill: float, average_fill_price: float, contract: ibapi.contract.Contract, order: ibapi.order.Order, order_state: ibapi.order_state.OrderState):
        self.order_id = order_id
        self.status = global_common.get_enum_from_value(status, OrderStatus)
        self.quantity_filled = Decimal(str(quantity_filled))
        self.remaining_to_fill = Decimal(str(remaining_to_fill))
        self.average_fill_price = Decimal(str(average_fill_price))
        self.contract = Contract(contract.conId, contract.currency, contract.symbol, contract.exchange)
        self.order = order
        self.order_state = order_state


@dataclass
class Account:
    cash_balance: Decimal
    stock_market_value: Decimal
    unrealized_pnl: Decimal
    net_liquidity: Decimal

    def __init__(self, data_list: List[Dict[str, Any]]):
        for data in data_list:
            if data.get("tag") == "TotalCashBalance":
                self.cash_balance = Decimal(str(data.get("value")))
            elif data.get("tag") == "StockMarketValue":
                self.stock_market_value = Decimal(str(data.get("value")))
            elif data.get("tag") == "UnrealizedPnL":
                self.unrealized_pnl = Decimal(str(data.get("value")))
            elif data.get("tag") == "NetLiquidationByCurrency":
                self.net_liquidity = Decimal(str(data.get("value")))
