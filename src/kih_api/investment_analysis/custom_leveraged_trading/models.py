from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Union

from kih_api.ibkr.helper import HistoricalDataHelper
from kih_api.ibkr.models import HistoricalData, IBKR
from kih_api.investment_analysis import calculations
from kih_api.investment_analysis.custom_leveraged_trading.helper import InvestmentAnalysisHelper
from kih_api.investment_analysis.models import Statistics


@dataclass
class HistoricalReturn:
    date: datetime
    number_of_shares_bought: Decimal
    net_liquidity: Decimal
    close: Decimal


@dataclass
class InvestmentAnalysis:
    symbol: str
    starting_date: datetime
    ending_date: datetime
    raw_historical_data_list: List[HistoricalData]
    historical_data_list: List[HistoricalData]
    historical_returns_list: List[HistoricalReturn]
    profit: Decimal
    annual_rate_of_return: Decimal
    number_of_days_till_no_loss: Decimal
    lowest_net_liquidity: Decimal

    def __init__(self, symbol: str, starting_balance: Decimal, daily_leverage: Decimal, starting_date: Union[datetime, str] = None, ending_date: Union[datetime, str] = None, raw_historical_data_list: List[HistoricalData] = None):
        starting_date = datetime.utcfromtimestamp(1) if starting_date is None else datetime.strptime(starting_date, '%Y-%m-%d') if isinstance(starting_date, str) else starting_date
        ending_date = datetime.today() if ending_date is None else datetime.strptime(ending_date, '%Y-%m-%d') if isinstance(ending_date, str) else ending_date

        self.symbol = symbol
        self.raw_historical_data_list = IBKR.get_historical_data(symbol) if raw_historical_data_list is None else raw_historical_data_list
        self.historical_data_list = HistoricalDataHelper.filter_historical_data_list(starting_date, ending_date, self.raw_historical_data_list)
        self.starting_date = self.historical_data_list[0].timestamp
        self.ending_date = self.historical_data_list[-1].timestamp
        self.historical_returns_list = InvestmentAnalysisHelper.get_leveraged_historical_data_list(starting_balance, daily_leverage, self.historical_data_list)
        self.profit = self.historical_returns_list[-1].net_liquidity - starting_balance
        self.annual_rate_of_return = calculations.get_annual_rate_of_return(starting_balance, self.historical_returns_list[-1].net_liquidity, calculations.get_year_frac(self.starting_date, self.ending_date))
        self.number_of_days_till_no_loss, self.lowest_net_liquidity = InvestmentAnalysisHelper.get_number_of_days_till_no_loss(self.historical_returns_list)


@dataclass
class InvestmentAnalysisStatistics:
    profit: Statistics
    annual_rate_of_return: Statistics
    number_of_days_till_no_loss: Statistics
    lowest_net_liquidity: Statistics

    def __init__(self, investment_analysis_list: List[InvestmentAnalysis]):
        self.profit = Statistics([data.profit for data in investment_analysis_list])
        self.annual_rate_of_return = Statistics([data.annual_rate_of_return for data in investment_analysis_list])
        self.number_of_days_till_no_loss = Statistics([data.number_of_days_till_no_loss for data in investment_analysis_list])
        self.lowest_net_liquidity = Statistics([data.lowest_net_liquidity for data in investment_analysis_list])


@dataclass
class InvestmentAnalysisSimulation:
    symbol: str
    investment: Decimal
    leverage: Decimal
    starting_date: datetime
    ending_date: datetime
    number_of_years_of_investment: Decimal
    investment_analysis_list: List[InvestmentAnalysis]
    raw_historical_data_list: List[HistoricalData]
    investment_analysis_statistics: InvestmentAnalysisStatistics

    def __init__(self, symbol: str, investment: Decimal, leverage: Decimal, starting_date: Union[datetime, str], ending_date: Union[datetime, str], number_of_years_of_investment: Decimal,
                 raw_historical_data_list: List[HistoricalData] = None):
        self.starting_date = datetime.utcfromtimestamp(1) if starting_date is None else datetime.strptime(starting_date, '%Y-%m-%d') if isinstance(starting_date, str) else starting_date
        self.ending_date = datetime.today() if ending_date is None else datetime.strptime(ending_date, '%Y-%m-%d') if isinstance(ending_date, str) else ending_date

        self.symbol = symbol
        self.investment = investment
        self.leverage = leverage
        self.number_of_years_of_investment = Decimal(str(number_of_years_of_investment))
        self.raw_historical_data_list = IBKR.get_historical_data(self.symbol) if raw_historical_data_list is None else raw_historical_data_list
        self.get_investment_analysis_list()
        self.investment_analysis_statistics = InvestmentAnalysisStatistics(self.investment_analysis_list)

    def get_investment_analysis_list(self) -> None:
        self.investment_analysis_list = []
        investment_starting_date = max(self.starting_date, self.raw_historical_data_list[0].timestamp)
        next_investment_starting_date: datetime = investment_starting_date
        next_investment_ending_date = calculations.add_years_to_date(next_investment_starting_date, self.number_of_years_of_investment)

        while next_investment_ending_date <= min(self.ending_date, self.raw_historical_data_list[-1].timestamp):
            self.investment_analysis_list.append(
                InvestmentAnalysis(self.symbol, self.investment, self.leverage, starting_date=next_investment_starting_date, ending_date=next_investment_ending_date, raw_historical_data_list=self.raw_historical_data_list))

            next_investment_starting_date = next_investment_starting_date + timedelta(days=1)
            next_investment_ending_date = calculations.add_years_to_date(next_investment_starting_date, self.number_of_years_of_investment)
