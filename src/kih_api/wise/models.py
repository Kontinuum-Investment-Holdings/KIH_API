from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Union

from kih_api import global_common
from kih_api.finance_database.exceptions import InsufficientFundsException, AccountForCurrencyNotFoundException
from kih_api.http_requests import ClientErrorException
from kih_api.logger import logger
from kih_api.wise import wise_models
from kih_api.wise.exceptions import MultipleUserProfilesWithSameTypeException, MultipleRecipientsWithSameAccountNumberException, TransferringMoneyToNonSelfOwnedAccountsException, ReserveAccountNotFoundException


class ProfileTypes(enum.Enum):
    PERSONAL: str = "personal"
    BUSINESS: str = "business"


class AccountType(enum.Enum):
    CashAccount: str = "STANDARD"
    ReserveAccount: str = "SAVINGS"


@dataclass
class UserProfile:
    id: int
    type: ProfileTypes
    first_name: str
    last_name: str
    date_of_birth: str

    @classmethod
    def get_all(cls) -> List["UserProfile"]:
        user_profiles_list: List[UserProfile] = []

        for wise_user_profile in wise_models.UserProfiles.call():
            user_profiles_list.append(UserProfile(wise_user_profile.id, global_common.get_enum_from_value(wise_user_profile.type, ProfileTypes), wise_user_profile.details.firstName, wise_user_profile.details.lastName, wise_user_profile.details.dateOfBirth))

        return user_profiles_list

    @classmethod
    def get_by_profile_type(cls, profile_type: ProfileTypes) -> "UserProfile":
        return_user_profile: UserProfile = None

        for user_profile in UserProfile.get_all():
            if user_profile.type == profile_type:
                if return_user_profile is None:
                    return_user_profile = user_profile
                else:
                    raise MultipleUserProfilesWithSameTypeException()
        return return_user_profile


@dataclass
class Account:
    id: int
    currency: global_common.Currency
    balance: Decimal
    type: AccountType
    name: str
    profile_type: ProfileTypes

    def __init__(self, wise_account: wise_models.Account):
        self.id = wise_account.id
        self.currency = global_common.get_enum_from_value(wise_account.currency, global_common.Currency)
        self.balance = Decimal(str(wise_account.cashAmount.value))
        self.type = global_common.get_enum_from_value(wise_account.type, AccountType)
        self.profile_type = global_common.get_enum_from_value(wise_account.type, AccountType)

    @classmethod
    def get_all_by_profile_type(cls, profile_type: ProfileTypes) -> List["CashAccount" | "ReserveAccount"]:
        user_profile: UserProfile = UserProfile.get_by_profile_type(profile_type)
        accounts_list: List["CashAccount" | "ReserveAccount"] = []

        for wise_account in wise_models.Account.call(user_profile.id):
            account_type: AccountType = global_common.get_enum_from_value(wise_account.type, AccountType)
            if account_type == AccountType.CashAccount:
                accounts_list.append(CashAccount(wise_account))
            elif account_type == AccountType.ReserveAccount:
                accounts_list.append(ReserveAccount(wise_account))

        return accounts_list

    @classmethod
    def get_by_profile_type_and_currency(cls, profile_type: ProfileTypes, currency: global_common.Currency) -> "CashAccount" | "ReserveAccount":
        all_accounts_list: List["CashAccount" | "ReserveAccount"] = Account.get_all_by_profile_type(profile_type)
        for account in all_accounts_list:
            if account.currency == currency:
                return account
        raise AccountForCurrencyNotFoundException()


