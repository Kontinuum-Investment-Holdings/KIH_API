import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Any, Dict

from requests import Response

from kih_api import http_requests
from kih_api.http_requests.models import ResponseObject
from kih_api.ibkr_web_api import constants
from kih_api.ibkr_web_api.exceptions import StockNotFoundException, MarketOrderOutsideRTHException


@dataclass
class KeepAlive(ResponseObject):
    session: Optional[str] = None
    ssoExpires: Optional[int] = None
    collission: Optional[bool] = None
    userId: Optional[int] = None
    iserver: Optional[Dict[str, Any]] = None
    endpoint: str = constants.ENDPOINT_KEEP_ALIVE

    def __init__(self, session: str = None, ssoExpires: int = None, collission: bool = None, userId: int = None,
                 iserver: Dict[str, Any] = None, **kwargs: Any):
        self.session = session
        self.ssoExpires = ssoExpires
        self.collission = collission
        self.userId = userId
        self.iserver = iserver

    @classmethod
    def call(cls) -> "KeepAlive":
        response: Response = http_requests.get(cls.endpoint, None)
        return KeepAlive.create(response)

    @classmethod
    def create(cls, response: Response) -> "KeepAlive":
        if response.status_code == 200:
            keep_alive: KeepAlive = KeepAlive(**response.json())
        else:
            keep_alive = KeepAlive()

        keep_alive.response = response
        keep_alive.is_successful = 200 <= keep_alive.response.status_code < 300
        return keep_alive


@dataclass
class Authentication(ResponseObject):
    authenticated: Optional[bool] = None
    connected: Optional[bool] = None
    competing: Optional[bool] = None
    fail: Optional[str] = None
    message: Optional[str] = None
    prompts: Optional[List[str]] = None
    MAC: Optional[str] = None
    endpoint: str = constants.ENDPOINT_AUTHENTICATION_STATUS

    def __init__(self, authenticated: bool = None, connected: bool = None, competing: bool = None, fail: str = None,
                 message: str = None, prompts: List[str] = None, MAC: str = None, **kwargs: Any):
        self.authenticated = authenticated
        self.connected = connected
        self.competing = competing
        self.fail = fail
        self.message = message
        self.prompts = prompts
        self.MAC = MAC

    @classmethod
    def call(cls) -> "Authentication":
        response: Response = http_requests.get(cls.endpoint)
        return Authentication.create(response)

    @classmethod
    def create(cls, response: Response) -> "Authentication":
        if response.status_code == 200:
            authentication: Authentication = Authentication(**response.json())
        else:
            authentication = Authentication()

        authentication.response = response
        authentication.is_successful = 200 <= authentication.response.status_code < 300
        return authentication


@dataclass
class ReAuthentication(ResponseObject):
    authenticated: Optional[bool] = None
    connected: Optional[bool] = None
    competing: Optional[bool] = None
    fail: Optional[str] = None
    message: Optional[str] = None
    prompts: Optional[List[str]] = None
    endpoint = constants.ENDPOINT_RE_AUTHENTICATE

    def __init__(self, authenticated: bool = None, connected: bool = None, competing: bool = None, fail: str = None,
                 message: str = None, prompts: List[str] = None, **kwargs: Any):
        self.authenticated = authenticated
        self.connected = connected
        self.competing = competing
        self.fail = fail
        self.message = message
        self.prompts = prompts

    @classmethod
    def call(cls) -> "ReAuthentication":
        response: Response = http_requests.get(cls.endpoint)
        return ReAuthentication.create(response)

    @classmethod
    def create(cls, response: Response) -> "ReAuthentication":
        if response.status_code == 200:
            re_authentication: ReAuthentication = ReAuthentication(**response.json())
        else:
            re_authentication = ReAuthentication()

        re_authentication.response = response
        re_authentication.is_successful = 200 <= re_authentication.response.status_code < 300
        return re_authentication


@dataclass
class PortfolioAccount:
    id: Optional[str] = None
    accountId: Optional[str] = None
    accountVan: Optional[str] = None
    accountTitle: Optional[str] = None
    displayName: Optional[str] = None
    accountAlias: Optional[str] = None
    accountStatus: Optional[int] = None
    currency: Optional[str] = None
    type: Optional[str] = None
    tradingType: Optional[str] = None
    faclient: Optional[bool] = None
    clearingStatus: Optional[str] = None
    covestor: Optional[bool] = None
    parent: Optional[Dict[str, Any]] = None
    desc: Optional[str] = None

    def __init__(self, id: str = None, accountId: str = None, accountVan: str = None, accountTitle: str = None,
                 displayName: str = None, accountAlias: str = None, accountStatus: int = None, currency: str =
                 None, type: str = None, tradingType: str = None, faclient: bool = None, clearingStatus: str =
                 None, covestor: bool = None, parent: Dict[str, Any] = None, desc: str = None, **kwargs: Any):
        self.id = id
        self.accountId = accountId
        self.accountVan = accountVan
        self.accountTitle = accountTitle
        self.displayName = displayName
        self.accountAlias = accountAlias
        self.accountStatus = accountStatus
        self.currency = currency
        self.type = type
        self.tradingType = tradingType
        self.faclient = faclient
        self.clearingStatus = clearingStatus
        self.covestor = covestor
        self.parent = parent
        self.desc = desc


@dataclass
class PortfolioAccounts(ResponseObject):
    portfolio_account_list: Optional[List[PortfolioAccount]] = None
    endpoint = constants.ENDPOINT_PORTFOLIO_ACCOUNTS

    def __init__(self, data: List[Dict] = None, **kwargs: Any):
        if data is not None:
            self.portfolio_account_list = []
            for portfolio_account in data:
                self.portfolio_account_list.append(PortfolioAccount(**portfolio_account))

    @classmethod
    def call(cls) -> "PortfolioAccounts":
        response: Response = http_requests.get(cls.endpoint)
        return PortfolioAccounts.create(response)

    @classmethod
    def create(cls, response: Response) -> "PortfolioAccounts":
        if response.status_code == 200:
            portfolio_accounts: PortfolioAccounts = PortfolioAccounts(response.json())
        else:
            portfolio_accounts = PortfolioAccounts()

        portfolio_accounts.response = response
        portfolio_accounts.is_successful = 200 <= portfolio_accounts.response.status_code < 300
        return portfolio_accounts


