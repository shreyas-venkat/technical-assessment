"""Auto-partitioned incremental ingestion for GL records."""
from datetime import datetime, timezone, date
import pandas as pd
import dagster as dg
from dagster import (
    asset, 
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    MonthlyPartitionsDefinition,
    TimeWindowPartitionsDefinition,
    StaticPartitionsDefinition,
)

from ..resources import DuckDBWarehouse, FastAPIClient

# Auto-generating quarterly partitions
def generate_quarterly_partitions(start_year=2024, num_years=5):
    """Auto-generate quarterly partitions for multiple years."""
    partitions = []
    for year in range(start_year, start_year + num_years):
        for quarter in range(1, 5):  # Q1, Q2, Q3, Q4
            partitions.append(f"{year}-Q{quarter}")
    return partitions

quarterly_partitions = StaticPartitionsDefinition(
    generate_quarterly_partitions(start_year=2024, num_years=5)  # 2024-2028
)

# Helper function to get date range for quarter partition
def get_quarter_date_range(quarter_key):
    """Convert quarter key like '2025-Q1' to start/end dates."""
    year, quarter = quarter_key.split('-Q')
    year, quarter = int(year), int(quarter)
    
    if quarter == 1:
        start_month, end_month = 1, 3
    elif quarter == 2:
        start_month, end_month = 4, 6
    elif quarter == 3:
        start_month, end_month = 7, 9
    else:  # Q4
        start_month, end_month = 10, 12
    
    start_date = date(year, start_month, 1)
    
    # Get first day of next quarter
    if quarter == 4:
        end_date = date(year + 1, 1, 1)  # Next year Q1
    else:
        end_date = date(year, end_month + 1, 1)  # Next quarter
    
    return start_date, end_date


@asset(
    partitions_def=quarterly_partitions,
    group_name="ingestion",
    description="Quarterly partitioned GL records from FastAPI (auto-generates partitions)",
)
def raw_gl_records(
    context: AssetExecutionContext,
    duckdb_warehouse: DuckDBWarehouse,
    fastapi_client: FastAPIClient,
) -> MaterializeResult:
    """
    Quarterly partitioned asset for GL records - each partition represents 3 months of data.
    
    Much more reasonable than daily partitions - only 4 partitions per year!
    """
    
    # Get the partition quarter for this run
    partition_quarter = context.partition_key
    context.log.info(f"Processing partition for quarter: {partition_quarter}")
    
    # Get date range for this quarter
    start_date, end_date = get_quarter_date_range(partition_quarter)
    context.log.info(f"Quarter {partition_quarter} covers {start_date} to {end_date}")
    
    # Get records from API
    context.log.info(f"Fetching GL records for {partition_quarter}...")
    gl_records = fastapi_client.get_gl_records(limit=5000)
    
    if not gl_records:
        context.log.info(f"No records from API for {partition_quarter}")
        return MaterializeResult(
            metadata={
                "partition_quarter": partition_quarter,
                "records_processed": 0,
            }
        )
    
    # Convert to DataFrame
    df = pd.DataFrame(gl_records)
    context.log.info(f"Got {len(df)} records from API")
    
    # Filter records for this quarter's date range
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.date
    quarter_records = df[
        (df['transaction_date'] >= start_date) & 
        (df['transaction_date'] < end_date)
    ]
    
    if quarter_records.empty:
        context.log.info(f"No records found for quarter {partition_quarter}")
        return MaterializeResult(
            metadata={
                "partition_quarter": partition_quarter,
                "records_processed": 0,
                "total_api_records": len(df),
                "date_range": f"{start_date} to {end_date}",
            }
        )
    
    context.log.info(f"Found {len(quarter_records)} records for {partition_quarter}")
    context.log.info(f"ID range: {quarter_records['gl_entry_id'].min()} - {quarter_records['gl_entry_id'].max()}")
    context.log.info(f"Date range: {quarter_records['transaction_date'].min()} - {quarter_records['transaction_date'].max()}")
    
    # Add ingestion metadata
    current_time = datetime.now(timezone.utc)
    quarter_records = quarter_records.copy()
    quarter_records['ingested_at'] = current_time
    quarter_records['source'] = 'fastapi'
    
    # Insert into DuckDB
    with duckdb_warehouse.get_connection() as conn:
        try:
            # Delete existing records for this quarter to handle re-processing
            conn.execute(f"""
                DELETE FROM raw.gl_records 
                WHERE DATE(transaction_date) >= '{start_date}' 
                AND DATE(transaction_date) < '{end_date}'
                AND source = 'fastapi'
            """)
            
            conn.execute("INSERT INTO raw.gl_records SELECT * FROM quarter_records")
            context.log.info(f"Successfully inserted {len(quarter_records)} records for {partition_quarter}")
            
        except Exception as e:
            context.log.error(f"Failed to insert records for {partition_quarter}: {e}")
            raise
    
    return MaterializeResult(
        metadata={
            "partition_quarter": partition_quarter,
            "records_processed": len(quarter_records),
            "id_range": f"{quarter_records['gl_entry_id'].min()}-{quarter_records['gl_entry_id'].max()}",
            "date_range": f"{start_date} to {end_date}",
            "ingestion_time": MetadataValue.timestamp(current_time),
            "total_api_records": len(df),
        }
    )


