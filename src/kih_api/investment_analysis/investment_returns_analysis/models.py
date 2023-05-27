from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

from dateutil.relativedelta import relativedelta
from mongoengine import FloatField, EmbeddedDocument, DateTimeField

from kih_api.investment_analysis import calculations


@dataclass
class InvestmentReturn(EmbeddedDocument):
    date: datetime = DateTimeField(required=True)
    profit: Decimal = FloatField(required=True)
    capital: Decimal = FloatField(required=True)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.profit = Decimal(str(self.profit))
        self.capital = Decimal(str(self.capital))

    @staticmethod
    def get_investment_return(starting_date: datetime, starting_capital: Decimal, annual_rate_of_return: Decimal, number_of_years_of_investment: Decimal) -> "InvestmentReturn":
        investment_return: InvestmentReturn = InvestmentReturn.get_monthly_investment_returns_list(starting_date, starting_capital, annual_rate_of_return, number_of_years_of_investment)[-1]
        return InvestmentReturn(
            date=investment_return.date,
            profit=(investment_return.capital - starting_capital),
            capital=investment_return.capital
        )

    @staticmethod
    def get_monthly_investment_returns_list(starting_date: datetime, starting_capital: Decimal, annual_rate_of_return: Decimal, number_of_years_of_investment: Decimal) -> List["InvestmentReturn"]:
        monthly_return: Decimal = calculations.get_monthly_rate_of_return_from_annual(annual_rate_of_return)
        investment_returns_list: List[InvestmentReturn] = []
        end_date: datetime = starting_date + relativedelta(months=int(number_of_years_of_investment * Decimal("12")))
        date: datetime = starting_date
        capital: Decimal = starting_capital

        while date < end_date:
            profit: Decimal = capital * monthly_return
            capital = capital + profit
            date = date + relativedelta(months=1)

            investment_returns_list.append(InvestmentReturn(profit=profit, capital=capital, date=date))

        return investment_returns_list
