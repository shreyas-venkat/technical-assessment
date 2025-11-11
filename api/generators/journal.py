"""Journal-related data generators."""
import random


class JournalGenerator:
    """Generates journal-related identifiers."""

    JOURNAL_SOURCES = ["AP", "AR", "JIB", "PA", "PROD", "MANUAL", "ADJ"]
    TRANSACTION_TYPES = ["INV", "PAY", "ADJ", "ALLOC", "ACCR", "REV"]

    def generate_journal_source(self) -> str:
        """Generate journal source (where transaction originated)."""
        return random.choice(self.JOURNAL_SOURCES)

    def generate_transaction_type(self) -> str:
        """Generate transaction type."""
        return random.choice(self.TRANSACTION_TYPES)

