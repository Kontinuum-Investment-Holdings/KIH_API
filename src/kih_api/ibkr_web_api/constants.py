KEEP_ALIVE_TIMEOUT_IN_SECONDS: int = 60
ENDPOINT_BASE: str = "https://localhost:5000/v1/api/"
ENDPOINT_KEEP_ALIVE: str = ENDPOINT_BASE + "tickle"
ENDPOINT_AUTHENTICATION_STATUS: str = ENDPOINT_BASE + "iserver/auth/status"
ENDPOINT_RE_AUTHENTICATE: str = ENDPOINT_BASE + "iserver/reauthenticate?force=true"
ENDPOINT_PORTFOLIO_ACCOUNTS: str = ENDPOINT_BASE + "portfolio/accounts"
ENDPOINT_PORTFOLIO_POSITIONS: str = ENDPOINT_BASE + "portfolio/{accountId}/positions/0"
ENDPOINT_STOCK_SEARCH: str = ENDPOINT_BASE + "iserver/secdef/search"
ENDPOINT_CONTRACT: str = ENDPOINT_BASE + "iserver/contract/{contract_id}/info"
ENDPOINT_MARKET_DATA_HISTORY: str = ENDPOINT_BASE + "iserver/marketdata/history?conid={contract_id}&period={" \
                                                    "period}&bar={bar}"
ENDPOINT_MARKET_DATA_SNAPSHOT: str = ENDPOINT_BASE + "/iserver/marketdata/snapshot?conids={contract_id}&fields=31," \
                                                     "55,58,70,71,72,73,74,75,76,77,78,82,83,84,85,86,87,88,6004,6008,6070,6072,6073,6119,6457,6509,7051,7057,7058,7059,7068,7084,7085,7086,7087,7088,7089,7094,7219,7220,7221,7280,7281,7282,7283,7284,7285,7286,7287,7288,7289,7290,7291,7292,7293,7294,7295,7296,7308,7309,7310,7311,7607,7633,7635,7636,7637,7638,7639,7644,7655,7671,7672,7674,7675,7676,7677,7678,7679,7680,7681,7682,7683,7684,7685,7686,7687,7688,7689,7690,7694,7695,7696,7697,7698,7699,7700,7702,7703,7704,7705,7706,7707,7708,7714,7715,7718,7720,7741,7762"
ENDPOINT_LIST_OF_TRADES: str = ENDPOINT_BASE + "portal/iserver/account/trades"
ENDPOINT_CREATE_ORDER: str = ENDPOINT_BASE + "iserver/account/{account_id}/orders"
ENDPOINT_CANCEL_ORDER: str = ENDPOINT_BASE + "iserver/account/{account_id}/order/{order_id}"
ENDPOINT_ACCOUNTS: str = ENDPOINT_BASE + "iserver/accounts"
ENDPOINT_LIVE_ORDERS: str = ENDPOINT_BASE + "iserver/account/orders"
ENDPOINT_ACCOUNT_INFORMATION: str = ENDPOINT_BASE + "portfolio/{account_id}/summary"
ENDPOINT_SELECT_ACCOUNT: str = ENDPOINT_BASE + "iserver/accounts"
ENDPOINT_PLACE_ORDER_REPLY: str = ENDPOINT_BASE + "iserver/reply/{reply_id}"
NUMBER_OF_RE_TRIES: int = 3
