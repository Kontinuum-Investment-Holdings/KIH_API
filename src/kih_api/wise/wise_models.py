import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

from requests import Response

from kih_api import global_common, http_requests
from kih_api.http_requests import common
from kih_api.http_requests.models import ResponseObject
from kih_api.wise import constants


@dataclass
class UserProfileDetails:
    occupations: None = None
    acn: None = None
    abn: None = None
    arbn: None = None
    webpage: None = None
    businessSubCategory: Optional[str] = None
    avatar: Optional[str] = None
    occupation: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    dateOfBirth: Optional[str] = None
    phoneNumber: Optional[str] = None
    primaryAddress: Optional[int] = None
    name: Optional[str] = None
    registrationNumber: Optional[str] = None
    companyType: Optional[str] = None
    companyRole: Optional[str] = None
    descriptionOfBusiness: Optional[str] = None
    businessCategory: Optional[str] = None
    firstNameInKana: Optional[str] = None
    lastNameInKana: Optional[str] = None


@dataclass
class UserProfiles(ResponseObject):
    id: Optional[int] = None
    type: Optional[str] = None
    details: Optional[UserProfileDetails] = None
    endpoint: str = constants.ENDPOINT_PROFILES

    @classmethod
    def call(cls) -> List["UserProfiles"]:
        response: Response = http_requests.get(cls.endpoint, headers=constants.HEADERS)
        return common.get_model_from_response(response, cls)  # type: ignore


@dataclass
class Amount:
    value: Optional[float] = None
    currency: Optional[str] = None


@dataclass
class BankAddress:
    stateCode: None = None
    postCode: Optional[int] = None
    addressFirstLine: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


@dataclass
class BankDetails:
    id: Optional[int] = None
    currency: Optional[str] = None
    bankCode: Optional[str] = None
    accountNumber: Optional[str] = None
    swift: Optional[str] = None
    iban: Optional[str] = None
    bankName: Optional[str] = None
    accountHolderName: Optional[str] = None
    bankAddress: Optional[BankAddress] = None


@dataclass
class Balance:
    name: Optional[str] = None
    icon: Optional[Dict] = None
    id: Optional[int] = None
    currency: Optional[str] = None
    amount: Optional[Amount] = None
    reservedAmount: Optional[Amount] = None
    cashAmount: Optional[Amount] = None
    totalWorth: Optional[Amount] = None
    type: Optional[str] = None
    investmentState: Optional[str] = None
    creationTime: Optional[str] = None
    modificationTime: Optional[str] = None
    visible: Optional[bool] = None
    primary: Optional[bool] = None

    def __init__(self, id: int, balanceType: str, currency: str, amount: Dict, reservedAmount: Dict[str, Any], bankDetails: Dict[str, Any]):
        self.id = id
        self.balanceType = balanceType
        self.currency = currency
        self.amount = Amount(**amount)
        self.reservedAmount = Amount(**reservedAmount)


@dataclass
class Account(ResponseObject):
    name: Optional[str] = None
    icon: Optional[Dict] = None
    id: Optional[int] = None
    currency: Optional[str] = None
    amount: Optional[Amount] = None
    reservedAmount: Optional[Amount] = None
    cashAmount: Optional[Amount] = None
    totalWorth: Optional[Amount] = None
    type: Optional[str] = None
    investmentState: Optional[str] = None
    creationTime: Optional[str] = None
    modificationTime: Optional[str] = None
    visible: Optional[bool] = None
    primary: Optional[bool] = None
    endpoint: str = constants.ENDPOINT_ACCOUNTS
    endpoint_create_account: str = constants.ENDPOINT_CREATE_ACCOUNT

    @classmethod
    def call(cls, profile_id: int) -> List["Account"]:
        from kih_api.wise.models import AccountType

        response: Response = http_requests.get(cls.endpoint.replace("{profile_id}", str(profile_id)).replace("{account_type}", AccountType.CashAccount.value), headers=constants.HEADERS)
        all_accounts_list: List[Account] = common.get_model_from_response(response, cls)  # type: ignore

        response = http_requests.get(cls.endpoint.replace("{profile_id}", str(profile_id)).replace("{account_type}", AccountType.ReserveAccount.value), headers=constants.HEADERS)
        all_accounts_list.extend(common.get_model_from_response(response, cls))  # type: ignore

        return all_accounts_list

    @classmethod
    def create_reserve_account(cls, name: str, currency: global_common.Currency, profile_id: int) -> None:
        from kih_api.wise.models import AccountType

        parameters: Dict[str, Any] = {
            "currency": currency.value,
            "type": AccountType.ReserveAccount.value,
            "name": name
        }

        headers = constants.HEADERS.copy()
        headers["X-idempotence-uuid"] = str(uuid.uuid4())
        http_requests.post(cls.endpoint_create_account.replace("{profile_id}", str(profile_id)), parameters=parameters, headers=headers)


