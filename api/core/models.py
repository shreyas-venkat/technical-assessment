"""Data models for QByte GL records."""
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Account:
    """Represents a GL account."""
    code: str
    name: str
    account_type: str  # REVENUE, EXPENSE, etc.

    def is_revenue(self) -> bool:
        """Check if account is a revenue account."""
        return self.account_type == "REVENUE"

    def is_capex(self) -> bool:
        """Check if account is capital expenditure."""
        return self.code.startswith("6")


@dataclass
class GLRecord:
    """Represents a QByte-style GL entry."""
    gl_entry_id: int
    journal_batch: str
    journal_entry: str
    transaction_date: date
    posting_date: date
    account_code: str
    account_name: str
    account_type: str
    debit_amount: float
    credit_amount: float
    net_amount: float
    well_id: str
    lease_name: str
    property_id: str
    afe_number: str | None
    jib_number: str | None
    cost_center: str
    journal_source: str
    transaction_type: str
    description: str
    fiscal_period: str
    fiscal_year: int
    fiscal_month: int
    state: str
    county: str
    basin: str
    created_timestamp: datetime
    created_by: str
    last_modified: datetime

    def to_dict(self) -> dict:
        """Convert GL record to dictionary for JSON serialization."""
        return {
            "gl_entry_id": self.gl_entry_id,
            "journal_batch": self.journal_batch,
            "journal_entry": self.journal_entry,
            "transaction_date": self.transaction_date.isoformat(),
            "posting_date": self.posting_date.isoformat(),
            "account_code": self.account_code,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "debit_amount": self.debit_amount,
            "credit_amount": self.credit_amount,
            "net_amount": self.net_amount,
            "well_id": self.well_id,
            "lease_name": self.lease_name,
            "property_id": self.property_id,
            "afe_number": self.afe_number,
            "jib_number": self.jib_number,
            "cost_center": self.cost_center,
            "journal_source": self.journal_source,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "fiscal_period": self.fiscal_period,
            "fiscal_year": self.fiscal_year,
            "fiscal_month": self.fiscal_month,
            "state": self.state,
            "county": self.county,
            "basin": self.basin,
            "created_timestamp": self.created_timestamp.isoformat(),
            "created_by": self.created_by,
            "last_modified": self.last_modified.isoformat()
        }

