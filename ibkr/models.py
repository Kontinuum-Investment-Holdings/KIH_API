import datetime
import enum
import uuid
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import List

import pytz

import global_common
import communication.telegram
import ibkr
from ibkr import ibkr_models
from ibkr.exceptions import StockNotFoundException, StockDataNotAvailableException
from ibkr.ibkr_models import StockSearchResults, Contract, MarketDataSnapshot, PortfolioPositions, PortfolioAccounts, \
    MarketDataHistory, LiveOrders, LiveOrder, PlaceOrderReply


class InstrumentType(enum.Enum):
    STOCK: str = "STK"
    CASH: str = "CASH"
    OPTION: str = "OPT"
    INDEX: str = "IND"


class Currency(enum.Enum):
    USD: str = "USD"
    NZD: str = "NZD"
    SGD: str = "SGD"


class OrderType(enum.Enum):
    MARKET: str = "MKT"
    LIMIT: str = "LMT"
    STOP: str = "STP"
    STOP_LIMIT: str = "STOP_LIMIT"
    MIDPRICE: str = "MIDPRICE"


class OrderSide(enum.Enum):
    BUY: str = "BUY"
    SELL: str = "SELL"


class OrderTimeInForce(enum.Enum):
    GOOD_TILL_CANCEL: str = "GTC"
    DAY: str = "DAY"


class StockExchanges(enum.Enum):
    SMART: str = "SMART"
    NASDAQ: str = "NASDAQ"
    AMEX: str = "AMEX"
    NYSE: str = "NYSE"
    CBOE: str = "CBOE"

class OrderStatus(enum.Enum):
    SUBMITTED: str = "Submitted"
    INACTIVE: str = "Inactive"
    CANCELLED: str = "Cancelled"
    PENDING_SUBMIT: str = "PendingSubmit"


