import os
from typing import Dict

API_KEY: str = os.getenv("TRANSFER_WISE_API_KEY")
HEADERS: Dict[str, str] = {"Authorization": f"Bearer {API_KEY}"}
ENDPOINT_BASE_SANDBOX: str = "https://api.sandbox.transferwise.tech/"
ENDPOINT_BASE_LIVE: str = "https://api.transferwise.com/"
ENDPOINT_BASE: str = ENDPOINT_BASE_SANDBOX
ENDPOINT_PROFILES: str = ENDPOINT_BASE + "v1/profiles"
ENDPOINT_ACCOUNTS: str = ENDPOINT_BASE + "v4/profiles/{profile_id}/balances?types={account_type}"
ENDPOINT_EXCHANGE_RATES: str = ENDPOINT_BASE + "v1/rates"
ENDPOINT_TRANSFER: str = ENDPOINT_BASE + "v1/transfers"
ENDPOINT_QUOTE: str = ENDPOINT_BASE + "v3/profiles/{profile_id}/quotes"
ENDPOINT_RECIPIENT_ACCOUNTS_LIST: str = ENDPOINT_BASE + "v1/accounts?profile={profile_id}"
ENDPOINT_FUND: str = ENDPOINT_BASE + "v3/profiles/{profile_id}/transfers/{transfer_id}/payments"
ENDPOINT_CREATE_ACCOUNT: str = ENDPOINT_BASE + "v3/profiles/{profile_id}/balances"
ENDPOINT_INTRA_ACCOUNT_TRANSFER: str = ENDPOINT_BASE + "v2/profiles/{profile_id}/balance-movements"
