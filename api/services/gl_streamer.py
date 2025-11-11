"""GL data streaming service."""
import asyncio
import json
import random
from collections.abc import AsyncGenerator
from datetime import date, datetime, timedelta

from core.accounts import AccountRegistry
from core.models import Account, GLRecord
from generators import AmountGenerator, DateGenerator, JournalGenerator, OilGasDataGenerator


class GLDataStreamer:
    """Handles streaming of GL data records."""

    # Fixed start date for deterministic data generation
    FIXED_START_DATE = date(2025, 11, 10)
    FIXED_START_DATETIME = datetime(2025, 11, 10, 0, 0, 0)

    def __init__(self, historical_days: int = 365):
        """
        Initialize GL data streamer.

        Args:
            historical_days: Number of days back from FIXED_START_DATE to generate historical records (default 365)
        """
        self.account_registry = AccountRegistry()
        self.oil_gas_generator = OilGasDataGenerator()
        self.journal_generator = JournalGenerator()
        self.amount_generator = AmountGenerator()
        self.date_generator = DateGenerator()
        self._counter = 0
        self._journal_batch = 1
        self._historical_batch: list[GLRecord] = []
        # Create a seeded RNG instance for ALL data (deterministic)
        self._deterministic_rng = random.Random(42)
        # One record per day
        self._historical_days = historical_days
        # Track current records generated (new records after historical batch)
        self._current_records_count = 0
        # Track total records streamed (including historical)
        self._total_streamed_count = 0
        # Buffer to store generated records for clients to consume
        self._record_buffer: list[GLRecord] = []
        self._buffer_lock = asyncio.Lock()
        self._initialize_historical_batch()
        # Pre-load all historical records into buffer immediately
        self._preload_historical_records()

    def _initialize_historical_batch(self):
        """Generate historical records going back historical_days from FIXED_START_DATE."""
        # Save current counter state

        # Calculate start date: go back historical_days from FIXED_START_DATE
        start_date = self.FIXED_START_DATE - timedelta(days=self._historical_days)
        datetime.combine(start_date, datetime.min.time())

        # Temporarily replace generators' random with our seeded RNG
        original_random = random.random
        original_choice = random.choice
        original_uniform = random.uniform
        original_randint = random.randint

        # Monkey-patch random functions to use our seeded RNG
        random.random = self._deterministic_rng.random
        random.choice = self._deterministic_rng.choice
        random.uniform = self._deterministic_rng.uniform
        random.randint = self._deterministic_rng.randint

        try:
            current_date = start_date
            # Generate one record per day for historical_days
            for _i in range(self._historical_days):
                current_datetime = datetime.combine(current_date, datetime.min.time())
                gl_record = self._generate_gl_record(
                    transaction_date=current_date,
                    transaction_datetime=current_datetime
                )
                self._historical_batch.append(gl_record)
                current_date += timedelta(days=1)
        finally:
            # Restore original random functions
            random.random = original_random
            random.choice = original_choice
            random.uniform = original_uniform
            random.randint = original_randint

        # Don't reset counter state - let it continue for unique IDs
        # The counter should continue from where historical batch generation left off
        # to ensure all gl_entry_id values are unique across historical and real-time records

    def _preload_historical_records(self):
        """Pre-load all historical records into buffer immediately."""
        # Add all historical records to buffer
        self._record_buffer.extend(self._historical_batch)
        # Set counter to reflect historical records
        self._total_streamed_count = len(self._historical_batch)

    def get_current_records_count(self) -> int:
        """Get the current number of records generated."""
        return self._current_records_count

    def get_total_streamed_count(self) -> int:
        """Get the total number of records streamed including historical."""
        return self._total_streamed_count


    def _select_account(self) -> tuple[Account, bool]:
        """
        Select an account based on transaction type probability.

        Returns:
            Tuple of (account, is_revenue)
        """
        account_type_roll = random.random()
        if account_type_roll < 0.3:  # 30% revenue
            account = random.choice(self.account_registry.revenue_accounts)
            return (account, True)
        elif account_type_roll < 0.7:  # 40% operating expense
            account = random.choice(self.account_registry.operating_expense_accounts)
            return (account, False)
        elif account_type_roll < 0.9:  # 20% capex
            account = random.choice(self.account_registry.capex_accounts)
            return (account, False)
        else:  # 10% admin
            account = random.choice(self.account_registry.admin_accounts)
            return (account, False)

    def _generate_gl_record(self, transaction_date: datetime.date = None, transaction_datetime: datetime = None) -> GLRecord:
        """
        Generate a single GL record.

        Args:
            transaction_date: Specific transaction date (if None, uses date generator)
            transaction_datetime: Specific transaction datetime for created_timestamp
        """
        account, is_revenue = self._select_account()

        # Generate dates first (needed for JIB number)
        if transaction_date is None:
            transaction_date = self.date_generator.generate_transaction_date()

        # Generate oil & gas specific data
        well_id = self.oil_gas_generator.generate_well_id()
        afe_number = self.oil_gas_generator.generate_afe_number() if account.is_capex() else None
        lease_name = self.oil_gas_generator.generate_lease_name()
        property_id = self.oil_gas_generator.generate_property_id()
        jib_number = self.oil_gas_generator.generate_jib_number(transaction_date) if random.random() < 0.4 else None
        cost_center = self.oil_gas_generator.generate_cost_center()
        journal_source = self.journal_generator.generate_journal_source()
        transaction_type = self.journal_generator.generate_transaction_type()

        # Generate amounts
        debit_amount, credit_amount = self.amount_generator.generate_for_account(account)

        # Posting date (use transaction date as posting date for historical records)
        posting_date = transaction_date

        # Use provided datetime or fixed start datetime for deterministic generation
        created_dt = transaction_datetime if transaction_datetime else self.FIXED_START_DATETIME

        # Create GL record
        gl_record = GLRecord(
            gl_entry_id=self._counter + 1,
            journal_batch=f"BATCH-{self._journal_batch:06d}",
            journal_entry=f"JE-{self._counter + 1:08d}",
            transaction_date=transaction_date,
            posting_date=posting_date,
            account_code=account.code,
            account_name=account.name,
            account_type="REVENUE" if is_revenue else "EXPENSE",
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            net_amount=round(credit_amount - debit_amount, 2),
            well_id=well_id,
            lease_name=lease_name,
            property_id=property_id,
            afe_number=afe_number,
            jib_number=jib_number,
            cost_center=cost_center,
            journal_source=journal_source,
            transaction_type=transaction_type,
            description=f"{transaction_type} - {account.name} for {well_id}",
            fiscal_period=transaction_date.strftime("%Y-%m"),
            fiscal_year=transaction_date.year,
            fiscal_month=transaction_date.month,
            state=self.oil_gas_generator.generate_state(),
            county=self.oil_gas_generator.generate_county(),
            basin=self.oil_gas_generator.generate_basin(),
            created_timestamp=created_dt,
            created_by=f"USER-{random.randint(100, 999)}",
            last_modified=created_dt
        )

        # Update counters
        self._counter += 1
        if self._counter % 50 == 0:
            self._journal_batch += 1

        return gl_record

    async def background_generate(self, interval_seconds: float = 30.0):
        """
        Background task that continuously generates new records and stores them in buffer.
        Historical records are already pre-loaded, so this just generates new ones.

        Args:
            interval_seconds: Time between records in seconds (default 1.0)
        """
        # Historical records are already pre-loaded, start generating new records immediately
        # Start from FIXED_START_DATETIME (after historical batch)
        # Start from FIXED_START_DATETIME (after historical batch)
        record_number = len(self._historical_batch)
        current_datetime = self.FIXED_START_DATETIME

        # Temporarily replace generators' random with our seeded RNG
        original_random = random.random
        original_choice = random.choice
        original_uniform = random.uniform
        original_randint = random.randint

        # Monkey-patch random functions to use our seeded RNG
        random.random = self._deterministic_rng.random
        random.choice = self._deterministic_rng.choice
        random.uniform = self._deterministic_rng.uniform
        random.randint = self._deterministic_rng.randint

        try:
            while True:
                await asyncio.sleep(interval_seconds)

                # Calculate transaction datetime deterministically: one record per second
                transaction_date = current_datetime.date()

                gl_record = self._generate_gl_record(
                    transaction_date=transaction_date,
                    transaction_datetime=current_datetime
                )

                # Increment current records counter
                self._current_records_count += 1
                self._total_streamed_count += 1

                # Store in buffer
                async with self._buffer_lock:
                    self._record_buffer.append(gl_record)

                # Move to next second (deterministic progression)
                current_datetime += timedelta(seconds=1)
                record_number += 1
        finally:
            # Restore original random functions
            random.random = original_random
            random.choice = original_choice
            random.uniform = original_uniform
            random.randint = original_randint

    async def stream_with_instant_buffer(self, interval_seconds: float = 30.0) -> AsyncGenerator[bytes]:
        """
        Stream GL records: first sends all buffered records instantly as JSON, then streams new ones.

        First sends all buffered records (historical + any new) as a single JSON array,
        then continues streaming new records as they're generated. All records are deterministic
        based on the fixed start date and seeded RNG.

        Args:
            interval_seconds: Time between records in seconds (default 1.0)
        """
        # First, send all buffered records instantly as JSON
        async with self._buffer_lock:
            buffered_records = self._record_buffer.copy()
            last_buffer_size = len(self._record_buffer)

        # Send all buffered records as a single JSON response
        buffered_data = {
            "type": "buffered_records",
            "count": len(buffered_records),
            "data": [record.to_dict() for record in buffered_records]
        }
        yield (json.dumps(buffered_data) + "\n").encode("utf-8")

        # Then continue streaming new records as they're generated
        while True:
            await asyncio.sleep(interval_seconds)

            async with self._buffer_lock:
                current_buffer_size = len(self._record_buffer)
                if current_buffer_size > last_buffer_size:
                    # New records available, stream them
                    for i in range(last_buffer_size, current_buffer_size):
                        gl_record = self._record_buffer[i]
                        new_record_data = {
                            "type": "new_record",
                            "data": gl_record.to_dict()
                        }
                        yield (json.dumps(new_record_data) + "\n").encode("utf-8")
                    last_buffer_size = current_buffer_size

    async def stream(self, interval_seconds: float = 30.0) -> AsyncGenerator[bytes]:
        """
        Stream GL records: first serves buffered records, then continues with new ones.

        First streams through all buffered records (already generated by background task),
        then continues streaming new records as they're generated. All records are deterministic
        based on the fixed start date and seeded RNG.

        Args:
            interval_seconds: Time between records in seconds (default 1.0)
        """
        # First, stream all buffered records
        buffer_index = 0
        while True:
            async with self._buffer_lock:
                if buffer_index < len(self._record_buffer):
                    gl_record = self._record_buffer[buffer_index]
                    buffer_index += 1
                else:
                    # No more buffered records, wait for new ones
                    break

            await asyncio.sleep(interval_seconds)
            yield (json.dumps(gl_record.to_dict()) + "\n").encode("utf-8")

        # Then continue streaming new records as they're generated
        last_buffer_size = len(self._record_buffer)
        while True:
            await asyncio.sleep(interval_seconds)

            async with self._buffer_lock:
                current_buffer_size = len(self._record_buffer)
                if current_buffer_size > last_buffer_size:
                    # New records available, stream them
                    for i in range(last_buffer_size, current_buffer_size):
                        gl_record = self._record_buffer[i]
                        yield (json.dumps(gl_record.to_dict()) + "\n").encode("utf-8")
                    last_buffer_size = current_buffer_size

    def get_buffered_records(self, limit: int = None) -> list[GLRecord]:
        """
        Get buffered records (historical + any new records generated).

        Args:
            limit: Maximum number of records to return (if None, returns all)

        Returns:
            List of GLRecord objects from the buffer
        """
        if limit is None:
            return self._record_buffer.copy()
        else:
            return self._record_buffer[:limit]

    def get_historical_range(
        self,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> list[GLRecord]:
        """
        Get historical GL records within a date range from pre-generated batch.

        Filters and returns records from the pre-generated historical batch that fall
        within the specified date range.

        Args:
            start_date: Start date for the range (inclusive)
            end_date: End date for the range (inclusive)

        Returns:
            List of GLRecord objects that fall within the date range
        """
        # Filter pre-generated records that fall within the date range
        filtered_records = [
            record for record in self._historical_batch
            if start_date <= record.transaction_date <= end_date
        ]

        return filtered_records

    async def stream_historical_range(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        interval_seconds: float = 1.0
    ) -> AsyncGenerator[bytes]:
        """
        Stream historical GL records within a date range from pre-generated batch.

        Filters and streams records from the pre-generated historical batch that fall
        within the specified date range.

        Args:
            start_date: Start date for the range (inclusive)
            end_date: End date for the range (inclusive)
            interval_seconds: Time between records in seconds (default 1.0)
        """
        # Get filtered records
        filtered_records = self.get_historical_range(start_date, end_date)

        # Stream the filtered records
        for gl_record in filtered_records:
            await asyncio.sleep(interval_seconds)
            yield (json.dumps(gl_record.to_dict()) + "\n").encode("utf-8")

    def generate_historical_batch(
        self,
        days: int = 365,
        start_date: date = None
    ) -> list[GLRecord]:
        """
        Generate a batch of historical GL records, one per day.

        Args:
            days: Number of days of records to generate (default 365)
            start_date: Start date for generation (if None, goes back from FIXED_START_DATE)

        Returns:
            List of GLRecord objects
        """
        # Use fixed start date if not provided, going back from FIXED_START_DATE
        if start_date is None:
            start_date = self.FIXED_START_DATE - timedelta(days=days)

        # Temporarily replace generators' random with our seeded RNG
        original_random = random.random
        original_choice = random.choice
        original_uniform = random.uniform
        original_randint = random.randint

        # Monkey-patch random functions to use our seeded RNG
        random.random = self._deterministic_rng.random
        random.choice = self._deterministic_rng.choice
        random.uniform = self._deterministic_rng.uniform
        random.randint = self._deterministic_rng.randint

        try:
            records = []
            current_date = start_date

            for _i in range(days):
                # Generate record with specific transaction date and datetime
                transaction_datetime = datetime.combine(current_date, datetime.min.time())
                gl_record = self._generate_gl_record(
                    transaction_date=current_date,
                    transaction_datetime=transaction_datetime
                )
                records.append(gl_record)

                # Move to next day
                current_date += timedelta(days=1)

            return records
        finally:
            # Restore original random functions
            random.random = original_random
            random.choice = original_choice
            random.uniform = original_uniform
            random.randint = original_randint