@dataclass
class Instrument:
    symbol: str
    contract_id: int
    instrument_type: InstrumentType
    exchanges_list: List[str]
    main_exchange: str
    name: str
    open_price: Decimal
    close_price: Decimal
    high_price: Decimal
    low_price: Decimal
    last_price: Decimal
    change_in_currency: Decimal
    change_in_percentage: Decimal
    bid_price: Decimal
    ask_price: Decimal
    ask_size: Decimal
    bid_size: Decimal
    volume: Decimal
    option_volume: Decimal
    dividend_amount: Decimal
    dividend_yield: Decimal
    market_capitalization: Decimal
    price_to_earnings_ratio: Decimal
    earnings_per_share: Decimal

    def __init__(self, symbol: str, contract_id: int, instrument_type: str, exchanges_list: List[str], main_exchange:
    str, name: str, open_price: str, close_price: str, high_price: str, low_price: str, last_price: str,
                 change_in_currency: str, change_in_percentage: str, bid_price: str, ask_price: str,
                 ask_size: str, bid_size: str,
                 volume: str, option_volume: str, dividend_amount: str, dividend_yield: str, market_capitalization:
            str, price_to_earnings_ratio: str, earnings_per_share: str):

        if contract_id is None:
            raise StockDataNotAvailableException()

        self.symbol = symbol
        self.contract_id = contract_id
        self.exchanges_list = exchanges_list
        self.main_exchange = main_exchange
        self.name = name
        self.last_price = Decimal(str(last_price.replace("C", "").replace("H", "")))
        self.change_in_currency = Decimal(str(change_in_currency))
        self.change_in_percentage = Decimal(str(change_in_percentage))
        self.instrument_type = global_common.get_enum_from_value(instrument_type, InstrumentType)

        if bid_price is not None:
            self.bid_price = Decimal(str(bid_price))

        if bid_size is not None:
            self.bid_size = Decimal(str(bid_size))

        if ask_price is not None:
            self.ask_price = Decimal(str(ask_price))

        if ask_size is not None:
            self.ask_size = Decimal(str(ask_size))

        if volume is not None:
            self.volume = Decimal(str(volume))

        if dividend_amount is not None:
            self.dividend_amount = Decimal(str(dividend_amount))

        if earnings_per_share is not None:
            self.earnings_per_share = Decimal(str(earnings_per_share))

        if price_to_earnings_ratio is not None:
            self.price_to_earnings_ratio = Decimal(str(price_to_earnings_ratio))

        if market_capitalization is not None:
            self.market_capitalization = ibkr.common.get_number_from_text_with_suffixes(market_capitalization)

        if open_price is not None:
            self.open_price = Decimal(str(open_price))

        if low_price is not None:
            self.low_price = Decimal(str(low_price))

        if high_price is not None:
            self.high_price = Decimal(str(high_price))

        if close_price is not None:
            self.close_price = Decimal(str(close_price))

        if option_volume is not None:
            self.option_volume = Decimal(str(ibkr.common.get_number_from_text_with_suffixes(option_volume)))

        if dividend_yield is not None:
            self.dividend_yield = Decimal(str(dividend_yield).replace("%", ""))

    @classmethod
    def get(cls, symbol: str, instrument_type: InstrumentType, exchange: StockExchanges) -> "Instrument":
        stock_search_results: StockSearchResults = StockSearchResults.call(symbol)
        contract_id: int = None

        if stock_search_results.stock_search_results_list is None:
            raise StockNotFoundException()

        for stock_search_result in stock_search_results.stock_search_results_list:
            if stock_search_result.description == exchange.value:
                contract_id = stock_search_result.conid
                break

        contract: Contract = Contract.call(contract_id)
        market_data_snapshot: MarketDataSnapshot = MarketDataSnapshot.call(contract_id)

        if contract.instrument_type != instrument_type.value:
            raise StockNotFoundException()

        return Instrument(contract.symbol, contract.con_id, contract.instrument_type, contract.valid_exchanges,
                          contract.exchange, contract.company_name, market_data_snapshot.open_price,
                          market_data_snapshot.close_price, market_data_snapshot.current_day_high_price,
                          market_data_snapshot.current_day_low_price, market_data_snapshot.last_price,
                          market_data_snapshot.change_in_currency, market_data_snapshot.change_in_percentage,
                          market_data_snapshot.bid_price, market_data_snapshot.ask_price, market_data_snapshot.ask_size,
                          market_data_snapshot.bid_size, market_data_snapshot.volume, market_data_snapshot.option_volume,
                          market_data_snapshot.dividend_amount, market_data_snapshot.dividend_yield,
                          market_data_snapshot.market_capitalization, market_data_snapshot.price_to_earnings_ratio,
                          market_data_snapshot.earnings_per_share)


@dataclass
class History:
    symbol: str
    high: Decimal
    low: Decimal
    open: Decimal
    close: Decimal
    timestamp: datetime.datetime

    def __init__(self, ticker: str, high: Decimal, low: Decimal, open_price: Decimal, close: Decimal, timestamp: datetime.datetime):
        self.ticker = ticker
        self.high = high
        self.low = low
        self.open = open_price
        self.close = close
        self.timestamp = timestamp

    @classmethod
    def get(cls, symbol: str, instrument_type: InstrumentType, exchange: StockExchanges, period: str = "10y", bar: str = "1d") -> List["History"]:
        stock: Instrument = Instrument.get(symbol, instrument_type, exchange)
        market_data_history: MarketDataHistory = MarketDataHistory.call(stock.contract_id, period, bar)
        stock_history_list: List[History] = []
        for past_market_data in market_data_history.market_data_history:
            stock_history_list.append(History(symbol, past_market_data.high, past_market_data.low,
                                              past_market_data.open, past_market_data.close,
                                              past_market_data.timestamp))
        return stock_history_list


