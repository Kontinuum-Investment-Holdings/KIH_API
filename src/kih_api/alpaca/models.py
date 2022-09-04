import enum
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Union

import alpaca_trade_api.entity
import dateutil.parser
from alpaca_trade_api.rest import APIError

import kih_api
from kih_api import global_common, communication
from kih_api.alpaca import alpaca_api
from kih_api.communication import telegram


class AccountStatus(enum.Enum):
    ON_BOARDING: str = "ONBOARDING"
    SUBMISSION_FAILED: str = "SUBMISSION_FAILED"
    SUBMITTED: str = "SUBMITTED"
    ACCOUNT_UPDATED: str = "ACCOUNT_UPDATED"
    APPROVAL_PENDING: str = "APPROVAL_PENDING"
    ACTIVE: str = "ACTIVE"
    REJECTED: str = "REJECTED"
    DISABLE_PENDING: str = "DISABLE_PENDING"


class OrderSide(enum.Enum):
    BUY: str = "buy"
    SELL: str = "sell"


class OrderType(enum.Enum):
    LIMIT: str = "limit"
    MARKET: str = "market"
    STOP: str = "stop"
    STOP_LIMIT: str = "stop_limit"
    TRAILING_STOP: str = "trailing_stop"


class OrderTimeInForce(enum.Enum):
    DAY: str = "day"
    GTC: str = "gtc"
    OPG: str = "opg"
    CLS: str = "cls"
    IOC: str = "ioc"
    FOK: str = "fok"


class OrderStatus(enum.Enum):
    NEW: str = "new"
    PARTIALLY_FILLED: str = "partially_filled"
    FILLED: str = "filled"
    DONE_FOR_DAY: str = "done_for_day"
    CANCELED: str = "canceled"
    EXPIRED: str = "expired"
    REPLACED: str = "replaced"
    PENDING_CANCEL: str = "pending_cancel"
    ACCEPTED: str = "accepted"
    PENDING_NEW: str = "pending_new"
    ACCEPTED_FOR_BIDDING: str = "accepted_for_bidding"
    STOPPED: str = "stopped"
    REJECTED: str = "rejected"
    SUSPENDED: str = "suspended"
    CALCULATED: str = "calculated"


@dataclass
class Account:
    account_blocked: bool
    account_number: str
    buying_power: Decimal
    cash: Decimal
    currency: global_common.Currency
    daytrading_buying_power: Decimal
    equity: Decimal
    portfolio_value: Decimal
    status: AccountStatus

    def __init__(self, alpaca_account: alpaca_trade_api.entity.Account):
        self.account_blocked = alpaca_account._raw["account_blocked"]
        self.account_number = alpaca_account._raw["account_number"]
        self.buying_power = Decimal(str(alpaca_account._raw["buying_power"]))
        self.cash = Decimal(str(alpaca_account._raw["cash"]))
        self.currency = global_common.get_enum_from_value(alpaca_account._raw["currency"], global_common.Currency)
        self.daytrading_buying_power = Decimal(str(alpaca_account._raw["daytrading_buying_power"]))
        self.equity = Decimal(str(alpaca_account._raw["equity"]))
        self.portfolio_value = Decimal(str(alpaca_account._raw["portfolio_value"]))
        self.status = global_common.get_enum_from_value(alpaca_account._raw["status"], AccountStatus)

    @staticmethod
    def call() -> "Account":
        alpaca_account: alpaca_trade_api.entity.Account = alpaca_api.get_account()
        return Account(alpaca_account)


