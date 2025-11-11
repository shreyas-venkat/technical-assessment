"""Account management for QByte GL accounts."""
from .models import Account


class AccountRegistry:
    """Manages GL accounts by type."""

    def __init__(self):
        self._revenue_accounts = [
            Account("4100", "Crude Oil Sales Revenue", "REVENUE"),
            Account("4200", "Natural Gas Sales Revenue", "REVENUE"),
            Account("4300", "NGL Sales Revenue", "REVENUE"),
            Account("4400", "Condensate Sales Revenue", "REVENUE"),
            Account("4500", "Gathering & Processing Revenue", "REVENUE"),
        ]

        self._operating_expense_accounts = [
            Account("5100", "Lease Operating Expense", "EXPENSE"),
            Account("5200", "Workover Expense", "EXPENSE"),
            Account("5300", "Well Service Expense", "EXPENSE"),
            Account("5400", "Production Equipment Maintenance", "EXPENSE"),
            Account("5500", "Field Operations Expense", "EXPENSE"),
            Account("5600", "Gathering & Transportation", "EXPENSE"),
            Account("5700", "Processing & Treating", "EXPENSE"),
        ]

        self._capex_accounts = [
            Account("6100", "Drilling Costs", "EXPENSE"),
            Account("6200", "Completion Costs", "EXPENSE"),
            Account("6300", "Facilities & Equipment", "EXPENSE"),
            Account("6400", "Land & Lease Acquisition", "EXPENSE"),
            Account("6500", "Geological & Geophysical", "EXPENSE"),
        ]

        self._admin_accounts = [
            Account("7100", "General & Administrative", "EXPENSE"),
            Account("7200", "Overhead Allocation", "EXPENSE"),
            Account("7300", "Insurance Expense", "EXPENSE"),
            Account("7400", "Property Tax", "EXPENSE"),
        ]

    @property
    def revenue_accounts(self) -> list[Account]:
        """Get all revenue accounts."""
        return self._revenue_accounts

    @property
    def operating_expense_accounts(self) -> list[Account]:
        """Get all operating expense accounts."""
        return self._operating_expense_accounts

    @property
    def capex_accounts(self) -> list[Account]:
        """Get all capital expenditure accounts."""
        return self._capex_accounts

    @property
    def admin_accounts(self) -> list[Account]:
        """Get all administrative accounts."""
        return self._admin_accounts

    def get_all_accounts(self) -> list[Account]:
        """Get all accounts."""
        return (
            self._revenue_accounts +
            self._operating_expense_accounts +
            self._capex_accounts +
            self._admin_accounts
        )

    def get_account_types_info(self) -> dict:
        """Get account type information."""
        return {
            "4xxx": "Revenue Accounts",
            "5xxx": "Operating Expense Accounts",
            "6xxx": "Capital Expenditure Accounts",
            "7xxx": "Administrative Accounts"
        }