@dataclass
class PortfolioPosition:
    acctId: Optional[str] = None
    conid: Optional[int] = None
    contractDesc: Optional[str] = None
    assetClass: Optional[str] = None
    position: Optional[int] = None
    mktPrice: Optional[int] = None
    mktValue: Optional[int] = None
    currency: Optional[str] = None
    avgCost: Optional[int] = None
    avgPrice: Optional[int] = None
    realizedPnl: Optional[int] = None
    unrealizedPnl: Optional[int] = None
    exchs: Optional[str] = None
    expiry: Optional[str] = None
    putOrCall: Optional[str] = None
    multiplier: Optional[int] = None
    strike: Optional[int] = None
    exerciseStyle: Optional[str] = None
    undConid: Optional[int] = None
    conExchMap: Optional[List[Any]] = None
    baseMktValue: Optional[int] = None
    baseMktPrice: Optional[int] = None
    baseAvgCost: Optional[int] = None
    baseAvgPrice: Optional[int] = None
    baseRealizedPnl: Optional[int] = None
    baseUnrealizedPnl: Optional[int] = None
    name: Optional[str] = None
    lastTradingDay: Optional[str] = None
    group: Optional[str] = None
    sector: Optional[str] = None
    sectorGroup: Optional[str] = None
    ticker: Optional[str] = None
    undComp: Optional[str] = None
    undSym: Optional[str] = None
    fullName: Optional[str] = None
    pageSize: Optional[int] = None
    model: Optional[str] = None

    def __init__(self, acctId: str = None, conid: int = None, contractDesc: str = None, assetClass: str = None,
                 position: int = None, mktPrice: int = None,
                 mktValue: int = None, currency: str = None, avgCost: int = None, avgPrice: int = None,
                 realizedPnl: int = None, unrealizedPnl: int = None,
                 exchs: str = None, expiry: str = None, putOrCall: str = None, multiplier: int = None,
                 strike: int = None, exerciseStyle: str = None,
                 undConid: int = None, conExchMap: List[Any] = None, baseMktValue: int = None, baseMktPrice: int = None,
                 baseAvgCost: int = None,
                 baseAvgPrice: int = None, baseRealizedPnl: int = None, baseUnrealizedPnl: int = None, name: str = None,
                 lastTradingDay: str = None,
                 group: str = None, sector: str = None, sectorGroup: str = None, ticker: str = None,
                 undComp: str = None, undSym: str = None, fullName: str = None,
                 pageSize: int = None, model: str = None) -> None:
        self.acctId = acctId
        self.conid = conid
        self.contractDesc = contractDesc
        self.assetClass = assetClass
        self.position = position
        self.mktPrice = mktPrice
        self.mktValue = mktValue
        self.currency = currency
        self.avgCost = avgCost
        self.avgPrice = avgPrice
        self.realizedPnl = realizedPnl
        self.unrealizedPnl = unrealizedPnl
        self.exchs = exchs
        self.expiry = expiry
        self.putOrCall = putOrCall
        self.multiplier = multiplier
        self.strike = strike
        self.exerciseStyle = exerciseStyle
        self.undConid = undConid
        self.conExchMap = conExchMap
        self.baseMktValue = baseMktValue
        self.baseMktPrice = baseMktPrice
        self.baseAvgCost = baseAvgCost
        self.baseAvgPrice = baseAvgPrice
        self.baseRealizedPnl = baseRealizedPnl
        self.baseUnrealizedPnl = baseUnrealizedPnl
        self.name = name
        self.lastTradingDay = lastTradingDay
        self.group = group
        self.sector = sector
        self.sectorGroup = sectorGroup
        self.ticker = ticker
        self.undComp = undComp
        self.undSym = undSym
        self.fullName = fullName
        self.pageSize = pageSize
        self.model = model


@dataclass
class PortfolioPositions(ResponseObject):
    portfolio_positions_list: Optional[List[PortfolioPosition]] = None
    endpoint: str = constants.ENDPOINT_PORTFOLIO_POSITIONS

    def __init__(self, data: List[Dict] = None, **kwargs: Any):
        if data is not None:
            self.portfolio_positions_list = []
            for portfolio_position in data:
                self.portfolio_positions_list.append(PortfolioPosition(**portfolio_position))

    @classmethod
    def call(cls, account_id: str) -> "PortfolioPositions":
        response: Response = http_requests.get(cls.endpoint.replace("{accountId}", account_id))
        return PortfolioPositions.create(response)

    @classmethod
    def create(cls, response: Response) -> "PortfolioPositions":
        if response.status_code == 200:
            portfolio_positions: PortfolioPositions = PortfolioPositions(response.json())
        else:
            portfolio_positions = PortfolioPositions()

        portfolio_positions.response = response
        portfolio_positions.is_successful = 200 <= portfolio_positions.response.status_code < 300

        portfolio_positions.endpoint = response.url
        return portfolio_positions


@dataclass
class StockSearchResults(ResponseObject):
    stock_search_results_list: Optional[List["StockSearchResult"]] = None
    endpoint: str = constants.ENDPOINT_STOCK_SEARCH

    def __init__(self, data: List[Dict] = None, **kwargs: Any):
        if data is not None:
            self.stock_search_results_list = []
            for stock_search_result in data:
                self.stock_search_results_list.append(StockSearchResult(**stock_search_result))

    @classmethod
    def call(cls, symbol: str) -> "StockSearchResults":
        response: Response = http_requests.post(cls.endpoint, {"symbol": symbol, "name": False})
        return StockSearchResults.create(response)

    @classmethod
    def create(cls, response: Response) -> "StockSearchResults":
        if response.status_code == 200:
            stock_search_result: StockSearchResults = StockSearchResults(response.json())
        else:
            stock_search_result = StockSearchResults()

        stock_search_result.response = response
        stock_search_result.is_successful = 200 <= stock_search_result.response.status_code < 300

        stock_search_result.endpoint = response.url
        return stock_search_result


class StockSearchResult(ResponseObject):
    conid: Optional[int] = None
    companyHeader: Optional[str] = None
    companyName: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    restricted: Optional[str] = None
    fop: Optional[str] = None
    opt: Optional[List[str]] = None
    war: Optional[List[str]] = None
    sections: Optional["Sections"] = None
    issuers: Optional[List["Issuer"]] = None

    def __init__(self, conid: int = None, companyHeader: str = None, companyName: str = None, symbol: str = None,
                 description: str = None, restricted: str = None, fop: str = None, opt: str = None, war: str = None,
                 sections: List[Dict[str, Any]] = None, issuers: List["Issuer"] = None, **kwargs: Any):
        self.conid = conid
        self.companyHeader = companyHeader
        self.companyName = companyName
        self.symbol = symbol
        self.description = description
        self.restricted = restricted
        self.fop = fop
        self.sections = Sections(sections)
        self.issuers = issuers
        if opt is not None:
            self.opt = opt.split(";")
        if war is not None:
            self.war = war.split(";")


@dataclass
class Section:
    exchange: Optional[List[str]] = None
    legSecType: Optional[str] = None
    conid: Optional[str] = None
    secType: Optional[str] = None
    months: Optional[List[str]] = None
    symbol: Optional[str] = None

    def __init__(self, secType: str = None, months: str = None, symbol: str = None, exchange: str = None, legSecType:
    str = None, conid: str = None, **kwargs: Any):
        self.secType = secType
        self.symbol = symbol
        self.legSecType = legSecType
        self.conid = conid
        if months is not None:
            self.months = months.split(";")
        if exchange is not None:
            self.exchange = exchange.split(";")


@dataclass
class Issuer:
    id: str
    name: str

    def __init__(self, id: Optional[str] = None, name: Optional[str] = None, **kwargs: Any):
        self.id = id
        self.name = name


@dataclass
class Sections:
    sections_list: Optional[List[Section]] = None

    def __init__(self, sections: List[Dict[str, Any]] = None, **kwargs: Any):
        self.sections_list = []
        for section in sections:
            self.sections_list.append(Section(**section))


@dataclass
class Contract(ResponseObject):
    cfi_code: Optional[str] = None
    symbol: Optional[str] = None
    cusip: Optional[str] = None
    expiry_full: Optional[str] = None
    con_id: Optional[int] = None
    maturity_date: Optional[str] = None
    industry: Optional[str] = None
    instrument_type: Optional[str] = None
    trading_class: Optional[str] = None
    valid_exchanges: Optional[List[str]] = None
    allow_sell_long: Optional[bool] = None
    is_zero_commission_security: Optional[bool] = None
    local_symbol: Optional[str] = None
    classifier: Optional[str] = None
    currency: Optional[str] = None
    text: Optional[str] = None
    underlying_con_id: Optional[int] = None
    r_t_h: Optional[bool] = None
    multiplier: Optional[str] = None
    underlying_issuer: Optional[str] = None
    contract_month: Optional[str] = None
    company_name: Optional[str] = None
    smart_available: Optional[bool] = None
    exchange: Optional[str] = None
    category: Optional[str] = None
    contract_clarification_type: Optional[str] = None
    endpoint: Optional[str] = constants.ENDPOINT_CONTRACT

    def __init__(self, cfi_code: str = None, symbol: str = None, cusip: str = None, expiry_full: str = None,
                 con_id: int = None, maturity_date: str = None, industry: str = None, instrument_type: str = None,
                 trading_class: str = None, valid_exchanges: str = None, allow_sell_long: bool = None,
                 is_zero_commission_security: bool = None, local_symbol: str = None, classifier: str = None,
                 currency: str = None, text: str = None, underlying_con_id: int = None, r_t_h: bool = None,
                 multiplier: str = None, underlying_issuer: str = None, contract_month: str = None, company_name: str
                 = None, smart_available: bool = None, exchange: str = None, category: str = None,
                 contract_clarification_type: str = None, **kwargs: Any):
        self.cfi_code = cfi_code
        self.symbol = symbol
        self.cusip = cusip
        self.expiry_full = expiry_full
        self.con_id = con_id
        self.maturity_date = maturity_date
        self.industry = industry
        self.instrument_type = instrument_type
        self.trading_class = trading_class
        self.allow_sell_long = allow_sell_long
        self.is_zero_commission_security = is_zero_commission_security
        self.local_symbol = local_symbol
        self.classifier = classifier
        self.currency = currency
        self.text = text
        self.underlying_con_id = underlying_con_id
        self.r_t_h = r_t_h
        self.multiplier = multiplier
        self.underlying_issuer = underlying_issuer
        self.contract_month = contract_month
        self.company_name = company_name
        self.smart_available = smart_available
        self.exchange = exchange
        self.category = category
        self.contract_clarification_type = contract_clarification_type

        if valid_exchanges is not None:
            self.valid_exchanges = valid_exchanges.split(" = None,")

    @classmethod
    def call(cls, contract_id: int) -> "Contract":
        response: Response = http_requests.get(cls.endpoint.replace("{contract_id}", str(contract_id)))
        return Contract.create(response)

    @classmethod
    def create(cls, response: Response) -> "Contract":
        if response.status_code == 200:
            contract: Contract = Contract(**response.json())
        else:
            contract = Contract()

        contract.response = response
        contract.is_successful = 200 <= contract.response.status_code < 300

        contract.endpoint = response.url
        return contract


