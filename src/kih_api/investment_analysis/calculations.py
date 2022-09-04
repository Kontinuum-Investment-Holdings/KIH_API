import datetime
from decimal import Decimal


def get_annual_rate_of_return(starting_value: Decimal, ending_value: Decimal, number_of_years: Decimal) -> Decimal:
    a: Decimal = ending_value ** (1 / number_of_years)
    b: Decimal = (1 / starting_value) ** (1 / number_of_years)
    return (a * b) - Decimal("1")


def get_year_frac(starting_date: datetime.datetime, ending_date: datetime.datetime) -> Decimal:
    number_of_whole_years: Decimal = Decimal(ending_date.year - starting_date.year)

    new_starting_date: datetime.datetime
    try:
        new_starting_date = datetime.datetime(starting_date.year + int(number_of_whole_years), starting_date.month, starting_date.day)
    except ValueError as e:
        if starting_date.month == 2 and starting_date.day == 29:
            new_starting_date = datetime.datetime(int(starting_date.year + number_of_whole_years), 3, 1)
        else:
            raise e

    difference_in_days: Decimal = Decimal((ending_date - new_starting_date).days)
    return number_of_whole_years + get_year_frac_from_number_of_days(difference_in_days, ending_date.year)


def get_number_of_days_from_year_frac(number_of_fractional_years: Decimal, year: int) -> Decimal:
    day_count_basis: Decimal = Decimal("365") if year % 4 != 0 else Decimal("366")
    return Decimal(int((number_of_fractional_years * day_count_basis)))


def get_year_frac_from_number_of_days(number_of_days: Decimal, year: int) -> Decimal:
    day_count_basis: Decimal = Decimal("365") if year % 4 != 0 else Decimal("366")
    return number_of_days / day_count_basis


def add_years_to_date(date: datetime.datetime, number_of_years: Decimal) -> datetime:
    number_of_whole_years: Decimal = Decimal(int(number_of_years))
    number_of_fractional_years: Decimal = number_of_years - number_of_whole_years

    future_date: datetime.datetime
    try:
        future_date = date.replace(year=int(date.year + number_of_whole_years))
    except ValueError as e:
        if date.month == 2 and date.day == 29:
            future_date = datetime.datetime(int(date.year + number_of_whole_years), 3, 1)
        else:
            raise e

    return future_date + datetime.timedelta(days=float(get_number_of_days_from_year_frac(number_of_fractional_years, future_date.year)))
