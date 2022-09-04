import datetime
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from kih_api.investment_analysis import calculations
from kih_api.investment_analysis.models import Statistics, HistoricalStockPriceData, NumberOfYearsTillPerpetualProfit


@dataclass
class StockAnalysis:
    stock_symbol: str
    analysis_start_date: datetime.datetime
    analysis_end_date: datetime.datetime
    historical_data_list: List[HistoricalStockPriceData]
    investment_time_frame: Decimal
    absolute_return: Optional[Statistics]
    annualized_return: Optional[Statistics]
    number_of_years_till_perpetual_profit: NumberOfYearsTillPerpetualProfit

    def __init__(self, stock_symbol: str, analysis_start_date: str, analysis_end_date: str, investment_time_frame: float):
        self.stock_symbol = stock_symbol
        self.analysis_start_date = datetime.datetime.strptime(analysis_start_date, "%Y-%m-%d")
        self.analysis_end_date = datetime.datetime.strptime(analysis_end_date, "%Y-%m-%d")
        self.investment_time_frame = Decimal(str(investment_time_frame))
        self.get_historical_data()
        self.calculate()

    def get_historical_data(self) -> None:
        all_historical_data_list: List[HistoricalStockPriceData] = HistoricalStockPriceData.get(self.stock_symbol)
        filtered_historical_data_list: List[HistoricalStockPriceData] = list(filter(lambda data: self.analysis_start_date <= data.timestamp <= self.analysis_end_date, all_historical_data_list))
        sorted_historical_data_list: List[HistoricalStockPriceData] = sorted(filtered_historical_data_list, key=lambda data: data.timestamp)
        self.historical_data_list = sorted_historical_data_list

    def calculate(self) -> None:
        self.calculate_returns()
        self.calculate_number_of_years_till_no_loss()

    def calculate_returns(self) -> None:
        absolute_return_list: List[Dict[datetime.datetime, Decimal]] = []
        annualized_return_list: List[Dict[datetime.datetime, Decimal]] = []

        for starting_historical_data in self.historical_data_list:
            end_date: datetime.datetime = calculations.add_years_to_date(starting_historical_data.timestamp, self.investment_time_frame)
            ending_historical_data: HistoricalStockPriceData = HistoricalStockPriceData.get_from_date(end_date, self.historical_data_list)

            if ending_historical_data is None:
                break

            year_frac: Decimal = calculations.get_year_frac(starting_historical_data.timestamp, ending_historical_data.timestamp)

            absolute_return: Decimal = calculations.get_annual_rate_of_return(starting_historical_data.close, ending_historical_data.close, Decimal("1"))
            annualized_return: Decimal = calculations.get_annual_rate_of_return(starting_historical_data.close, ending_historical_data.close, year_frac)

            absolute_return_list.append({starting_historical_data.timestamp: absolute_return})
            annualized_return_list.append({starting_historical_data.timestamp: annualized_return})

        if len(absolute_return_list) > 0:
            self.absolute_return = Statistics.get([data[next(iter(data))] for data in absolute_return_list])
            self.absolute_return.data = absolute_return_list

        if len(annualized_return_list) > 0:
            self.annualized_return = Statistics.get([data[next(iter(data))] for data in annualized_return_list])
            self.annualized_return.data = annualized_return_list

    def calculate_number_of_years_till_no_loss(self) -> None:
        start_time = time.time_ns()
        self.number_of_years_till_perpetual_profit = NumberOfYearsTillPerpetualProfit.get_from_historical_stock_price_data_list(self.historical_data_list, True)
        print(f"Time taken: {(time.time_ns() - start_time) / 1_000_000_000 / 60} minutes")


test = StockAnalysis("TQQQ", "2010-01-01", "2023-01-01", 3)