@dataclass
class Position:
    description: str
    position_size: Decimal
    market_price: Decimal
    market_value: Decimal
    instrument_type: InstrumentType
    currency: Currency
    account_id: str

    def __init__(self, description: str, position_size: float, market_price: float, market_value: float,
                 instrument_type: str, currency: str, account_id: str):
        self.description = description
        self.position_size = Decimal(str(position_size))
        self.market_price = Decimal(str(market_price))
        self.market_value = Decimal(str(market_value))
        self.account_id = account_id
        self.instrument_type = global_common.get_enum_from_value(instrument_type, InstrumentType)
        self.currency = global_common.get_enum_from_value(currency, Currency)

    @classmethod
    def get_all_by_account_id(cls, account_id: str) -> List["Position"]:
        portfolio_positions: PortfolioPositions = PortfolioPositions.call(account_id)
        all_positions: List[Position] = []

        if portfolio_positions.portfolio_positions_list is not None:
            for portfolio_position in portfolio_positions.portfolio_positions_list:
                all_positions.append(Position(portfolio_position.contractDesc,
                                              portfolio_position.position, portfolio_position.mktPrice,
                                              portfolio_position.mktValue, portfolio_position.assetClass,
                                              portfolio_position.currency, account_id))
        return all_positions


@dataclass
class Account:
    account_id: str
    alias: str

    def __init__(self, account_id: str, alias: str):
        self.account_id = account_id
        self.alias = alias

    @classmethod
    def get_all(cls) -> List["Account"]:
        portfolio_accounts: PortfolioAccounts = PortfolioAccounts.call()
        all_accounts_list: List[Account] = []
        for portfolio_account in portfolio_accounts.portfolio_account_list:
            all_accounts_list.append(Account(portfolio_account.accountId, portfolio_account.accountAlias))

        return all_accounts_list


@dataclass
class PlaceOrder:
    symbol: str
    secType: InstrumentType
    orderType: OrderType
    side: OrderSide
    quantity: Decimal
    account_id: str
    price: Decimal = None
    custom_order_id: str = str(uuid.uuid4())
    outsideRTH: bool = True
    tif: OrderTimeInForce = OrderTimeInForce.GOOD_TILL_CANCEL

    def __init__(self, symbol: str, orderType: OrderType, side: OrderSide, quantity: int, price: float, account_id: str):

        self.symbol = symbol
        self.orderType = orderType
        self.side = side
        self.quantity = Decimal(str(quantity))

        if orderType != OrderType.MARKET:
            self.price = Decimal(str(price))
        else:
            self.outsideRTH = False

        self.account_id = account_id

    def execute(self) -> "PlaceOrderResponse":
        communication.telegram.send_message(communication.telegram.constants.telegram_channel_username_development,
                                            f"<u><b>Placing a new order</b></u>\n\nSymbol: <i>{self.symbol}</i>\nOrder "
                                            f"Type: "
                                            f"<i>{self.orderType.value}</i>\nQuantity: <i>{str(self.quantity)}</i>\nPrice: "
                                            f"<i>{str(self.price)}</i>\nAccount ID: <i>{self.account_id}</i>", True)

        stock: Instrument = Instrument.get(self.symbol, InstrumentType.STOCK, StockExchanges.NASDAQ)

        price: float = None
        if self.price is not None:
            price = float(self.price)

        order_response: PlaceOrderResponse = PlaceOrderResponse(ibkr_models.PlaceOrder.call(self.account_id,
                                                                                            stock.contract_id,
                                                                                            self.orderType.value, self.outsideRTH,
                                                                                            self.side.value, self.tif.value,
                                                                                            int(self.quantity), self.custom_order_id,
                                                                                            price))

        if order_response.is_order_placed:
            communication.telegram.send_message(communication.telegram.constants.telegram_channel_username_development,
                                                f"<u><b>Order has been placed successfully</b></u>"
                                                f"\n\nSymbol: <i>{self.symbol}</i>"
                                                f"\nOrder Type: <i>{self.orderType.value}</i>"
                                                f"\nQuantity: <i>{str(self.quantity)}</i>"
                                                f"\nPrice: <i>{str(price)}</i>"
                                                f"\nAccount ID: <i>{self.account_id}</i>", True)
        else:
            communication.telegram.send_message(communication.telegram.constants.telegram_channel_username_development,
                                                f"<u><b>ERROR: Order has not been placed</b></u>"
                                                f"\n\nSymbol: <i>{self.symbol}</i>"
                                                f"\nOrder Type: <i>{self.orderType.value}</i>"
                                                f"\nQuantity: <i>{str(self.quantity)}</i>"
                                                f"\nPrice: <i>{str(price)}</i>"
                                                f"\nAccount ID: <i>{self.account_id}</i>"
                                                f"\nResponse Message: <i>{ibkr.common.get_html_commented(order_response.response_text)}</i>",
                                                True)
        return order_response


