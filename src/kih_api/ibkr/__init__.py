import threading
import time
from typing import Dict, Any, List

from ibapi.client import EClient
from ibapi.common import TickAttrib, BarData, OrderId
from ibapi.contract import Contract, ContractDetails
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper

from kih_api.ibkr import constants


class IBKR_API(EWrapper, EClient):
    data: Dict[str, List[Any]] = {}
    next_order_id: int

    def __init__(self) -> None:
        self.data = {}
        EClient.__init__(self, self)

    def save_data(self, key: str, data: Any) -> None:
        if isinstance(data, Dict) and data.get("self") is not None:
            data.pop("self")

        if self.data.get(key) is None:
            self.data[key] = [data]
        else:
            self.data[key].append(data)

    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: TickAttrib) -> None:
        self.save_data("ask_price", locals())

    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState: OrderState) -> None:
        self.save_data("order_status", locals())

    def nextValidId(self, orderId: int) -> None:
        self.next_order_id = orderId
        self.save_data("next_order_id", locals())

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str) -> None:
        super().accountSummary(reqId, account, tag, value, currency)
        self.save_data("account_summary", locals())

    def accountSummaryEnd(self, reqId: int) -> None:
        super().accountSummaryEnd(reqId)
        self.save_data("account_summary_end", locals())

    def position(self, account: str, contract: Contract, position: float, avgCost: float) -> None:
        super().position(account, contract, position, avgCost)
        self.save_data("positions", locals())

    def positionEnd(self) -> None:
        super().positionEnd()
        self.save_data("positions_end", locals())

    def historicalData(self, reqId: int, bar: BarData) -> None:
        self.save_data("historical_data", locals())

    def historicalDataEnd(self, reqId: int, start: str, end: str) -> None:
        super().historicalDataEnd(reqId, start, end)
        self.save_data("historical_data_end", locals())

    def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float) -> None:
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        self.save_data("order_status", locals())

    def openOrderEnd(self) -> None:
        super().openOrderEnd()
        self.save_data("order_status_end", locals())

    def managedAccounts(self, accountsList: str) -> None:
        super().managedAccounts(accountsList)
        self.save_data("managed_accounts", locals())

    def contractDetails(self, reqId: int, contractDetails: ContractDetails) -> None:
        super().contractDetails(reqId, contractDetails)
        self.save_data("contract_details", locals())

    def contractDetailsEnd(self, reqId: int) -> None:
        super().contractDetailsEnd(reqId)
        self.save_data("contract_details_end", locals())

    def disconnect(self) -> None:
        super().disconnect()
        time.sleep(constants.WAIT_TIME_IN_SECONDS)


def connect_to_ib_api(ibkr_api: IBKR_API) -> None:
    ibkr_api.connect(constants.WEB_SOCKET_IP, constants.WEB_SOCKET_PORT, constants.CLIENT_ID)
    api_thread = threading.Thread(target=ibkr_api.run, daemon=True)
    api_thread.start()
    time.sleep(constants.WAIT_TIME_IN_SECONDS)