@dataclass
class PastMarketData:
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal
    timestamp: datetime.datetime

    def __init__(self, o: float = None, c: float = None, h: float = None, l: float = None, v: int = None,
                 t: int = None, **kwargs: Any):
        self.open = Decimal(str(o))
        self.close = Decimal(str(c))
        self.high = Decimal(str(h))
        self.low = Decimal(str(l))
        self.volume = Decimal(str(v))
        self.timestamp = datetime.datetime.utcfromtimestamp(int(t / 1000))


@dataclass
class MarketDataHistory(ResponseObject):
    serverId: Optional[int] = None
    symbol: Optional[str] = None
    text: Optional[str] = None
    priceFactor: Optional[int] = None
    chartAnnotations: Optional[str] = None
    startTime: Optional[str] = None
    high: Optional[str] = None
    low: Optional[str] = None
    timePeriod: Optional[str] = None
    barLength: Optional[int] = None
    mdAvailability: Optional[str] = None
    mktDataDelay: Optional[int] = None
    outsideRth: Optional[bool] = None
    volumeFactor: Optional[int] = None
    priceDisplayRule: Optional[int] = None
    priceDisplayValue: Optional[int] = None
    negativeCapable: Optional[bool] = None
    messageVersion: Optional[int] = None
    points: Optional[int] = None
    travelTime: Optional[int] = None
    market_data_history: List[PastMarketData] = None
    endpoint: str = constants.ENDPOINT_MARKET_DATA_HISTORY

    def __init__(self, serverId: int = None, symbol: str = None, text: str = None, priceFactor: int = None,
                 chartAnnotations: str = None, startTime: str = None, high: str = None, low: str = None,
                 timePeriod: str = None, barLength: int = None, mdAvailability: str = None, mktDataDelay: int = None,
                 outsideRth: bool = None, volumeFactor: int = None, priceDisplayRule: int = None, priceDisplayValue:
            int = None, negativeCapable: bool = None, messageVersion: int = None, data: List[Dict[str, Any]] = None,
                 points: int = None, travelTime: int = None) -> None:
        self.serverId = serverId
        self.symbol = symbol
        self.text = text
        self.priceFactor = priceFactor
        self.chartAnnotations = chartAnnotations
        self.startTime = startTime
        self.high = high
        self.low = low
        self.timePeriod = timePeriod
        self.barLength = barLength
        self.mdAvailability = mdAvailability
        self.mktDataDelay = mktDataDelay
        self.outsideRth = outsideRth
        self.volumeFactor = volumeFactor
        self.priceDisplayRule = priceDisplayRule
        self.priceDisplayValue = priceDisplayValue
        self.negativeCapable = negativeCapable
        self.messageVersion = messageVersion
        self.points = points
        self.travelTime = travelTime

        if data is not None:
            self.market_data_history = []
            for one_data in data:
                self.market_data_history.append(PastMarketData(**one_data))

    @classmethod
    def call(cls, contract_id: int, period: str, bar: str) -> "MarketDataHistory":
        response: Response = http_requests.get(cls.endpoint.replace("{contract_id}",
                                                                    str(contract_id)).replace("{period}",
                                                                                              period).replace(
            "{bar}", bar))
        return MarketDataHistory.create(response)

    @classmethod
    def create(cls, response: Response) -> "MarketDataHistory":
        if response.status_code == 200:
            market_data_history: MarketDataHistory = MarketDataHistory(**response.json())
        else:
            market_data_history = MarketDataHistory()

        market_data_history.response = response
        market_data_history.is_successful = 200 <= market_data_history.response.status_code < 300
        market_data_history.endpoint = response.url
        return market_data_history