@dataclass
class ReserveAccount(Account):
    name: str

    def __init__(self, wise_account: wise_models.Account):
        super().__init__(wise_account)
        self.name = wise_account.name

    @classmethod
    def get_all_by_profile_type(cls, profile_type: ProfileTypes) -> List["ReserveAccount"]:  # type: ignore
        all_accounts: List["CashAccount" | "ReserveAccount"] = super().get_all_by_profile_type(profile_type)
        all_cash_accounts: List[ReserveAccount] = []

        for account in all_accounts:
            if isinstance(account, ReserveAccount):
                all_cash_accounts.append(account)
        return all_cash_accounts

    @classmethod
    def get_by_profile_type_and_currency(cls, profile_type: ProfileTypes, currency: global_common.Currency) -> List["ReserveAccount"]:  # type: ignore
        all_accounts_list: List[ReserveAccount] = ReserveAccount.get_all_by_profile_type(profile_type)
        reserve_account_list: List[ReserveAccount] = []
        for account in all_accounts_list:
            if account.currency == currency:
                reserve_account_list.append(account)
        return reserve_account_list

    @classmethod
    def get_reserve_account_by_profile_type_currency_and_name(cls, profile_type: ProfileTypes, currency: global_common.Currency, name: str, create_if_unavailable: bool = False) -> "ReserveAccount":
        all_reserve_accounts_list: List[ReserveAccount] = ReserveAccount.get_by_profile_type_and_currency(profile_type, currency)
        for reserve_account in all_reserve_accounts_list:
            if reserve_account.name == name:
                return reserve_account
        if create_if_unavailable:
            return ReserveAccount.create_reserve_account(name, currency, profile_type, False)
        else:
            raise ReserveAccountNotFoundException()

    @classmethod
    def create_reserve_account(cls, name: str, currency: global_common.Currency, profile_type: ProfileTypes, check_if_available_before_creation: bool = True) -> "ReserveAccount":
        if check_if_available_before_creation:
            try:
                return ReserveAccount.get_reserve_account_by_profile_type_currency_and_name(profile_type, currency, name)
            except ReserveAccountNotFoundException:
                pass

        wise_models.Account.create_reserve_account(name, currency, UserProfile.get_by_profile_type(profile_type).id)
        return ReserveAccount.get_reserve_account_by_profile_type_currency_and_name(profile_type, currency, name)


@dataclass
class CashAccount(Account):

    def __init__(self, wise_account: wise_models.Account):
        super().__init__(wise_account)

    @classmethod
    def get_all_by_profile_type(cls, profile_type: ProfileTypes) -> List["CashAccount"]:  # type: ignore
        all_accounts: List["CashAccount" | "ReserveAccount"] = super().get_all_by_profile_type(profile_type)
        all_cash_accounts: List[CashAccount] = []

        for account in all_accounts:
            if isinstance(account, CashAccount):
                all_cash_accounts.append(account)
        return all_cash_accounts

    @classmethod
    def get_by_profile_type_and_currency(cls, profile_type: ProfileTypes, currency: global_common.Currency) -> "CashAccount":
        all_accounts_list: List[CashAccount] = CashAccount.get_all_by_profile_type(profile_type)
        for account in all_accounts_list:
            if account.currency == currency:
                return account
        raise AccountForCurrencyNotFoundException()


@dataclass
class ExchangeRate:
    exchange_rate: Decimal
    from_currency: global_common.Currency
    to_currency: global_common.Currency

    @classmethod
    def get(cls, from_currency: global_common.Currency, to_currency: global_common.Currency) -> "ExchangeRate":
        wise_exchange_rate: wise_models.ExchangeRate = wise_models.ExchangeRate.call(from_currency.value, to_currency.value)
        return ExchangeRate(Decimal(str(wise_exchange_rate.rate)), from_currency, to_currency)


@dataclass
class Recipient:
    account_id: int
    profile_id: int
    name: str
    currency: global_common.Currency
    is_active: bool
    is_self_owned: bool
    account_number: str
    swift_code: str
    bank_name: str
    branch_name: str
    iban: str
    bic: str

    @classmethod
    def get_all_by_profile_type(cls, profile_type: ProfileTypes) -> List["Recipient"]:
        user_profile: UserProfile = UserProfile.get_by_profile_type(profile_type)
        recipient_list: List[Recipient] = []

        for wise_recipient in wise_models.Recipient.call(user_profile.id):
            recipient_list.append(Recipient(wise_recipient.id, wise_recipient.profile, wise_recipient.accountHolderName, global_common.get_enum_from_value(wise_recipient.currency, global_common.Currency), wise_recipient.active, wise_recipient.ownedByCustomer, wise_recipient.details.accountNumber, wise_recipient.details.swiftCode, wise_recipient.details.bankName, wise_recipient.details.branchName, wise_recipient.details.swiftCode, wise_recipient.details.bic))

        return recipient_list

    @classmethod
    def get_by_account_number_and_profile_type(cls, account_number: str, profile_type: ProfileTypes) -> "Recipient":
        return_recipient: Recipient = None
        for recipient in Recipient.get_all_by_profile_type(profile_type):
            if recipient.account_number == account_number:
                if return_recipient is None:
                    return_recipient = recipient
                else:
                    raise MultipleRecipientsWithSameAccountNumberException()

        return return_recipient