@dataclass
class Position:
    asset_id: str
    symbol: str
    exchange: str
    average_entry_price: Decimal
    quantity: Decimal
    market_value: Decimal
    cost_basis: Decimal
    current_price: Decimal
    change_in_percentage: Decimal
    unrealized_profit_loss: Decimal
    unrealized_profit_loss_in_percentage: Decimal

    def __init__(self, alpaca_position: alpaca_trade_api.entity.Position):
        self.asset_id = alpaca_position._raw["asset_id"]
        self.symbol = alpaca_position._raw["symbol"]
        self.exchange = alpaca_position._raw["exchange"]
        self.average_entry_price = Decimal(str(alpaca_position._raw["avg_entry_price"]))
        self.quantity = Decimal(str(alpaca_position._raw["qty"]))
        self.market_value = Decimal(str(alpaca_position._raw["market_value"]))
        self.cost_basis = Decimal(str(alpaca_position._raw["cost_basis"]))
        self.current_price = Decimal(str(alpaca_position._raw["current_price"]))
        self.change_in_percentage = Decimal(str(alpaca_position._raw["change_today"]))
        self.unrealized_profit_loss = Decimal(str(alpaca_position._raw["unrealized_pl"]))
        self.unrealized_profit_loss_in_percentage = Decimal(str(alpaca_position._raw["unrealized_plpc"]))

    @staticmethod
    def call() -> List["Position"]:
        alpaca_positions: List[alpaca_trade_api.entity.Position] = alpaca_api.list_positions()
        positions_list: List[Position] = []
        for alpaca_position in alpaca_positions:
            positions_list.append(Position(alpaca_position))
        return positions_list

    @staticmethod
    def get_by_symbol(symbol: str) -> "Position":
        try:
            alpaca_position: alpaca_trade_api.entity.Position = alpaca_api.get_position(symbol)
        except APIError as e:
            if str(e) == "position does not exist":
                return None
            else:
                raise APIError(e)

        return Position(alpaca_position)

    @staticmethod
    def close_all_by_symbol(symbol: str) -> Union["Order", None]:
        position: Position = Position.get_by_symbol(symbol)

        if position is not None:
            quantity: Decimal = position.quantity
        else:
            quantity = Decimal("0")

        telegram.send_message(telegram.constants.telegram_channel_username,
                                            f"<u><b>Closing whole position</b></u>"
                                            f"\n\nSymbol: <i>{symbol}</i>"
                                            f"\nQuantity: <i>{str(quantity)}</i>", True)

        try:
            alpaca_order: List[alpaca_trade_api.entity.Position] = alpaca_api.close_position(symbol)
        except APIError as e:
            if str(e) == "position does not exist":
                return None
            else:
                raise APIError(e)

        return Order(alpaca_order)

    @staticmethod
    def close_by_symbol(symbol: str, quantity: Decimal) -> List["Position"]:
        alpaca_positions: List[alpaca_trade_api.entity.Position] = alpaca_api.close_position(symbol, quantity)
        positions_list: List[Position] = []
        for alpaca_position in alpaca_positions:
            positions_list.append(Position(alpaca_position))
        return positions_list

    @staticmethod
    def close_all() -> List["Position"]:
        telegram.send_message(telegram.constants.telegram_channel_username,
                                            f"<u><b>Closing every single position</b></u>", True)

        alpaca_positions: List[alpaca_trade_api.entity.Position] = alpaca_api.close_all_positions()
        positions_list: List[Position] = []
        for alpaca_position in alpaca_positions:
            positions_list.append(Position(alpaca_position))
        return positions_list