@dataclass
class MarketDataSnapshot(ResponseObject):
    last_price: Optional[str] = None
    symbol: Optional[str] = None
    text: Optional[str] = None
    current_day_high_price: Optional[str] = None
    current_day_low_price: Optional[str] = None
    position: Optional[str] = None
    market_value: Optional[str] = None
    average_price: Optional[str] = None
    unrealized_pnl: Optional[str] = None
    formatted_position: Optional[str] = None
    formatted_unrealized_pnl: Optional[str] = None
    daily_pnl: Optional[str] = None
    change_in_currency: Optional[str] = None
    change_in_percentage: Optional[str] = None
    bid_price: Optional[str] = None
    ask_size: Optional[str] = None
    ask_price: Optional[str] = None
    volume: Optional[str] = None
    bid_size: Optional[str] = None
    exchange_id: Optional[str] = None
    contract_id: Optional[int] = None
    instrument_type: Optional[str] = None
    months: Optional[str] = None
    regular_expiry: Optional[str] = None
    market_for_market_data_delivery: Optional[str] = None
    underlying_contract_id: Optional[int] = None
    market_data_availability: Optional[str] = None
    company_name: Optional[str] = None
    ask_exchange: Optional[str] = None
    last_exchange: Optional[str] = None
    last_size: Optional[str] = None
    bid_exchange: Optional[str] = None
    implied_volatility: Optional[str] = None
    put_call_interest: Optional[str] = None
    put_call_volume: Optional[str] = None
    historical_volatility: Optional[str] = None
    historical_volatility_close: Optional[str] = None
    option_volume: Optional[str] = None
    contract_id_and_exchange: Optional[str] = None
    contract_description: Optional[str] = None
    contract_description_2: Optional[str] = None
    listing_exchange: Optional[str] = None
    industry: Optional[str] = None
    category: Optional[str] = None
    average_volume: Optional[str] = None
    option_implied_volatility: Optional[str] = None
    historic_volume: Optional[str] = None
    put_call_ratio: Optional[str] = None
    dividend_amount: Optional[str] = None
    dividend_yield: Optional[str] = None
    ex_dividend_date: Optional[str] = None
    market_capitalization: Optional[str] = None
    price_to_earnings_ratio: Optional[str] = None
    earnings_per_share: Optional[str] = None
    cost_basis: Optional[str] = None
    fifty_two_week_high: Optional[str] = None
    fifty_two_week_low: Optional[str] = None
    open_price: Optional[str] = None
    close_price: Optional[str] = None
    delta: Optional[str] = None
    gamma: Optional[str] = None
    theta: Optional[str] = None
    vega: Optional[str] = None
    option_volume_change: Optional[str] = None
    implied_volatility_percentage: Optional[str] = None
    mark_price: Optional[str] = None
    shortable_shares_amount: Optional[str] = None
    interest_rate_on_borrowed_shares: Optional[str] = None
    option_open_interest: Optional[str] = None
    market_value_percentage: Optional[str] = None
    shortable_difficulty: Optional[str] = None
    morning_star_rating: Optional[str] = None
    expected_12_month_dividends: Optional[str] = None
    last_12_months_dividends: Optional[str] = None
    ema_200: Optional[str] = None
    ema_100: Optional[str] = None
    ema_50: Optional[str] = None
    ema_20: Optional[str] = None
    price_to_ema_200_ratio: Optional[str] = None
    price_to_ema_100_ratio: Optional[str] = None
    price_to_ema_50_ratio: Optional[str] = None
    price_to_ema_20_ratio: Optional[str] = None
    change_since_open: Optional[str] = None
    upcoming_event: Optional[str] = None
    upcoming_event_date: Optional[str] = None
    upcoming_analyst_meeting: Optional[str] = None
    upcoming_earnings: Optional[str] = None
    upcoming_misc_event: Optional[str] = None
    recent_analyst_meeting: Optional[str] = None
    recent_earnings: Optional[str] = None
    recent_misc_event: Optional[str] = None
    probability_of_max_return: Optional[str] = None
    break_even: Optional[str] = None
    spx_delta: Optional[str] = None
    futures_open_interest: Optional[str] = None
    last_yield: Optional[str] = None
    bid_yield: Optional[str] = None
    probability_of_max_return_2: Optional[str] = None
    probabilty_of_max_loss: Optional[str] = None
    profit_probability: Optional[str] = None
    organization_type: Optional[str] = None
    debt_class: Optional[str] = None
    ratings: Optional[str] = None
    bond_state_code: Optional[str] = None
    bond_type: Optional[str] = None
    last_trading_date: Optional[str] = None
    issue_date: Optional[str] = None
    beta_against_standard_index: Optional[str] = None
    ask_yield_of_bond: Optional[str] = None
    prior_close: Optional[str] = None
    server_id: Optional[str] = None
    conid: Optional[int] = None
    updated: Optional[datetime.datetime] = None
    conidEx: Optional[str] = None
    endpoint: str = constants.ENDPOINT_MARKET_DATA_SNAPSHOT

    def __init__(self, the31: str = None, the55: str = None, the58: str = None, the70: str = None, the71: str
    = None, the72: str = None, the73: str = None, the74: str = None, the75: str = None, the76: str = None,
                 the77: str = None, the78: str = None, the82: str = None, the83: str = None, the84: str = None,
                 the85: str = None, the86: str = None, the88: str = None, the6004: str = None,
                 the6008: int = None, the6070: str = None, the6072: str = None, the6073: str = None, the6119: str =
                 None, the6457: int = None, the6509: str = None, the7051: str = None, the7057: str = None,
                 the7058: str = None, the7059: str = None, the7068: str = None, the7084: str = None, the7085: str =
                 None, the7086: str = None, the7087: str = None, the7088: str = None, the7089: str = None,
                 the7094: str = None, the7219: str = None, the7220: str = None, the7221: str = None, the7280: str =
                 None, the7281: str = None, the7282: str = None, the7283: str = None, the7284: str = None,
                 the7285: str = None, the7286: str = None, the7287: str = None, the7288: str = None, the7289: str =
                 None, the7290: str = None, the7291: str = None, the7292: str = None, the7293: str = None,
                 the7294: str = None, the7295: str = None, the7296: str = None, the7308: str = None, the7309: str =
                 None, the7310: str = None, the7311: str = None, the7607: str = None, the7633: str = None,
                 the7635: str = None, the7636: str = None, the7637: str = None, the7638: str = None, the7639: str =
                 None, the7644: str = None, the7655: str = None, the7671: str = None, the7672: str = None,
                 the7674: str = None, the7675: str = None, the7676: str = None, the7677: str = None, the7678: str =
                 None, the7679: str = None, the7680: str = None, the7681: str = None, the7682: str = None,
                 the7683: str = None, the7684: str = None, the7685: str = None, the7686: str = None, the7687: str =
                 None, the7688: str = None, the7689: str = None, the7690: str = None, the7694: str = None,
                 the7695: str = None, the7696: str = None, the7697: str = None, the7698: str = None, the7699: str =
                 None, the7700: str = None, the7702: str = None, the7703: str = None, the7704: str = None,
                 the7705: str = None, the7706: str = None, the7707: str = None, the7708: str = None, the7714: str =
                 None, the7715: str = None, the7718: str = None, the7720: str = None, the7741: str = None,
                 the7762: str = None, server_id: str = None, conid: int = None, conidEx: str = None,
                 _updated: int = None, **kwargs: Any):

        if the55 is None:
            raise StockNotFoundException()
        self.updated = datetime.datetime.utcfromtimestamp(int(_updated / 1000))
        self.last_price = the31
        self.symbol = the55
        self.text = the58
        self.current_day_high_price = the70
        self.current_day_low_price = the71
        self.position = the72
        self.market_value = the73
        self.average_price = the74
        self.unrealized_pnl = the75
        self.formatted_position = the76
        self.formatted_unrealized_pnl = the77
        self.daily_pnl = the78
        self.change_in_currency = the82
        self.change_in_percentage = the83
        self.bid_price = the84
        self.ask_size = the85
        self.ask_price = the86
        self.volume = the7762
        self.bid_size = the88
        self.exchange_id = the6004
        self.contract_id = the6008
        self.instrument_type = the6070
        self.months = the6072
        self.regular_expiry = the6073
        self.market_for_market_data_delivery = the6119
        self.underlying_contract_id = the6457
        self.market_data_availability = the6509
        self.company_name = the7051
        self.ask_exchange = the7057
        self.last_exchange = the7058
        self.last_size = the7059
        self.bid_exchange = the7068
        self.implied_volatility = the7084
        self.put_call_interest = the7085
        self.put_call_volume = the7086
        self.historical_volatility = the7087
        self.historical_volatility_close = the7088
        self.option_volume = the7089
        self.contract_id_and_exchange = the7094
        self.contract_description = the7219
        self.contract_description_2 = the7220
        self.listing_exchange = the7221
        self.industry = the7280
        self.category = the7281
        self.average_volume = the7282
        self.option_implied_volatility = the7283
        self.historic_volume = the7284
        self.put_call_ratio = the7285
        self.dividend_amount = the7286
        self.dividend_yield = the7287
        self.ex_dividend_date = the7288
        self.market_capitalization = the7289
        self.price_to_earnings_ratio = the7290
        self.earnings_per_share = the7291
        self.cost_basis = the7292
        self.fifty_two_week_high = the7293
        self.fifty_two_week_low = the7294
        self.open_price = the7295
        self.close_price = the7296
        self.delta = the7308
        self.gamma = the7309
        self.theta = the7310
        self.vega = the7311
        self.option_volume_change = the7607
        self.implied_volatility_percentage = the7633
        self.mark_price = the7635
        self.shortable_shares_amount = the7636
        self.interest_rate_on_borrowed_shares = the7637
        self.option_open_interest = the7638
        self.market_value_percentage = the7639
        self.shortable_difficulty = the7644
        self.morning_star_rating = the7655
        self.expected_12_month_dividends = the7671
        self.last_12_months_dividends = the7672
        self.ema_200 = the7674
        self.ema_100 = the7675
        self.ema_50 = the7676
        self.ema_20 = the7677
        self.price_to_ema_200_ratio = the7678
        self.price_to_ema_100_ratio = the7679
        self.price_to_ema_50_ratio = the7680
        self.price_to_ema_20_ratio = the7681
        self.change_since_open = the7682
        self.upcoming_event = the7683
        self.upcoming_event_date = the7684
        self.upcoming_analyst_meeting = the7685
        self.upcoming_earnings = the7686
        self.upcoming_misc_event = the7687
        self.recent_analyst_meeting = the7688
        self.recent_earnings = the7689
        self.recent_misc_event = the7690
        self.probability_of_max_return = the7694
        self.break_even = the7695
        self.spx_delta = the7696
        self.futures_open_interest = the7697
        self.last_yield = the7698
        self.bid_yield = the7699
        self.probability_of_max_return_2 = the7700
        self.probabilty_of_max_loss = the7702
        self.profit_probability = the7703
        self.organization_type = the7704
        self.debt_class = the7705
        self.ratings = the7706
        self.bond_state_code = the7707
        self.bond_type = the7708
        self.last_trading_date = the7714
        self.issue_date = the7715
        self.beta_against_standard_index = the7718
        self.ask_yield_of_bond = the7720
        self.prior_close = the7741
        self.server_id = server_id
        self.conid = conid
        self.conidEx = conidEx

    @classmethod
    def call(cls, contract_id: int) -> "MarketDataSnapshot":
        endpoint: str = cls.endpoint.replace("{contract_id}", str(contract_id))

        # Endpoint needs to be called twice to work (for some reason)
        http_requests.get(endpoint)
        response: Response = http_requests.get(endpoint)
        return MarketDataSnapshot.create(response)

    @classmethod
    def create(cls, response: Response) -> "MarketDataSnapshot":
        if response.status_code == 200:
            data: List[Dict[str, Any]] = response.json()
            modified_data: Dict[str, Any] = {}

            for key in data[0].keys():
                modified_data_key: str = key
                if key.isnumeric():
                    modified_data_key = "the" + key

                modified_data[modified_data_key] = data[0][key]

            market_data_snapshot: MarketDataSnapshot = MarketDataSnapshot(**modified_data)
        else:
            market_data_snapshot = MarketDataSnapshot()

        market_data_snapshot.response = response
        market_data_snapshot.is_successful = 200 <= market_data_snapshot.response.status_code < 300
        market_data_snapshot.endpoint = response.url
        return market_data_snapshot