@dataclass
class Transfer:
    profile_id: int
    from_currency: global_common.Currency
    to_currency: global_common.Currency
    from_amount: Decimal
    to_amount: Decimal
    recipient: Recipient
    exchange_rate: ExchangeRate
    is_successful: bool
    error_message: Optional[str]
    error_code: Optional[str]

    def __init__(self, user_profile: UserProfile, recipient: Recipient, wise_transfer: wise_models.Transfer, wise_fund: wise_models.Fund):
        self.profile_id = user_profile.id
        self.from_currency = global_common.get_enum_from_value(wise_transfer.sourceCurrency, global_common.Currency)
        self.to_currency = global_common.get_enum_from_value(wise_transfer.targetCurrency, global_common.Currency)
        self.from_amount = Decimal(str(wise_transfer.sourceValue))
        self.to_amount = Decimal(str(wise_transfer.targetValue))
        self.recipient = recipient
        self.exchange_rate = ExchangeRate(Decimal(str(wise_transfer.rate)), self.from_currency, self.to_currency)
        self.is_successful = wise_fund.status == "COMPLETED"
        self.error_message = wise_fund.errorMessage
        self.error_code = wise_fund.errorCode

    @classmethod
    def execute(cls, receiving_amount: Decimal, from_currency: global_common.Currency, to_currency: global_common.Currency, recipient_account_number: str, reference: str, profile_type: ProfileTypes) -> "Transfer":
        recipient: Recipient = Recipient.get_by_account_number_and_profile_type(recipient_account_number, profile_type)

        if not recipient.is_self_owned:
            raise TransferringMoneyToNonSelfOwnedAccountsException()

        try:
            if from_currency == to_currency:
                cash_account: CashAccount = CashAccount.get_by_profile_type_and_currency(profile_type, from_currency)
                if cash_account.balance < receiving_amount:
                    raise InsufficientFundsException(f"Insufficient funds"
                                                     f"\nRequired amount: {from_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}"
                                                     f"\nAccount Balance: {from_currency.value} {global_common.get_formatted_string_from_decimal(cash_account.balance)}"
                                                     f"\nShort of: {from_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount - cash_account.balance)}")

            user_profile: UserProfile = UserProfile.get_by_profile_type(profile_type)
            wise_quote: wise_models.Quote = wise_models.Quote.call(user_profile.id, from_currency.value, to_currency.value, float(receiving_amount))
            wise_transfer: wise_models.Transfer = wise_models.Transfer.call(recipient.account_id, wise_quote.id, reference)
            wise_fund: wise_models.Fund = wise_models.Fund.call(user_profile.id, wise_transfer.id)
            transfer: Transfer = Transfer(user_profile, recipient, wise_transfer, wise_fund)

            if transfer.is_successful:
                communication.telegram.send_message(kih_api.communication.telegram.constants.telegram_channel_username,
                                                    f"<u><b>Money transferred</b></u>"
                                                    f"\n\nAmount: <i>{to_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}</i>"
                                                    f"\nTo: <i>{recipient.name}</i>"
                                                    f"\nReference: <i>{reference}</i>", True)
            else:
                raise ClientErrorException(transfer.error_message)

            return transfer

        except ClientErrorException as e:
            logger.error(str(e))
            communication.telegram.send_message(kih_api.communication.telegram.constants.telegram_channel_username,
                                                f"<u><b>ERROR: Money transfer failed</b></u>"
                                                f"\n\nAmount: <i>{to_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}</i>"
                                                f"\nTo: <i>{recipient.name}</i>"
                                                f"\nReason: <i>{str(e)}</i>"
                                                f"\nReference: <i>{reference}</i>", True)
        except InsufficientFundsException as e:
            logger.error(str(e))
            communication.telegram.send_message(kih_api.communication.telegram.constants.telegram_channel_username,
                                                f"<u><b>ERROR: Money transfer failed</b></u>"
                                                f"\n\nAmount: <i>{to_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}</i>"
                                                f"\nTo: <i>{recipient.name}</i>"
                                                f"\nReference: <i>{reference}</i>"
                                                f"\n\nReason: <i>{str(e)}</i>", True)
            raise InsufficientFundsException(str(e))

        return None