@dataclass
class Order:
    id: str
    client_order_id: str
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime
    filled_at: datetime
    expired_at: datetime
    canceled_at: datetime
    failed_at: datetime
    asset_id: str
    symbol: str
    quantity: Decimal
    filled_qty: Decimal
    filled_avg_price: Decimal
    order_type: OrderType
    side: OrderSide
    time_in_force: OrderTimeInForce
    limit_price: Decimal
    status: OrderStatus
    is_extended_hours: bool

    def __init__(self, alpaca_order: alpaca_trade_api.entity.Order):
        self.id = alpaca_order._raw["id"]
        self.created_at = dateutil.parser.isoparse(alpaca_order._raw["created_at"])
        self.updated_at = dateutil.parser.isoparse(alpaca_order._raw["updated_at"])
        self.submitted_at = dateutil.parser.isoparse(alpaca_order._raw["submitted_at"])
        self.asset_id = alpaca_order._raw["asset_id"]
        self.symbol = alpaca_order._raw["symbol"]
        self.quantity = Decimal(alpaca_order._raw["qty"])
        self.filled_qty = Decimal(alpaca_order._raw["filled_qty"])
        self.order_type = global_common.get_enum_from_value(alpaca_order._raw["order_type"], OrderType)
        self.side = global_common.get_enum_from_value(alpaca_order._raw["side"], OrderSide)
        self.time_in_force = global_common.get_enum_from_value(alpaca_order._raw["time_in_force"], OrderTimeInForce)
        self.status = global_common.get_enum_from_value(alpaca_order._raw["status"], OrderStatus)
        self.is_extended_hours = alpaca_order._raw["extended_hours"]

        if alpaca_order._raw["limit_price"] is not None:
            self.limit_price = Decimal(alpaca_order._raw["limit_price"])

        if alpaca_order._raw["filled_at"] is not None:
            self.filled_at = dateutil.parser.isoparse(alpaca_order._raw["filled_at"])

        if alpaca_order._raw["expired_at"] is not None:
            self.expired_at = dateutil.parser.isoparse(alpaca_order._raw["expired_at"])

        if alpaca_order._raw["canceled_at"] is not None:
            self.canceled_at = dateutil.parser.isoparse(alpaca_order._raw["canceled_at"])

        if alpaca_order._raw["failed_at"] is not None:
            self.failed_at = dateutil.parser.isoparse(alpaca_order._raw["failed_at"])

        if alpaca_order._raw["filled_avg_price"] is not None:
            self.filled_avg_price = Decimal(alpaca_order._raw["filled_avg_price"])

    @staticmethod
    def place(symbol: str, quantity: int, order_side: OrderSide, order_type: OrderType, limit_price: Decimal, time_in_force: OrderTimeInForce, custom_order_id: str = None) -> "Order":
        if custom_order_id is None:
            custom_order_id = str(uuid.uuid4())

        if order_type == OrderType.MARKET:
            float_limit_price: float = None
        else:
            float_limit_price = float(limit_price)

        telegram.send_message(telegram.constants.telegram_channel_username,
                                            f"<u><b>Placing a new order</b></u>"
                                            f"\n\nSymbol: <i>{symbol}</i>"
                                            f"\nOrder Type: <i>{order_type.value}</i>"
                                            f"\nOrder Side: <i>{order_side.value}</i>"
                                            f"\nQuantity: <i>{str(quantity)}</i>\nPrice: "
                                            f"<i>{str(float_limit_price)}</i>", True)

        alpaca_order: alpaca_trade_api.entity.Order = alpaca_api.submit_order(
            symbol=symbol,
            qty=int(quantity),
            side=order_side.value,
            type=order_type.value,
            time_in_force=time_in_force.value,
            limit_price=float_limit_price,
            client_order_id=custom_order_id
        )
        order: Order = Order(alpaca_order)

        if order.order_type == OrderType.MARKET:
            message: str = f"<u><b>Order status</b></u>" \
                           f"\n\nSymbol: <i>{symbol}</i>" \
                           f"\nOrder Type: <i>{order_type.value}</i>" \
                           f"\nOrder Side: <i>{order_side.value}</i>" \
                           f"\nQuantity: <i>{str(quantity)}</i>" \
                           f"\nFilled Quantity: <i>{str(order.filled_qty)}</i>"

            if order.filled_qty > 0:
                message = message + f"\nFilled Average Price: <i>${global_common.get_formatted_string_from_decimal(order.filled_avg_price)}</i>"

            telegram.send_message(telegram.constants.telegram_channel_username, message, True)

        return order

    @staticmethod
    def get_by_custom_order_id(custom_order_id: str) -> "Order":
        alpaca_order = alpaca_api.get_order_by_client_order_id(custom_order_id)
        return Order(alpaca_order)

    @staticmethod
    def get_all() -> List["Order"]:
        alpaca_order_list: List[alpaca_trade_api.entity.Order] = alpaca_api.list_orders()
        order_list: List["Order"] = []
        for alpaca_order in alpaca_order_list:
            order_list.append(Order(alpaca_order))
        return order_list

    @staticmethod
    def cancel_by_custom_order_id(custom_order_id: str) -> None:
        telegram.send_message(telegram.constants.telegram_channel_username,
                                            f"<u><b>Cancelling Order</b></u>"
                                            f"\n\nCustom Order ID: <i>{custom_order_id}</i>", True)

        alpaca_api.cancel_order(custom_order_id)

    @staticmethod
    def cancel_all() -> None:
        telegram.send_message(telegram.constants.telegram_channel_username,
                                            f"<u><b>Cancelling all orders</b></u>", True)

        alpaca_api.cancel_all_orders()