@dataclass
class ExchangeRate(ResponseObject):
    rate: Optional[float] = None
    source: Optional[str] = None
    target: Optional[str] = None
    time: Optional[str] = None
    endpoint: str = constants.ENDPOINT_EXCHANGE_RATES

    @classmethod
    def call(cls, source_currency: str = None, target_currency: str = None) -> "ExchangeRate":

        if source_currency is not None and target_currency is not None:
            response: Response = http_requests.get(cls.endpoint + f"?source={source_currency}&target={target_currency}", headers=constants.HEADERS)
        else:
            response = http_requests.get(cls.endpoint, headers=constants.HEADERS)

        return common.get_model_from_response(response, cls)[0]  # type: ignore


@dataclass
class Transfer(ResponseObject):
    transferRequest: None = None
    sourceAccount: None = None
    quote: None = None
    quoteUuid: Optional[str] = None
    id: Optional[int] = None
    user: Optional[int] = None
    targetAccount: Optional[int] = None
    status: Optional[str] = None
    reference: Optional[str] = None
    rate: Optional[float] = None
    created: Optional[str] = None
    business: Optional[int] = None
    details: Optional["Details"] = None
    hasActiveIssues: Optional[bool] = None
    sourceCurrency: Optional[str] = None
    sourceValue: Optional[float] = None
    targetCurrency: Optional[str] = None
    targetValue: Optional[float] = None
    customerTransactionId: Optional[str] = None
    endpoint: str = constants.ENDPOINT_TRANSFER

    @classmethod
    def call(cls, target_account_id: int, quote_uuid: str, reference: str) -> "Transfer":
        parameters: Dict[str, Any] = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_uuid,
            "customerTransactionId": str(uuid.uuid4()),
            "details": {"reference": reference}
        }

        response: Response = http_requests.post(cls.endpoint, parameters=parameters, headers=constants.HEADERS)
        return common.get_model_from_response(response, cls)  # type: ignore


@dataclass
class DisabledReason:
    code: Optional[str] = None
    message: Optional[str] = None
    arguments: Optional[List[Any]] = None


@dataclass
class Fee:
    transferwise: Optional[float] = None
    payIn: Optional[float] = None
    discount: Optional[int] = None
    total: Optional[float] = None
    priceSetId: Optional[int] = None
    partner: Optional[float] = None


@dataclass
class PaymentOption:
    formattedEstimatedDelivery: Optional[str] = None
    estimatedDeliveryDelays: Optional[List[Any]] = None
    allowedProfileTypes: Optional[List[str]] = None
    feePercentage: Optional[float] = None
    estimatedDelivery: Optional[str] = None
    sourceAmount: Optional[float] = None
    targetAmount: Optional[float] = None
    sourceCurrency: Optional[str] = None
    targetCurrency: Optional[str] = None
    payOut: Optional[str] = None
    fee: Optional[Fee] = None
    payIn: Optional[str] = None
    disabled: Optional[bool] = None
    disabledReason: Optional[DisabledReason] = None


@dataclass
class HighAmount:
    showFeePercentage: Optional[bool] = None
    trackAsHighAmountSender: Optional[bool] = None
    showEducationStep: Optional[bool] = None
    offerPrefundingOption: Optional[bool] = None


@dataclass
class TransferFlowConfig:
    highAmount: Optional[HighAmount] = None


@dataclass
class Quote(ResponseObject):
    targetAmount: Optional[float] = None
    guaranteedTargetAmountAllowed: Optional[bool] = None
    targetAmountAllowed: Optional[bool] = None
    paymentOptions: Optional[List[PaymentOption]] = None
    notices: Optional[List[Any]] = None
    transferFlowConfig: Optional[TransferFlowConfig] = None
    rateTimestamp: Optional[str] = None
    clientId: Optional[str] = None
    id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    profile: Optional[int] = None
    sourceCurrency: Optional[str] = None
    targetCurrency: Optional[str] = None
    rate: Optional[float] = None
    createdTime: Optional[str] = None
    user: Optional[int] = None
    rateType: Optional[str] = None
    rateExpirationTime: Optional[str] = None
    payOut: Optional[str] = None
    guaranteedTargetAmount: Optional[bool] = None
    providedAmountType: Optional[str] = None
    expirationTime: Optional[str] = None
    targetAccount: Optional[int] = None
    payInCountry: Optional[str] = None
    payOutCountry: Optional[str] = None
    funding: Optional[str] = None
    endpoint: str = constants.ENDPOINT_QUOTE

    @classmethod
    def call(cls, profile_id: int, source_currency: str, target_currency: str, target_amount: float) -> "Quote":
        parameters: Dict[str, Any] = {
            "profile": profile_id,
            "sourceCurrency": source_currency,
            "targetCurrency": target_currency,
            "targetAmount": target_amount,
            "payOut": "BALANCE"
        }
        response: Response = http_requests.post(cls.endpoint.replace("{profile_id}", str(profile_id)), parameters=parameters, headers=constants.HEADERS)
        return common.get_model_from_response(response, cls)  # type: ignore