@dataclass
class IntraAccountTransfer:
    from_currency: global_common.Currency
    from_amount: Decimal
    from_account: Account
    to_currency: global_common.Currency
    to_amount: Decimal
    to_account: Account
    exchange_rate: ExchangeRate
    is_successful: bool

    def __init__(self, from_account: Account, to_account: Account, intra_account_transfer: wise_models.IntraAccountTransfer):
        self.from_currency = global_common.get_enum_from_value(intra_account_transfer.sourceAmount.currency, global_common.Currency)
        self.from_amount = Decimal(str(intra_account_transfer.sourceAmount.value))
        self.from_account = from_account
        self.to_account = to_account
        self.to_currency = global_common.get_enum_from_value(intra_account_transfer.targetAmount.currency, global_common.Currency)
        self.to_amount = Decimal(str(intra_account_transfer.targetAmount.value))
        self.exchange_rate = ExchangeRate(Decimal(str(intra_account_transfer.rate)), self.from_currency, self.to_currency)
        self.is_successful = intra_account_transfer.state == "COMPLETED"

    # TODO: Implement withdrawal from reserve accounts
    @classmethod
    def execute(cls, receiving_amount: Decimal, from_currency: global_common.Currency, to_account: Union[CashAccount, ReserveAccount], profile_type: ProfileTypes) -> "IntraAccountTransfer":
        user_profile: UserProfile = UserProfile.get_by_profile_type(profile_type)
        from_account: CashAccount = CashAccount.get_by_profile_type_and_currency(profile_type, from_currency)
        intra_account_transfer: IntraAccountTransfer = None
        wise_intra_account_transfer: wise_models.IntraAccountTransfer = None

        try:
            if isinstance(to_account, CashAccount):
                wise_quote: wise_models.Quote = wise_models.Quote.call(user_profile.id, from_currency.value, to_account.currency.value, float(receiving_amount))
                wise_intra_account_transfer = wise_models.IntraAccountTransfer.call(user_profile.id, from_account.id, to_account.id, float(receiving_amount), wise_quote.id, None)
                intra_account_transfer = IntraAccountTransfer(from_account, to_account, wise_intra_account_transfer)

            elif isinstance(to_account, ReserveAccount):
                if from_currency != to_account.currency:
                    to_cash_account: CashAccount = CashAccount.get_by_profile_type_and_currency(profile_type, to_account.currency)
                    IntraAccountTransfer.execute(receiving_amount, from_currency, to_cash_account, profile_type)
                    from_account = to_cash_account

                if from_account.balance < receiving_amount:
                    raise InsufficientFundsException(f"Insufficient funds"
                                                     f"\nRequired amount: {from_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}"
                                                     f"\nAccount Balance: {from_currency.value} {global_common.get_formatted_string_from_decimal(from_account.balance)}"
                                                     f"\nShort of: {from_currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount - from_account.balance)}")

                wise_intra_account_transfer = wise_models.IntraAccountTransfer.call(user_profile.id, from_account.id, to_account.id, float(receiving_amount), None, to_account.currency.value)
                intra_account_transfer = IntraAccountTransfer(from_account, to_account, wise_intra_account_transfer)

                if intra_account_transfer.is_successful:
                    communication.telegram.send_message(
                        kih_api.communication.telegram.constants.telegram_channel_username,
                                                        f"<u><b>Intra account money transferred</b></u>"
                                                        f"\n\nAmount: <i>{to_account.currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}</i>"
                                                        f"\nFrom: <i>{to_account.currency.value}</i>"
                                                        f"\nTo: <i>{to_account.name if isinstance(to_account, ReserveAccount) else ''} ({to_account.currency.value})</i>", True)
            return intra_account_transfer

        except ClientErrorException as e:
            logger.error(str(e))
            communication.telegram.send_message(kih_api.communication.telegram.constants.telegram_channel_username,
                                                f"<u><b>ERROR: Intra account money transfer failed</b></u>"
                                                f"\n\nAmount: <i>{to_account.currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}</i>"
                                                f"\nFrom: <i>{to_account.currency.value}</i>"
                                                f"\nTo: <i>{to_account.name if isinstance(to_account, ReserveAccount) else None} ({to_account.currency.value})</i>"
                                                f"\nReason: <i>{str(e)}</i>", True)
        except InsufficientFundsException as e:
            logger.error(str(e))
            communication.telegram.send_message(kih_api.communication.telegram.constants.telegram_channel_username,
                                                f"<u><b>ERROR: Intra account money transfer failed</b></u>"
                                                f"\n\nAmount: <i>{to_account.currency.value} {global_common.get_formatted_string_from_decimal(receiving_amount)}</i>"
                                                f"\nFrom: <i>{to_account.currency.value}</i>"
                                                f"\nTo: <i>{to_account.name if isinstance(to_account, ReserveAccount) else to_account.currency.value} ({to_account.currency.value})</i>"
                                                f"\nReason: <i>{str(e)}</i>", True)
            raise InsufficientFundsException(str(e))

        return None