@dataclass
class MarketDataHistory:
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __init__(self, alpaca_market_data: alpaca_trade_api.entity.Bar):
        self.timestamp = datetime.utcfromtimestamp(alpaca_market_data._raw["t"])
        self.open = Decimal(str(alpaca_market_data._raw["o"]))
        self.high = Decimal(str(alpaca_market_data._raw["h"]))
        self.low = Decimal(str(alpaca_market_data._raw["l"]))
        self.close = Decimal(str(alpaca_market_data._raw["c"]))
        self.volume = Decimal(str(alpaca_market_data._raw["v"]))

    @staticmethod
    def get_history(symbol: str, number_of_days: int = None) -> List["MarketDataHistory"]:
        alpaca_market_data_history_list: alpaca_trade_api.entity.Bars = alpaca_api.get_barset(symbol, "day", limit=number_of_days)[symbol]
        market_data_history_list: List[MarketDataHistory] = []
        for alpaca_market_data in alpaca_market_data_history_list:
            market_data_history_list.append(MarketDataHistory(alpaca_market_data))
        return market_data_history_list


@dataclass
class MarketData:
    symbol: str
    ask_price: Decimal
    ask_size: Decimal
    bid_price: Decimal
    bid_size: Decimal
    timestamp: datetime

    def __init__(self, symbol: str, alpaca_market_data: alpaca_trade_api.entity.Quote):
        self.symbol = symbol
        self.ask_price = Decimal(str(alpaca_market_data._raw["askprice"]))
        self.ask_size = Decimal(str(alpaca_market_data._raw["asksize"]))
        self.bid_price = Decimal(str(alpaca_market_data._raw["bidprice"]))
        self.bid_size = Decimal(str(alpaca_market_data._raw["bidsize"]))
        self.timestamp = datetime.utcfromtimestamp(int(alpaca_market_data._raw["timestamp"] / 1000000000))

    @staticmethod
    def get(symbol: str) -> "MarketData":
        alpaca_market_data: alpaca_trade_api.entity.Quote = alpaca_api.get_last_quote(symbol)
        return MarketData(symbol, alpaca_market_data)


@dataclass
class MarketClock:
    timestamp: datetime
    is_open: bool
    next_open: datetime
    next_close: datetime

    def __init__(self, alpaca_clock: alpaca_trade_api.entity.Clock):
        self.timestamp = dateutil.parser.isoparse(alpaca_clock._raw["timestamp"])
        self.is_open = alpaca_clock._raw["is_open"]
        self.next_open = dateutil.parser.isoparse(alpaca_clock._raw["next_open"])
        self.next_close = dateutil.parser.isoparse(alpaca_clock._raw["next_close"])

    @staticmethod
    def get() -> "MarketClock":
        alpaca_clock: alpaca_trade_api.entity.Clock = alpaca_api.get_clock()
        return MarketClock(alpaca_clock)