@dataclass
class Address:
    country: Optional[str] = None
    countryCode: Optional[str] = None
    firstLine: Optional[str] = None
    postCode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


@dataclass
class RecipientDetails:
    accountHolderName: Optional[str] = None
    sortCode: Optional[str] = None
    abartn: Optional[str] = None
    accountType: Optional[str] = None
    bankgiroNumber: Optional[str] = None
    ifscCode: Optional[str] = None
    bsbCode: Optional[str] = None
    institutionNumber: Optional[str] = None
    transitNumber: Optional[str] = None
    phoneNumber: Optional[str] = None
    bankCode: Optional[str] = None
    russiaRegion: Optional[str] = None
    routingNumber: Optional[str] = None
    branchCode: Optional[str] = None
    cpf: Optional[str] = None
    cardToken: Optional[str] = None
    idType: Optional[str] = None
    idNumber: Optional[str] = None
    idCountryIso3: Optional[str] = None
    idValidFrom: Optional[str] = None
    idValidTo: Optional[str] = None
    clabe: Optional[str] = None
    dateOfBirth: Optional[str] = None
    clearingNumber: Optional[str] = None
    bankName: Optional[str] = None
    branchName: Optional[str] = None
    businessNumber: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    rut: Optional[str] = None
    token: Optional[str] = None
    cnpj: Optional[str] = None
    payinReference: Optional[str] = None
    pspReference: Optional[str] = None
    orderId: Optional[str] = None
    idDocumentType: Optional[str] = None
    idDocumentNumber: Optional[str] = None
    targetProfile: Optional[str] = None
    targetUserId: Optional[str] = None
    taxId: Optional[str] = None
    job: Optional[str] = None
    nationality: Optional[str] = None
    interacAccount: Optional[str] = None
    bban: Optional[str] = None
    town: Optional[str] = None
    postCode: Optional[str] = None
    language: Optional[str] = None
    billerCode: Optional[str] = None
    customerReferenceNumber: Optional[str] = None
    IBAN: Optional[str] = None
    iban: Optional[str] = None
    address: Optional[Address] = None
    email: Optional[str] = None
    legalType: Optional[str] = None
    accountNumber: Optional[str] = None
    swiftCode: Optional[str] = None
    bic: Optional[str] = None
    BIC: Optional[str] = None
    prefix: Optional[str] = None


@dataclass
class Recipient(ResponseObject):
    business: None = None
    id: Optional[int] = None
    profile: Optional[int] = None
    accountHolderName: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    details: Optional[RecipientDetails] = None
    user: Optional[int] = None
    active: Optional[bool] = None
    ownedByCustomer: Optional[bool] = None
    endpoint: str = constants.ENDPOINT_RECIPIENT_ACCOUNTS_LIST

    @classmethod
    def call(cls, profile_id: int) -> List["Recipient"]:
        response: Response = http_requests.get(cls.endpoint.replace("{profile_id}", str(profile_id)), headers=constants.HEADERS)
        return common.get_model_from_response(response, cls)  # type: ignore


@dataclass
class Fund(ResponseObject):
    type: Optional[str] = None
    status: Optional[str] = None
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None
    balanceTransactionId: Optional[int] = None
    endpoint: str = constants.ENDPOINT_FUND

    @classmethod
    def call(cls, profile_id: int, transfer_id: int) -> "Fund":
        response: Response = http_requests.post(cls.endpoint.replace("{profile_id}", str(profile_id)).replace("{transfer_id}", str(transfer_id)), parameters={"type": "BALANCE"}, headers=constants.HEADERS)
        return common.get_model_from_response(response, cls)  # type: ignore


@dataclass
class SourceAmount:
    value: Optional[float] = None
    currency: Optional[str] = None


@dataclass
class BalancesAfter:
    id: Optional[int] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    cashAmount: Optional[SourceAmount] = None
    availableAmount: Optional[SourceAmount] = None
    totalWorth: Optional[SourceAmount] = None


@dataclass
class Step:
    tracingReferenceCode: None = None
    channelReferenceId: Optional[str] = None
    id: Optional[int] = None
    transactionId: Optional[int] = None
    type: Optional[str] = None
    creationTime: Optional[str] = None
    balancesAfter: Optional[List[SourceAmount]] = None
    channelName: Optional[str] = None
    sourceBalanceId: Optional[int] = None
    targetBalanceId: Optional[int] = None
    sourceAmount: Optional[SourceAmount] = None
    targetAmount: Optional[SourceAmount] = None
    fee: Optional[SourceAmount] = None
    rate: Optional[float] = None


