import datetime
import statistics
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import List, Any, Optional, cast, Dict

from mongoengine import StringField, FloatField, DateTimeField, EmbeddedDocumentField, EmbeddedDocument, ListField

import kih_api.ibkr.models
from kih_api.database.models import DatabaseDocument
from kih_api.investment_analysis import calculations


@dataclass
class Statistics(EmbeddedDocument):
    maximum: Decimal = FloatField(required=True)
    median: Decimal = FloatField(required=True)
    average: Decimal = FloatField(required=True)
    minimum: Decimal = FloatField(required=True)
    standard_deviation: Decimal = FloatField(required=True)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.maximum = Decimal(str(self.maximum))
        self.median = Decimal(str(self.median))
        self.average = Decimal(str(self.average))
        self.minimum = Decimal(str(self.minimum))
        self.standard_deviation = Decimal(str(self.standard_deviation))

    @staticmethod
    def get(data: List[Decimal]) -> "Statistics":
        return Statistics(
            **{"maximum": Decimal(str(max(data))),
               "median": Decimal(str(statistics.median(data))),
               "average": Decimal(str(statistics.mean(data))),
               "minimum": Decimal(str(min(data))),
               "standard_deviation": Decimal(str(statistics.stdev(data)))}
        )


class HistoricalStockPriceData(DatabaseDocument):
    stock_symbol: str = StringField(required=True)
    open: Decimal = FloatField()
    high: Decimal = FloatField()
    low: Decimal = FloatField()
    close: Decimal = FloatField(required=True)
    volume: Decimal = FloatField()
    timestamp: datetime.datetime = DateTimeField(required=True)

    meta = {"indexes": ["stock_symbol", "timestamp"]}

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.open = Decimal(str(self.open))
        self.high = Decimal(str(self.high))
        self.low = Decimal(str(self.low))
        self.close = Decimal(str(self.close))
        self.volume = Decimal(str(self.volume))

    @staticmethod
    def get(stock_symbol: str, from_date: datetime.datetime = datetime.datetime.now().replace(year=(datetime.datetime.now().year - 10))) -> List["HistoricalStockPriceData"]:
        historical_data_list: List[HistoricalStockPriceData] = sorted(cast(List[HistoricalStockPriceData], HistoricalStockPriceData.objects(stock_symbol=stock_symbol, timestamp__gte=from_date)), key=lambda data: data.timestamp)

        if len(historical_data_list) > 0 and historical_data_list[-1].timestamp.date() == datetime.datetime.now().date():
            return historical_data_list

        updated_historical_data_list: List["HistoricalStockPriceData"] = HistoricalStockPriceData.get_updated_data(stock_symbol, historical_data_list[-1].timestamp if len(historical_data_list) > 0 else from_date)
        return historical_data_list + updated_historical_data_list

    @staticmethod
    def get_updated_data(stock_symbol: str, from_date: datetime.datetime) -> List["HistoricalStockPriceData"]:
        new_historical_data_list: List[HistoricalStockPriceData] = []
        if kih_api.ibkr.models.IBKR.is_connection_successful():
            new_historical_data_list = HistoricalStockPriceData.get_from_ibkr(stock_symbol, from_date)

        if len(new_historical_data_list) > 1:
            HistoricalStockPriceData.objects.insert(new_historical_data_list)

        return new_historical_data_list

    @staticmethod
    def get_from_ibkr(stock_symbol: str, from_date: datetime.datetime = datetime.datetime.now().replace(year=(datetime.datetime.now().year - 10))) -> List["HistoricalStockPriceData"]:
        historical_data_list: List[HistoricalStockPriceData] = []
        ibkr_historical_data_list: List[
            kih_api.ibkr.models.HistoricalData] = kih_api.ibkr.models.IBKR.get_historical_data(stock_symbol)
        for ibkr_historical_data in ibkr_historical_data_list:
            if ibkr_historical_data.timestamp > from_date:
                ibkr_historical_data_dict: Dict[str, Any] = asdict(ibkr_historical_data)
                ibkr_historical_data_dict.pop("average")
                ibkr_historical_data_dict["stock_symbol"] = stock_symbol
                historical_data_list.append(HistoricalStockPriceData(**ibkr_historical_data_dict))

        return historical_data_list

    @staticmethod
    def get_from_date(date: datetime.datetime, historical_data_list: List["HistoricalStockPriceData"], is_get_next_date_if_unavailable: bool = True) -> Optional["HistoricalStockPriceData"]:
        filtered_historical_data_list: List[HistoricalStockPriceData] = sorted(list(filter(lambda data: data.timestamp >= date, historical_data_list)), key=lambda data: data.timestamp)
        if len(filtered_historical_data_list) == 0 or (not is_get_next_date_if_unavailable and filtered_historical_data_list[0] != date):
            return None
        return filtered_historical_data_list[0]


class PerpetualProfitDate(EmbeddedDocument):
    investment_date: datetime.datetime = DateTimeField(required=True)
    perpetual_profit_date: datetime.datetime = DateTimeField(required=True)
    number_of_years: Decimal = FloatField(required=True)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.number_of_years = Decimal(str(self.number_of_years))


class NumberOfYearsTillPerpetualProfit(DatabaseDocument):
    stock_symbol: str = StringField(primary_key=True)
    data: List[PerpetualProfitDate] = ListField(EmbeddedDocumentField(PerpetualProfitDate))
    statistics: Statistics = EmbeddedDocumentField(Statistics)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_from_historical_stock_price_data_list(historical_stock_price_data: List[HistoricalStockPriceData], update_database: bool = False) -> "NumberOfYearsTillPerpetualProfit":
        perpetual_profit_date_list: List[PerpetualProfitDate] = []
        if len(historical_stock_price_data) == 0:
            raise Exception("No market data")

        for historical_data in historical_stock_price_data:
            profit_historical_data_list: List[HistoricalStockPriceData] = list(filter(lambda data: data.close >= historical_data.close and data.timestamp > historical_data.timestamp, historical_stock_price_data))

            date_of_no_loss: datetime.datetime = None

            for profit_historical_data in profit_historical_data_list:
                future_loss_historical_data_list: List[HistoricalStockPriceData] = list(filter(lambda data: data.close < historical_data.close and data.timestamp > profit_historical_data.timestamp, historical_stock_price_data))
                if len(future_loss_historical_data_list) == 0:
                    date_of_no_loss = profit_historical_data.timestamp
                    break

            if date_of_no_loss is None:
                continue

            year_frac: Decimal = calculations.get_year_frac(historical_data.timestamp, date_of_no_loss)
            perpetual_profit_date_list.append(PerpetualProfitDate(investment_date=historical_data.timestamp, perpetual_profit_date=date_of_no_loss, number_of_years=year_frac))

        number_of_years_till_perpetual_profit: NumberOfYearsTillPerpetualProfit = NumberOfYearsTillPerpetualProfit(
            stock_symbol=historical_stock_price_data[0].stock_symbol,
            data=perpetual_profit_date_list,
            statistics=Statistics.get([perpetual_profit_date.number_of_years for perpetual_profit_date in perpetual_profit_date_list])
        )

        if update_database:
            number_of_years_till_perpetual_profit.save()

        return number_of_years_till_perpetual_profit