@dataclass
class ExistingTrade:
    executionid: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    orderdescription: Optional[str] = None
    tradetime: Optional[str] = None
    tradetimer: Optional[int] = None
    size: Optional[str] = None
    price: Optional[str] = None
    submitter: Optional[str] = None
    exchange: Optional[str] = None
    comission: Optional[int] = None
    netamount: Optional[int] = None
    account: Optional[str] = None
    companyname: Optional[str] = None
    contractdescription1: Optional[str] = None
    sectype: Optional[str] = None
    conidex: Optional[str] = None
    position: Optional[str] = None
    clearingid: Optional[str] = None
    clearingname: Optional[str] = None

    def __init__(self, executionid: str = None, symbol: str = None, side: str = None, orderdescription: str =
    None, tradetime: str = None, tradetimer: int = None, size: str = None, price: str = None, submitter: str = None,
                 exchange: str = None, comission: int = None, netamount: int = None, account: str = None,
                 companyname: str = None, contractdescription1: str = None, sectype: str = None, conidex: str = None,
                 position: str = None, clearingid: str = None, clearingname: str = None, **kwargs: Any):
        self.executionid = executionid
        self.symbol = symbol
        self.side = side
        self.orderdescription = orderdescription
        self.tradetime = tradetime
        self.tradetimer = tradetimer
        self.size = size
        self.price = price
        self.submitter = submitter
        self.exchange = exchange
        self.comission = comission
        self.netamount = netamount
        self.account = account
        self.companyname = companyname
        self.contractdescription1 = contractdescription1
        self.sectype = sectype
        self.conidex = conidex
        self.position = position
        self.clearingid = clearingid
        self.clearingname = clearingname


@dataclass
class ExistingTrades(ResponseObject):
    existing_trades_list: List[ExistingTrade] = None
    endpoint: str = constants.ENDPOINT_LIST_OF_TRADES

    def __init__(self, data: List[Dict] = None, **kwargs: Any):
        if data is not None:
            self.existing_trades_list = []
            for existing_trade in data:
                self.existing_trades_list.append(ExistingTrade(**existing_trade))

    @classmethod
    def call(cls) -> "ExistingTrades":
        response: Response = http_requests.get(cls.endpoint)
        return ExistingTrades.create(response)

    @classmethod
    def create(cls, response: Response) -> "ExistingTrades":
        if response.status_code == 200:
            existing_trades: ExistingTrades = ExistingTrades(response.json())
        else:
            existing_trades = ExistingTrades()

        existing_trades.response = response
        existing_trades.is_successful = 200 <= existing_trades.response.status_code < 300
        existing_trades.endpoint = response.url
        return existing_trades


@dataclass
class PlaceOrderResponse(ResponseObject):
    order_id: Optional[str] = None
    local_order_id: Optional[str] = None
    order_status: Optional[str] = None
    warning_message: Optional[str] = None
    text: Optional[str] = None

    def __init__(self, order_id: str = None, local_order_id: str = None, order_status: str = None, warning_message:
    str = None, text: str = None, **kwargs: Any):
        self.order_id = order_id
        self.local_order_id = local_order_id
        self.order_status = order_status
        self.warning_message = warning_message
        self.text = text


@dataclass
class PlaceOrder:
    conid: Optional[int] = None
    orderType: Optional[str] = None
    outsideRTH: Optional[bool] = None
    side: Optional[str] = None
    tif: Optional[str] = None
    quantity: Optional[int] = None
    cOID: Optional[str] = None
    price: Optional[float] = None
    acctId: Optional[str] = None
    endpoint: str = constants.ENDPOINT_CREATE_ORDER

    def __init__(self, acctId: str = None, conid: int = None, orderType: str = None, outsideRTH:
    bool = None, side: str = None, tif: str = None, quantity: int = None, cOID: str = None,
                 price: float = None, **kwargs: Any):
        self.acctId = acctId
        self.conid = conid
        self.orderType = orderType
        self.outsideRTH = outsideRTH
        self.side = side
        self.tif = tif
        self.quantity = quantity
        self.cOID = cOID
        if price is not None:
            self.price = price

    @classmethod
    def call(cls, account_id: str, conid: int, orderType: str, outsideRTH: bool, side: str, tif: str, quantity: int,
             cOID: str, price: Optional[float] = None) -> PlaceOrderResponse:
        request_parameters: Dict[str, List[Dict[str, Any]]] = {
            "orders": [{
                "acctId": account_id,
                "conid": conid,
                "orderType": orderType,
                "outsideRTH": outsideRTH,
                "price": price,
                "side": side,
                "quantity": quantity,
                "tif": tif,
                "cOID": cOID
            }]}

        response: Response = http_requests.post(cls.endpoint.replace("{account_id}", account_id),
                                                request_parameters)

        if response.text == '{"error":"invalid order attribute : Outside Regular Trading Hours"}':
            raise MarketOrderOutsideRTHException()
        elif response.status_code == 200:
            place_order_response: PlaceOrderResponse = PlaceOrderResponse(**response.json()[0])
        else:
            place_order_response = PlaceOrderResponse()

        place_order_response.text = response.text
        place_order_response.response = response
        place_order_response.is_successful = 200 <= place_order_response.response.status_code < 300
        place_order_response.endpoint = response.url

        return place_order_response


@dataclass
class CancelOrderResponse(ResponseObject):
    order_id: Optional[str] = None
    msg: Optional[str] = None
    conid: Optional[int] = None
    account: Optional[str] = None

    def __init__(self, order_id: str = None, msg: str = None, conid: int = None, account: str = None, **kwargs: Any):
        self.order_id = order_id
        self.msg = msg
        self.conid = conid
        self.account = account


@dataclass
class CancelOrder(ResponseObject):
    endpoint: str = constants.ENDPOINT_CANCEL_ORDER

    @classmethod
    def call(cls, account_id: str, order_id: str) -> CancelOrderResponse:
        response: Response = http_requests.delete(cls.endpoint.replace("{account_id}", account_id).replace("{order_id}", str(order_id)), None)
        cancel_order_response: CancelOrderResponse = CancelOrderResponse(**response.json())
        cancel_order_response.response = response
        cancel_order_response.is_successful = 200 <= cancel_order_response.response.status_code < 300
        cancel_order_response.endpoint = response.url

        return cancel_order_response