@dataclass
class CancelOrder:
    unfilled_order: "UnfilledOrder"
    account_id: str
    order_id: str

    def __init__(self, unfilled_order: "UnfilledOrder"):
        self.unfilled_order = unfilled_order
        self.account_id = self.unfilled_order.account_id
        self.order_id = self.unfilled_order.order_id

    def execute(self) -> "CancelOrderResponse":
        communication.telegram.send_message(communication.telegram.constants.telegram_channel_username_development,
                                            f"<u><b>Cancelling an unfilled order</b></u>"
                                            f"\n\nSymbol: <i>{self.unfilled_order.symbol}</i>\n"
                                            f"\nUnfilled Quantity: <i>{str(self.unfilled_order.unfilled_quantity)}</i>"
                                            f"\nOrder Type: {self.unfilled_order.order_type.value}"
                                            f"\nPrice: <i>{str(self.unfilled_order.price)}</i>"
                                            f"\nAccount ID: <i>{self.account_id}</i>", True)

        cancel_order_response: CancelOrderResponse = CancelOrderResponse(ibkr.ibkr_models.CancelOrder.call(self.account_id, self.order_id))

        if not cancel_order_response.is_order_cancelled:
            communication.telegram.send_message(communication.telegram.constants.telegram_channel_username_development,
                                                f"<u><b>ERROR: Order has not been cancelled</b></u>"
                                                f"\n\nSymbol: <i>{self.unfilled_order.symbol}</i>\n"
                                                f"\nUnfilled Quantity: <i>{str(self.unfilled_order.unfilled_quantity)}</i>"
                                                f"\nOrder Type: {self.unfilled_order.order_type.value}"
                                                f"\nPrice: <i>{str(self.unfilled_order.price)}</i>"
                                                f"\nAccount ID: <i>{self.account_id}</i>", True)

        return cancel_order_response

class CancelOrderResponse:
    is_order_cancelled: bool
    order_id: str
    contract_id: int
    account_id: str
    response_message: str

    def __init__(self, cancel_order_response: ibkr.ibkr_models.CancelOrderResponse):
        self.order_id = cancel_order_response.order_id
        self.contract_id = cancel_order_response.conid
        self.account_id = cancel_order_response.account
        self.response_message = cancel_order_response.msg
        self.is_order_cancelled = cancel_order_response.is_successful


@dataclass
class PlaceOrderResponse:
    is_order_placed: bool
    ibkr_order_id: str
    order_id: str
    order_cancelled: datetime.datetime
    response_text: str

    def __init__(self, order_response: ibkr_models.PlaceOrderResponse):
        self.is_order_placed = order_response.is_successful and order_response.order_status == OrderStatus.SUBMITTED.value
        self.ibkr_order_id = order_response.order_id
        self.order_id = order_response.order_id
        self.response_text = order_response.text

        if order_response.text is not None and "will be automatically canceled at 20220101 13:00:00 HKT" in \
                order_response.text:
            datetime_string: str = order_response.text.split("will be automatically canceled at ")[-1].replace(" HKT",
                                                                                                               "")
            self.order_cancelled = pytz.timezone("Asia/Hong_Kong").localize(
                datetime.datetime.strptime(datetime_string, "%Y%m%d %H:%M:%S"))