@dataclass
class IntraAccountTransfer(ResponseObject):
    channelReferenceId: Optional[str] = None
    id: Optional[int] = None
    type: Optional[str] = None
    state: Optional[str] = None
    accountId: Optional[int] = None
    channelName: Optional[str] = None
    balancesAfter: Optional[List[BalancesAfter]] = None
    creationTime: Optional[str] = None
    steps: Optional[List[Step]] = None
    sourceAmount: Optional[SourceAmount] = None
    targetAmount: Optional[SourceAmount] = None
    rate: Optional[float] = None
    feeAmounts: Optional[List[SourceAmount]] = None
    endpoint: str = constants.ENDPOINT_INTRA_ACCOUNT_TRANSFER

    @classmethod
    def call(cls, profile_id: int, source_balance_id: int, target_balance_id: int, amount: float, quote_id: Optional[str], currency: str) -> "IntraAccountTransfer":
        parameters: Dict[str, Any] = {
            "profileId": profile_id,
            "sourceBalanceId": source_balance_id,
            "targetBalanceId": target_balance_id,
        }

        if quote_id is None:
            parameters["amount"] = {"value": amount, "currency": currency}
        else:
            parameters["quoteId"] = quote_id

        headers = constants.HEADERS.copy()
        headers["X-idempotence-uuid"] = str(uuid.uuid4())

        response: Response = http_requests.post(cls.endpoint.replace("{profile_id}", str(profile_id)), parameters=parameters, headers=headers)
        return common.get_model_from_response(response, cls)  # type: ignore


@dataclass
class AccountHolder:
    type: Optional[str] = None
    address: Optional[Address] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None


@dataclass
class EndOfStatementBalance:
    value: Optional[float] = None
    currency: Optional[str] = None
    zero: Optional[bool] = None


@dataclass
class Issuer:
    stateCode: None = None
    name: Optional[str] = None
    firstLine: Optional[str] = None
    city: Optional[str] = None
    postCode: Optional[str] = None
    countryCode: Optional[str] = None
    country: Optional[str] = None


@dataclass
class Query:
    intervalStart: Optional[str] = None
    intervalEnd: Optional[str] = None
    type: Optional[str] = None
    currency: Optional[str] = None
    profileId: Optional[int] = None
    timezone: Optional[str] = None


@dataclass
class Request:
    balanceName: None = None
    id: Optional[str] = None
    creationTime: Optional[str] = None
    profileId: Optional[int] = None
    currency: Optional[str] = None
    balanceId: Optional[int] = None
    intervalStart: Optional[str] = None
    intervalEnd: Optional[str] = None


@dataclass
class Details:
    type: Optional[str] = None
    description: Optional[str] = None
    sourceAmount: Optional[EndOfStatementBalance] = None
    targetAmount: Optional[EndOfStatementBalance] = None
    rate: Optional[float] = None
    recipient: Optional[Recipient] = None
    paymentReference: Optional[str] = None


@dataclass
class ExchangeDetails:
    toAmount: Optional[EndOfStatementBalance] = None
    fromAmount: Optional[EndOfStatementBalance] = None
    rate: Optional[float] = None


@dataclass
class Transaction:
    attachment: None = None
    type: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[EndOfStatementBalance] = None
    totalFees: Optional[EndOfStatementBalance] = None
    details: Optional[Details] = None
    exchangeDetails: Optional[ExchangeDetails] = None
    runningBalance: Optional[EndOfStatementBalance] = None
    referenceNumber: Optional[str] = None
    activityAssetAttributions: Optional[List[Any]] = None

@dataclass
class AccountStatement(ResponseObject):
    endOfStatementUnrealisedGainLoss: None = None
    balanceAssetConfiguration: None = None
    accountHolder: Optional[AccountHolder] = None
    issuer: Optional[Issuer] = None
    bankDetails: Optional[List[Any]] = None
    transactions: Optional[List[Transaction]] = None
    endOfStatementBalance: Optional[EndOfStatementBalance] = None
    query: Optional[Query] = None
    request: Optional[Request] = None
    endpoint: str = constants.ENDPOINT_ACCOUNT_STATEMENT

    @classmethod
    def call(cls, profile_id: int, balance_id: int, start_time: datetime, end_time: datetime) -> "AccountStatement":
        parameters: Dict[str, str] = {
            "intervalStart": f"{start_time.isoformat()}Z",
            "intervalEnd": f"{end_time.isoformat()}Z"
        }
        response: Response = http_requests.get(cls.endpoint.replace("{profile_id}", str(profile_id)).replace("{balance_id}", str(balance_id)), parameters=parameters, headers=constants.HEADERS)
        return common.get_model_from_response(response, cls)  # type: ignore