@dataclass
class LiveOrder:
    acct: Optional[str] = None
    exchange: Optional[str] = None
    conid: Optional[int] = None
    orderId: Optional[str] = None
    cashCcy: Optional[str] = None
    sizeAndFills: Optional[int] = None
    orderDesc: Optional[str] = None
    description1: Optional[str] = None
    ticker: Optional[str] = None
    secType: Optional[str] = None
    listingExchange: Optional[str] = None
    remainingQuantity: Optional[int] = None
    filledQuantity: Optional[int] = None
    companyName: Optional[str] = None
    status: Optional[str] = None
    origOrderType: Optional[str] = None
    supportsTaxOpt: Optional[int] = None
    lastExecutionTime: Optional[int] = None
    lastExecutionTimer: Optional[int] = None
    orderType: Optional[str] = None
    orderref: Optional[str] = None
    side: Optional[str] = None
    timeInForce: Optional[str] = None
    price: Optional[int] = None
    bgColor: Optional[str] = None
    fgColor: Optional[str] = None
    conidex: Optional[str] = None
    order_ref: Optional[str] = None
    lastExecutionTime_r: Optional[int] = None

    def __init__(self, acct: str = None, exchange: str = None, conid: int = None, orderId: str = None, cashCcy: str =
    None, sizeAndFills: int = None, orderDesc: str = None, description1: str = None, ticker: str = None, secType: str
                 = None, listingExchange: str = None, remainingQuantity: int = None, filledQuantity: int = None,
                 companyName: str
                 = None, status: str = None, origOrderType: str = None, supportsTaxOpt: int = None,
                 lastExecutionTime: int = None,
                 lastExecutionTimer: int = None, orderType: str = None, orderref: str = None, side: str = None,
                 timeInForce: str = None, price: int = None, bgColor: str = None, fgColor: str = None, conidex: str =
                 None, order_ref: str = None, lastExecutionTime_r: int = None, **kwargs: Any):
        self.acct = acct
        self.exchange = exchange
        self.conid = conid
        self.orderId = orderId
        self.cashCcy = cashCcy
        self.sizeAndFills = sizeAndFills
        self.orderDesc = orderDesc
        self.description1 = description1
        self.ticker = ticker
        self.secType = secType
        self.listingExchange = listingExchange
        self.remainingQuantity = remainingQuantity
        self.filledQuantity = filledQuantity
        self.companyName = companyName
        self.status = status
        self.origOrderType = origOrderType
        self.supportsTaxOpt = supportsTaxOpt
        self.lastExecutionTime = lastExecutionTime
        self.lastExecutionTimer = lastExecutionTimer
        self.orderType = orderType
        self.orderref = orderref
        self.side = side
        self.timeInForce = timeInForce
        self.price = price
        self.bgColor = bgColor
        self.fgColor = fgColor
        self.conidex = conidex
        self.order_ref = order_ref
        self.lastExecutionTime_r = lastExecutionTime_r


@dataclass
class LiveOrders(ResponseObject):
    live_orders_list: Optional[List[LiveOrder]] = None
    snapshot: bool = None
    endpoint: str = constants.ENDPOINT_LIVE_ORDERS

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any):
        if data is None:
            return

        self.live_orders_list = []
        for order in data["orders"]:
            self.live_orders_list.append(LiveOrder(**order))

    @classmethod
    def call(cls) -> "LiveOrders":
        response: Response = http_requests.get(cls.endpoint)
        return LiveOrders.create(response)

    @classmethod
    def create(cls, response: Response) -> "LiveOrders":
        if response.status_code == 200:
            live_orders: LiveOrders = LiveOrders(response.json())
        else:
            live_orders = LiveOrders()

        live_orders.response = response
        live_orders.is_successful = 200 <= live_orders.response.status_code < 300
        live_orders.endpoint = response.url
        return live_orders


