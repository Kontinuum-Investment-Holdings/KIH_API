import typing
from datetime import datetime
from decimal import Decimal
from typing import List
from typing import Tuple

from kih_api.ibkr.models import HistoricalData

if typing.TYPE_CHECKING:
    from kih_api.investment_analysis.custom_leveraged_trading.models import HistoricalData, HistoricalReturn


class InvestmentAnalysisHelper:

    @staticmethod
    def get_leveraged_historical_data_list(starting_balance: Decimal, leverage: Decimal, historical_data_list: List["HistoricalData"]) -> List["HistoricalReturn"]:
        from kih_api.investment_analysis.custom_leveraged_trading.models import HistoricalReturn
        historical_returns_list: List[HistoricalReturn] = []

        number_of_shares_bought: Decimal = Decimal(0)
        loan_amount: Decimal = Decimal(0)
        for historical_data in historical_data_list:
            if historical_data == historical_data_list[0]:
                cash_balance: Decimal = starting_balance
            else:
                cash_balance = (number_of_shares_bought * historical_data.close) - loan_amount if number_of_shares_bought != Decimal(0) else cash_balance

            if cash_balance <= Decimal(0):
                historical_returns_list.append(HistoricalReturn(historical_data.timestamp, Decimal(0), Decimal(0), historical_data.close))
                return historical_returns_list

            number_of_shares_bought = Decimal(int((cash_balance * leverage) / historical_data.close))
            loan_amount = (number_of_shares_bought * historical_data.close) - cash_balance if (number_of_shares_bought * historical_data.close) > cash_balance else Decimal(0)
            net_liquidity = (number_of_shares_bought * historical_data.close) - loan_amount if (number_of_shares_bought * historical_data.close) > cash_balance else cash_balance

            historical_returns_list.append(HistoricalReturn(historical_data.timestamp, number_of_shares_bought, net_liquidity, historical_data.close))
        return historical_returns_list

    @staticmethod
    def get_number_of_days_till_no_loss(historical_returns_list: List["HistoricalReturn"]) -> Tuple[Decimal, Decimal]:
        starting_date: datetime = historical_returns_list[0].date
        lowest_net_liquidity: Decimal = historical_returns_list[0].net_liquidity
        number_of_days_till_no_loss: Decimal = Decimal(0)
        for historical_return in historical_returns_list:
            number_of_days_till_no_loss = Decimal((historical_return.date - starting_date).days) if historical_return.net_liquidity < lowest_net_liquidity else number_of_days_till_no_loss
            lowest_net_liquidity = historical_return.net_liquidity if historical_return.net_liquidity < lowest_net_liquidity else lowest_net_liquidity
        return number_of_days_till_no_loss, lowest_net_liquidity