# Simple non-partitioned version for comparison
@asset(
    group_name="ingestion",
    description="Simple incremental GL records (no partitions)",
)
def raw_gl_records_simple(
    context: AssetExecutionContext,
    duckdb_warehouse: DuckDBWarehouse,
    fastapi_client: FastAPIClient,
) -> MaterializeResult:
    """Simple incremental loading using gl_entry_id as watermark."""
    
    # Get records from API
    context.log.info("Fetching GL records from API...")
    gl_records = fastapi_client.get_gl_records(limit=5000)
    
    if not gl_records:
        context.log.info("No records from API")
        return MaterializeResult(metadata={"records_processed": 0})
    
    # Convert to DataFrame
    df = pd.DataFrame(gl_records)
    context.log.info(f"Got {len(df)} records from API")
    
    with duckdb_warehouse.get_connection() as conn:
        # Find the highest gl_entry_id we already have
        try:
            result = conn.execute("SELECT COUNT(*), COALESCE(MAX(gl_entry_id), 0) FROM raw.gl_records").fetchone()
            record_count = result[0]
            max_existing_id = result[1]
            context.log.info(f"Database has {record_count} existing records")
            context.log.info(f"Highest existing gl_entry_id: {max_existing_id}")
        except Exception as e:
            context.log.info(f"Error querying database (table might not exist): {e}")
            max_existing_id = 0
            record_count = 0
        
        # If database is empty, insert all records
        if record_count == 0:
            context.log.info("Database is empty, inserting all records")
            new_records = df.copy()
        else:
            # Only keep records with gl_entry_id higher than what we have
            new_records = df[df['gl_entry_id'] > max_existing_id]
        
        if new_records.empty:
            context.log.info("No new records to insert")
            return MaterializeResult(metadata={"records_processed": 0})
        
        context.log.info(f"Found {len(new_records)} new records to insert")
        
        # Add metadata columns
        current_time = datetime.now(timezone.utc)
        new_records = new_records.copy()
        new_records['ingested_at'] = current_time
        new_records['source'] = 'fastapi'
        
        # Insert directly into DuckDB
        conn.execute("INSERT INTO raw.gl_records SELECT * FROM new_records")
        
        context.log.info(f"Successfully inserted {len(new_records)} records")
        
        return MaterializeResult(
            metadata={
                "records_processed": len(new_records),
                "highest_id_inserted": int(new_records['gl_entry_id'].max()),
                "ingestion_time": MetadataValue.timestamp(current_time),
            }
        )