@dataclass
class AccountInformation(ResponseObject):
    accountcode: Optional["AccountInformationDetail"] = None
    accountready: Optional["AccountInformationDetail"] = None
    accounttype: Optional["AccountInformationDetail"] = None
    accruedcash: Optional["AccountInformationDetail"] = None
    accruedcash_c: Optional["AccountInformationDetail"] = None
    accruedcash_s: Optional["AccountInformationDetail"] = None
    accrueddividend: Optional["AccountInformationDetail"] = None
    accrueddividend_c: Optional["AccountInformationDetail"] = None
    accrueddividend_s: Optional["AccountInformationDetail"] = None
    availablefunds: Optional["AccountInformationDetail"] = None
    availablefunds_c: Optional["AccountInformationDetail"] = None
    availablefunds_s: Optional["AccountInformationDetail"] = None
    billable: Optional["AccountInformationDetail"] = None
    billable_c: Optional["AccountInformationDetail"] = None
    billable_s: Optional["AccountInformationDetail"] = None
    buyingpower: Optional["AccountInformationDetail"] = None
    cushion: Optional["AccountInformationDetail"] = None
    daytradesremaining: Optional["AccountInformationDetail"] = None
    daytradesremainingt_plus1: Optional["AccountInformationDetail"] = None
    daytradesremainingt_plus2: Optional["AccountInformationDetail"] = None
    daytradesremainingt_plus3: Optional["AccountInformationDetail"] = None
    daytradesremainingt_plus4: Optional["AccountInformationDetail"] = None
    equitywithloanvalue: Optional["AccountInformationDetail"] = None
    equitywithloanvalue_c: Optional["AccountInformationDetail"] = None
    equitywithloanvalue_s: Optional["AccountInformationDetail"] = None
    excessliquidity: Optional["AccountInformationDetail"] = None
    excessliquidity_c: Optional["AccountInformationDetail"] = None
    excessliquidity_s: Optional["AccountInformationDetail"] = None
    fullavailablefunds: Optional["AccountInformationDetail"] = None
    fullavailablefunds_c: Optional["AccountInformationDetail"] = None
    fullavailablefunds_s: Optional["AccountInformationDetail"] = None
    fullexcessliquidity: Optional["AccountInformationDetail"] = None
    fullexcessliquidity_c: Optional["AccountInformationDetail"] = None
    fullexcessliquidity_s: Optional["AccountInformationDetail"] = None
    fullinitmarginreq: Optional["AccountInformationDetail"] = None
    fullinitmarginreq_c: Optional["AccountInformationDetail"] = None
    fullinitmarginreq_s: Optional["AccountInformationDetail"] = None
    fullmaintmarginreq: Optional["AccountInformationDetail"] = None
    fullmaintmarginreq_c: Optional["AccountInformationDetail"] = None
    fullmaintmarginreq_s: Optional["AccountInformationDetail"] = None
    grosspositionvalue: Optional["AccountInformationDetail"] = None
    grosspositionvalue_s: Optional["AccountInformationDetail"] = None
    guarantee: Optional["AccountInformationDetail"] = None
    guarantee_c: Optional["AccountInformationDetail"] = None
    guarantee_s: Optional["AccountInformationDetail"] = None
    highestseverity: Optional["AccountInformationDetail"] = None
    indianstockhaircut: Optional["AccountInformationDetail"] = None
    indianstockhaircut_c: Optional["AccountInformationDetail"] = None
    indianstockhaircut_s: Optional["AccountInformationDetail"] = None
    initmarginreq: Optional["AccountInformationDetail"] = None
    initmarginreq_c: Optional["AccountInformationDetail"] = None
    initmarginreq_s: Optional["AccountInformationDetail"] = None
    leverage_s: Optional["AccountInformationDetail"] = None
    lookaheadavailablefunds: Optional["AccountInformationDetail"] = None
    lookaheadavailablefunds_c: Optional["AccountInformationDetail"] = None
    lookaheadavailablefunds_s: Optional["AccountInformationDetail"] = None
    lookaheadexcessliquidity: Optional["AccountInformationDetail"] = None
    lookaheadexcessliquidity_c: Optional["AccountInformationDetail"] = None
    lookaheadexcessliquidity_s: Optional["AccountInformationDetail"] = None
    lookaheadinitmarginreq: Optional["AccountInformationDetail"] = None
    lookaheadinitmarginreq_c: Optional["AccountInformationDetail"] = None
    lookaheadinitmarginreq_s: Optional["AccountInformationDetail"] = None
    lookaheadmaintmarginreq: Optional["AccountInformationDetail"] = None
    lookaheadmaintmarginreq_c: Optional["AccountInformationDetail"] = None
    lookaheadmaintmarginreq_s: Optional["AccountInformationDetail"] = None
    lookaheadnextchange: Optional["AccountInformationDetail"] = None
    maintmarginreq: Optional["AccountInformationDetail"] = None
    maintmarginreq_c: Optional["AccountInformationDetail"] = None
    maintmarginreq_s: Optional["AccountInformationDetail"] = None
    netliquidation: Optional["AccountInformationDetail"] = None
    netliquidation_c: Optional["AccountInformationDetail"] = None
    netliquidation_s: Optional["AccountInformationDetail"] = None
    netliquidationuncertainty: Optional["AccountInformationDetail"] = None
    nlvandmargininreview: Optional["AccountInformationDetail"] = None
    pasharesvalue: Optional["AccountInformationDetail"] = None
    pasharesvalue_c: Optional["AccountInformationDetail"] = None
    pasharesvalue_s: Optional["AccountInformationDetail"] = None
    physicalcertificatevalue: Optional["AccountInformationDetail"] = None
    physicalcertificatevalue_c: Optional["AccountInformationDetail"] = None
    physicalcertificatevalue_s: Optional["AccountInformationDetail"] = None
    postexpirationexcess: Optional["AccountInformationDetail"] = None
    postexpirationexcess_c: Optional["AccountInformationDetail"] = None
    postexpirationexcess_s: Optional["AccountInformationDetail"] = None
    postexpirationmargin: Optional["AccountInformationDetail"] = None
    postexpirationmargin_c: Optional["AccountInformationDetail"] = None
    postexpirationmargin_s: Optional["AccountInformationDetail"] = None
    previousdayequitywithloanvalue: Optional["AccountInformationDetail"] = None
    previousdayequitywithloanvalue_s: Optional["AccountInformationDetail"] = None
    regtequity: Optional["AccountInformationDetail"] = None
    regtequity_s: Optional["AccountInformationDetail"] = None
    regtmargin: Optional["AccountInformationDetail"] = None
    regtmargin_s: Optional["AccountInformationDetail"] = None
    segmenttitle_c: Optional["AccountInformationDetail"] = None
    segmenttitle_s: Optional["AccountInformationDetail"] = None
    sma: Optional["AccountInformationDetail"] = None
    sma_s: Optional["AccountInformationDetail"] = None
    totalcashvalue: Optional["AccountInformationDetail"] = None
    totalcashvalue_c: Optional["AccountInformationDetail"] = None
    totalcashvalue_s: Optional["AccountInformationDetail"] = None
    totaldebitcardpendingcharges: Optional["AccountInformationDetail"] = None
    totaldebitcardpendingcharges_c: Optional["AccountInformationDetail"] = None
    totaldebitcardpendingcharges_s: Optional["AccountInformationDetail"] = None
    tradingtype_s: Optional["AccountInformationDetail"] = None
    whatifpmenabled: Optional["AccountInformationDetail"] = None

    endpoint: str = constants.ENDPOINT_ACCOUNT_INFORMATION

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.accountcode = AccountInformationDetail(**data.get("accountcode"))
        self.accountready = AccountInformationDetail(**data.get("accountready"))
        self.accounttype = AccountInformationDetail(**data.get("accounttype"))
        self.accruedcash = AccountInformationDetail(**data.get("accruedcash"))
        self.accruedcash_c = AccountInformationDetail(**data.get("accruedcash-c"))
        self.accruedcash_s = AccountInformationDetail(**data.get("accruedcash-s"))
        self.accrueddividend = AccountInformationDetail(**data.get("accrueddividend"))
        self.accrueddividend_c = AccountInformationDetail(**data.get("accrueddividend-c"))
        self.accrueddividend_s = AccountInformationDetail(**data.get("accrueddividend-s"))
        self.availablefunds = AccountInformationDetail(**data.get("availablefunds"))
        self.availablefunds_c = AccountInformationDetail(**data.get("availablefunds-c"))
        self.availablefunds_s = AccountInformationDetail(**data.get("availablefunds-s"))
        self.billable = AccountInformationDetail(**data.get("billable"))
        self.billable_c = AccountInformationDetail(**data.get("billable-c"))
        self.billable_s = AccountInformationDetail(**data.get("billable-s"))
        self.buyingpower = AccountInformationDetail(**data.get("buyingpower"))
        self.cushion = AccountInformationDetail(**data.get("cushion"))
        self.daytradesremaining = AccountInformationDetail(**data.get("daytradesremaining"))
        self.daytradesremainingt_plus1 = AccountInformationDetail(**data.get("daytradesremainingt+1"))
        self.daytradesremainingt_plus2 = AccountInformationDetail(**data.get("daytradesremainingt+2"))
        self.daytradesremainingt_plus3 = AccountInformationDetail(**data.get("daytradesremainingt+3"))
        self.daytradesremainingt_plus4 = AccountInformationDetail(**data.get("daytradesremainingt+4"))
        self.equitywithloanvalue = AccountInformationDetail(**data.get("equitywithloanvalue"))
        self.equitywithloanvalue_c = AccountInformationDetail(**data.get("equitywithloanvalue-c"))
        self.equitywithloanvalue_s = AccountInformationDetail(**data.get("equitywithloanvalue-s"))
        self.excessliquidity = AccountInformationDetail(**data.get("excessliquidity"))
        self.excessliquidity_c = AccountInformationDetail(**data.get("excessliquidity-c"))
        self.excessliquidity_s = AccountInformationDetail(**data.get("excessliquidity-s"))
        self.fullavailablefunds = AccountInformationDetail(**data.get("fullavailablefunds"))
        self.fullavailablefunds_c = AccountInformationDetail(**data.get("fullavailablefunds-c"))
        self.fullavailablefunds_s = AccountInformationDetail(**data.get("fullavailablefunds-s"))
        self.fullexcessliquidity = AccountInformationDetail(**data.get("fullexcessliquidity"))
        self.fullexcessliquidity_c = AccountInformationDetail(**data.get("fullexcessliquidity-c"))
        self.fullexcessliquidity_s = AccountInformationDetail(**data.get("fullexcessliquidity-s"))
        self.fullinitmarginreq = AccountInformationDetail(**data.get("fullinitmarginreq"))
        self.fullinitmarginreq_c = AccountInformationDetail(**data.get("fullinitmarginreq-c"))
        self.fullinitmarginreq_s = AccountInformationDetail(**data.get("fullinitmarginreq-s"))
        self.fullmaintmarginreq = AccountInformationDetail(**data.get("fullmaintmarginreq"))
        self.fullmaintmarginreq_c = AccountInformationDetail(**data.get("fullmaintmarginreq-c"))
        self.fullmaintmarginreq_s = AccountInformationDetail(**data.get("fullmaintmarginreq-s"))
        self.grosspositionvalue = AccountInformationDetail(**data.get("grosspositionvalue"))
        self.grosspositionvalue_s = AccountInformationDetail(**data.get("grosspositionvalue-s"))
        self.guarantee = AccountInformationDetail(**data.get("guarantee"))
        self.guarantee_c = AccountInformationDetail(**data.get("guarantee-c"))
        self.guarantee_s = AccountInformationDetail(**data.get("guarantee-s"))
        self.highestseverity = AccountInformationDetail(**data.get("highestseverity"))
        self.indianstockhaircut = AccountInformationDetail(**data.get("indianstockhaircut"))
        self.indianstockhaircut_c = AccountInformationDetail(**data.get("indianstockhaircut-c"))
        self.indianstockhaircut_s = AccountInformationDetail(**data.get("indianstockhaircut-s"))
        self.initmarginreq = AccountInformationDetail(**data.get("initmarginreq"))
        self.initmarginreq_c = AccountInformationDetail(**data.get("initmarginreq-c"))
        self.initmarginreq_s = AccountInformationDetail(**data.get("initmarginreq-s"))
        self.leverage_s = AccountInformationDetail(**data.get("leverage-s"))
        self.lookaheadavailablefunds = AccountInformationDetail(**data.get("lookaheadavailablefunds"))
        self.lookaheadavailablefunds_c = AccountInformationDetail(**data.get("lookaheadavailablefunds-c"))
        self.lookaheadavailablefunds_s = AccountInformationDetail(**data.get("lookaheadavailablefunds-s"))
        self.lookaheadexcessliquidity = AccountInformationDetail(**data.get("lookaheadexcessliquidity"))
        self.lookaheadexcessliquidity_c = AccountInformationDetail(**data.get("lookaheadexcessliquidity-c"))
        self.lookaheadexcessliquidity_s = AccountInformationDetail(**data.get("lookaheadexcessliquidity-s"))
        self.lookaheadinitmarginreq = AccountInformationDetail(**data.get("lookaheadinitmarginreq"))
        self.lookaheadinitmarginreq_c = AccountInformationDetail(**data.get("lookaheadinitmarginreq-c"))
        self.lookaheadinitmarginreq_s = AccountInformationDetail(**data.get("lookaheadinitmarginreq-s"))
        self.lookaheadmaintmarginreq = AccountInformationDetail(**data.get("lookaheadmaintmarginreq"))
        self.lookaheadmaintmarginreq_c = AccountInformationDetail(**data.get("lookaheadmaintmarginreq-c"))
        self.lookaheadmaintmarginreq_s = AccountInformationDetail(**data.get("lookaheadmaintmarginreq-s"))
        self.lookaheadnextchange = AccountInformationDetail(**data.get("lookaheadnextchange"))
        self.maintmarginreq = AccountInformationDetail(**data.get("maintmarginreq"))
        self.maintmarginreq_c = AccountInformationDetail(**data.get("maintmarginreq-c"))
        self.maintmarginreq_s = AccountInformationDetail(**data.get("maintmarginreq-s"))
        self.netliquidation = AccountInformationDetail(**data.get("netliquidation"))
        self.netliquidation_c = AccountInformationDetail(**data.get("netliquidation-c"))
        self.netliquidation_s = AccountInformationDetail(**data.get("netliquidation-s"))
        self.netliquidationuncertainty = AccountInformationDetail(**data.get("netliquidationuncertainty"))
        self.nlvandmargininreview = AccountInformationDetail(**data.get("nlvandmargininreview"))
        self.pasharesvalue = AccountInformationDetail(**data.get("pasharesvalue"))
        self.pasharesvalue_c = AccountInformationDetail(**data.get("pasharesvalue-c"))
        self.pasharesvalue_s = AccountInformationDetail(**data.get("pasharesvalue-s"))
        self.physicalcertificatevalue = AccountInformationDetail(**data.get("physicalcertificatevalue"))
        self.physicalcertificatevalue_c = AccountInformationDetail(**data.get("physicalcertificatevalue-c"))
        self.physicalcertificatevalue_s = AccountInformationDetail(**data.get("physicalcertificatevalue-s"))
        self.postexpirationexcess = AccountInformationDetail(**data.get("postexpirationexcess"))
        self.postexpirationexcess_c = AccountInformationDetail(**data.get("postexpirationexcess-c"))
        self.postexpirationexcess_s = AccountInformationDetail(**data.get("postexpirationexcess-s"))
        self.postexpirationmargin = AccountInformationDetail(**data.get("postexpirationmargin"))
        self.postexpirationmargin_c = AccountInformationDetail(**data.get("postexpirationmargin-c"))
        self.postexpirationmargin_s = AccountInformationDetail(**data.get("postexpirationmargin-s"))
        self.previousdayequitywithloanvalue = AccountInformationDetail(**data.get("previousdayequitywithloanvalue"))
        self.previousdayequitywithloanvalue_s = AccountInformationDetail(**data.get("previousdayequitywithloanvalue-s"))
        self.regtequity = AccountInformationDetail(**data.get("regtequity"))
        self.regtequity_s = AccountInformationDetail(**data.get("regtequity-s"))
        self.regtmargin = AccountInformationDetail(**data.get("regtmargin"))
        self.regtmargin_s = AccountInformationDetail(**data.get("regtmargin-s"))
        self.segmenttitle_c = AccountInformationDetail(**data.get("segmenttitle-c"))
        self.segmenttitle_s = AccountInformationDetail(**data.get("segmenttitle-s"))
        self.sma = AccountInformationDetail(**data.get("sma"))
        self.sma_s = AccountInformationDetail(**data.get("sma-s"))
        self.totalcashvalue = AccountInformationDetail(**data.get("totalcashvalue"))
        self.totalcashvalue_c = AccountInformationDetail(**data.get("totalcashvalue-c"))
        self.totalcashvalue_s = AccountInformationDetail(**data.get("totalcashvalue-s"))
        self.totaldebitcardpendingcharges = AccountInformationDetail(**data.get("totaldebitcardpendingcharges"))
        self.totaldebitcardpendingcharges_c = AccountInformationDetail(**data.get("totaldebitcardpendingcharges-c"))
        self.totaldebitcardpendingcharges_s = AccountInformationDetail(**data.get("totaldebitcardpendingcharges-s"))
        self.tradingtype_s = AccountInformationDetail(**data.get("tradingtype-s"))
        self.whatifpmenabled = AccountInformationDetail(**data.get("whatifpmenabled"))

    @classmethod
    def call(cls, account_id: str) -> "AccountInformation":
        response: Response = http_requests.get(cls.endpoint.replace("{account_id}", account_id))
        return AccountInformation.create(response)

    @classmethod
    def create(cls, response: Response) -> "AccountInformation":
        if response.status_code == 200:
            account_summary: AccountInformation = AccountInformation(response.json())
        else:
            account_summary = AccountInformation()

        account_summary.response = response
        account_summary.is_successful = 200 <= account_summary.response.status_code < 300
        account_summary.endpoint = response.url
        return account_summary