@dataclass
class UnfilledOrder:
    account_id: str
    exchange: StockExchanges
    contract_id: int
    order_id: str
    currency: Currency
    unfilled_quantity: Decimal
    filled_quantity: Decimal
    order_description: str
    symbol: str
    security_type: InstrumentType
    status: str
    order_type: OrderType
    last_execution_time: datetime.datetime
    custom_order_id: str
    price: Decimal
    time_in_force: OrderTimeInForce
    side: OrderSide

    def __init__(self, live_order: LiveOrder):
        self.account_id = live_order.acct
        self.exchange = global_common.get_enum_from_value(live_order.exchange, StockExchanges)
        self.contract_id = live_order.conid
        self.order_id = live_order.orderId
        self.currency = global_common.get_enum_from_value(live_order.cashCcy, Currency)
        self.unfilled_quantity = Decimal(str(live_order.remainingQuantity))
        self.filled_quantity = Decimal(str(live_order.filledQuantity))
        self.order_description = live_order.orderDesc
        self.symbol = live_order.ticker
        self.security_type = global_common.get_enum_from_value(live_order.secType, InstrumentType)
        self.status = live_order.status
        self.last_execution_time = datetime.datetime.utcfromtimestamp(int(live_order.lastExecutionTime_r / 1000))
        self.custom_order_id = live_order.order_ref
        self.time_in_force = global_common.get_enum_from_value(live_order.timeInForce, OrderTimeInForce)
        self.side = global_common.get_enum_from_value(live_order.side, OrderSide)

        if live_order.orderType == "Limit":
            self.order_type = OrderType.LIMIT
        elif live_order.orderType == "Market":
            self.order_type = OrderType.MARKET

        if self.order_type is not OrderType.MARKET:
            self.price = Decimal(str(live_order.price))
        else:
            self.price = None

    @classmethod
    def get(cls) -> List["UnfilledOrder"]:
        live_orders: LiveOrders = LiveOrders.call()

        unfilled_orders_list: List[UnfilledOrder] = []
        for live_order in live_orders.live_orders_list:
            if live_order.status != OrderStatus.INACTIVE.value and live_order.status != OrderStatus.CANCELLED.value:
                unfilled_orders_list.append(UnfilledOrder(live_order))

        return unfilled_orders_list

    @classmethod
    def get_all_unfilled_orders_value(cls, exchange: StockExchanges) -> Decimal:
        value: Decimal = Decimal("0")
        for unfilled_order in UnfilledOrder.get():
            value_of_order: Decimal = None
            if unfilled_order.order_type == OrderType.LIMIT:
                value_of_order = unfilled_order.price * unfilled_order.unfilled_quantity
            elif unfilled_order.order_type == OrderType.MARKET:
                value_of_order = Instrument.get(unfilled_order.symbol, InstrumentType.STOCK, exchange).last_price * \
                                 unfilled_order.unfilled_quantity

            value = value + value_of_order

        return value


@dataclass()
class AccountInformation:
    available_funds: Decimal
    currency: Currency
    updated_at: datetime.datetime

    def __init__(self, account_information: ibkr_models.AccountInformation):
        self.available_funds = Decimal(str(account_information.fullavailablefunds.amount))
        self.currency = global_common.get_enum_from_value(account_information.fullavailablefunds.currency, Currency)
        self.updated_at = datetime.datetime.utcfromtimestamp(int(account_information.fullavailablefunds.timestamp / 1000))

    @classmethod
    def get_by_account_id(cls, account_id: str) -> "AccountInformation":
        return AccountInformation(ibkr_models.AccountInformation.call(account_id))