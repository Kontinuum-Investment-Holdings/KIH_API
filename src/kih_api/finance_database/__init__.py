from datetime import datetime

from kih_api.finance_database import common
from kih_api.finance_database.models import ExcelData, Transfers, FixedExpenses, MonthlyExpenseReport, Summary, Settings, Reserve


class FinanceDatabase:
    settings: Settings
    summary: Summary
    monthly_expenses_report: MonthlyExpenseReport
    fixed_expenses: FixedExpenses
    transfers: Transfers
    reserve: Reserve

    def __init__(self, excel_file_path: str, month: datetime = None):
        excel_data: ExcelData = ExcelData.read_excel(excel_file_path, common.get_next_month_text() if month is None else month.strftime("%B, %Y"))
        self.settings = Settings(excel_file_path)
        self.summary = Summary(excel_data)
        self.monthly_expenses_report = MonthlyExpenseReport(excel_data)
        self.fixed_expenses = FixedExpenses(excel_data)
        self.transfers = Transfers(excel_data, self.settings)
        self.reserve = Reserve(excel_data)