@dataclass
class AccountInformationDetail:
    amount: Optional[float] = None
    currency: Optional[str] = None
    isNull: Optional[bool] = None
    timestamp: Optional[int] = None
    value: Optional[str] = None
    severity: Optional[int] = None

    def __init__(self, amount: float = None, currency: str = None, isNull: bool = None, timestamp: int = None,
                 value: str = None, severity: int = None, **kwargs: Any):
        self.amount = amount
        self.currency = currency
        self.isNull = isNull
        self.timestamp = timestamp
        self.value = value
        self.severity = severity


@dataclass
class SelectAccount(ResponseObject):
    accounts: Optional[List[str]] = None
    aliases: Optional[Dict[str, str]] = None
    selectedAccount: Optional[str] = None
    endpoint: str = constants.ENDPOINT_SELECT_ACCOUNT

    def __init__(self, accounts: List[str], aliases: Dict[str, str], selectedAccount: str, **kwargs: Any):
        self.accounts = accounts
        self.aliases = aliases
        self.selectedAccount = selectedAccount

    @classmethod
    def execute(cls) -> "SelectAccount":
        response: Response = http_requests.get(cls.endpoint, None)
        select_account: SelectAccount = SelectAccount(**response.json())
        select_account.response = response
        select_account.is_successful = 200 <= select_account.response.status_code < 300
        select_account.endpoint = response.url

        return select_account


@dataclass
class PlaceOrderReply(ResponseObject):
    confirmed: Optional[bool] = None
    endpoint: str = constants.ENDPOINT_PLACE_ORDER_REPLY

    def __init__(self, confirmed: bool = None, **kwargs: Any):
        self.confirmed = confirmed

    @classmethod
    def execute(cls, reply_id: str, confirmed: bool) -> "PlaceOrderReply":
        response: Response = http_requests.post(cls.endpoint.replace("{reply_id}", reply_id), {"confirmed": confirmed})
        place_order_reply: PlaceOrderReply = PlaceOrderReply(**response.json()[0])
        place_order_reply.response = response
        place_order_reply.is_successful = 200 <= place_order_reply.response.status_code < 300
        place_order_reply.endpoint = response.url

        return place_order_reply
