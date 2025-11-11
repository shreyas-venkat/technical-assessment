"""FastAPI application for QByte GL Data Service."""
import asyncio
import logging
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exception_handlers import http_exception_handler
from datetime import date, datetime
from services.gl_streamer import GLDataStreamer
from core.accounts import AccountRegistry
from core.exceptions import (
    GLDataServiceException,
    InvalidDateRangeError,
    StreamingError,
    validation_error,
    internal_server_error
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QByte GL Data Service",
    description="""
    A FastAPI service that generates and streams QByte-style General Ledger (GL) data 
    for oil & gas operations. This service simulates real-time GL entries with realistic 
    oil & gas accounting fields including well IDs, AFE numbers, JIB numbers, and more.
    
    ## Features
    
    * Streams GL records one per 30 seconds
    * QByte-compatible data structure
    * Oil & gas specific fields (wells, basins, leases, etc.)
    * Multiple account types (Revenue, Operating Expenses, Capex, Admin)
    * Realistic transaction amounts and dates
    
    ## Usage
    
    Use the `/get-gl` endpoint to receive a continuous stream of GL records.
    Each record is a JSON object sent as a newline-delimited stream.
    """,
    version="1.0.0",
    tags_metadata=[
        {
            "name": "streaming",
            "description": "Streaming endpoints for GL data",
        },
        {
            "name": "info",
            "description": "Service information and metadata",
        },
        {
            "name": "health",
            "description": "Health check endpoints",
        },
    ]
)

# Initialize the GL streamer
gl_streamer = GLDataStreamer()
account_registry = AccountRegistry()


# Global exception handlers
@app.exception_handler(GLDataServiceException)
async def gl_service_exception_handler(request: Request, exc: GLDataServiceException):
    """Handle custom GL service exceptions."""
    logger.error(f"GL Service Exception: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": "GLDataServiceException"
        }
    )


@app.exception_handler(InvalidDateRangeError)
async def invalid_date_range_handler(request: Request, exc: InvalidDateRangeError):
    """Handle invalid date range exceptions."""
    logger.warning(f"Invalid date range: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": "InvalidDateRangeError"
        }
    )


@app.exception_handler(StreamingError)
async def streaming_error_handler(request: Request, exc: StreamingError):
    """Handle streaming exceptions."""
    logger.error(f"Streaming error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": "StreamingError"
        }
    )


async def background_stream_task():
    """Background task that continuously generates records and stores them in buffer."""
    await gl_streamer.background_generate()


@app.on_event("startup")
async def startup_event():
    """Start background streaming task on server startup."""
    asyncio.create_task(background_stream_task())


@app.get("/", tags=["info"], summary="API Information")
async def root():
    """Get API information and available endpoints."""
    return {
        "service": "QByte GL Data Service",
        "version": "1.0.0",
        "description": "Streams QByte-style General Ledger data for oil & gas operations",
        "endpoints": {
            "/health": "Health check endpoint",
            "/get-gl": "Stream GL records (instant buffered records + real-time streaming)",
            "/docs": "Interactive API documentation",
            "/openapi.json": "OpenAPI schema"
        },
        "account_types": account_registry.get_account_types_info()
    }


@app.get(
    "/get-gl",
    tags=["streaming"],
    summary="Stream GL Data",
    description="""
    Streams QByte-style General Ledger records.
    
    **Modes:**
    1. **Continuous streaming**: When no date range is provided, first streams 1000 pre-generated historical 
       records (generated at startup at 3 per hour spacing), then continues generating new real-time records 
       indefinitely, one per second.
    2. **Date range filter**: When `start_date` and `end_date` are provided, returns a JSON array of records 
       from the pre-generated historical batch that fall within the specified date range.
    
    **Parameters:**
    - **start_date**: Start date for historical records (YYYY-MM-DD format). If provided, `end_date` is required.
    - **end_date**: End date for historical records (YYYY-MM-DD format). If provided, `start_date` is required.
    
    **Response Format:**
    - **Without date range**: Streaming response - each line is a JSON object (newline-delimited JSON).
      Streams 1000 pre-generated historical records, then continues with new records indefinitely.
    - **With date range**: JSON response - returns a JSON array of records that match the date range.
      Example: `{"count": 150, "data": [{...}, {...}, ...]}`
    - Each record contains a complete GL entry with oil & gas specific fields
    
    **Example Record:**
    ```json
    {
        "gl_entry_id": 1,
        "journal_batch": "BATCH-000001",
        "journal_entry": "JE-00000001",
        "transaction_date": "2024-01-15",
        "account_code": "4100",
        "account_name": "Crude Oil Sales Revenue",
        "account_type": "REVENUE",
        "debit_amount": 0.0,
        "credit_amount": 25000.50,
        "well_id": "PERM-1234",
        "basin": "Permian",
        "state": "TX",
        ...
    }
    ```
    
    **Examples:**
    - Real-time: `GET /get-gl`
    - Historical: `GET /get-gl?start_date=2024-01-01&end_date=2024-01-15`
    
    **Note:** This is a streaming endpoint. Use Ctrl+C or close the connection to stop.
    """,
    response_description="Stream of GL records as newline-delimited JSON"
)
async def stream_gl_data(
    start_date: str = Query(None, description="Start date for historical records (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date for historical records (YYYY-MM-DD)")
) -> StreamingResponse:
    """
    Stream GL data records.
    
    If date range is provided, filters and returns records from the pre-generated historical batch 
    that fall within the date range. Otherwise, first streams the pre-generated batch of 1000 historical 
    records (created at startup), then continues generating new real-time records indefinitely.
    
    Args:
        start_date: Start date for historical batch generation (YYYY-MM-DD format)
        end_date: End date for historical batch generation (YYYY-MM-DD format)
    
    Returns:
        StreamingResponse with GL records as newline-delimited JSON
    """
    # Parse and validate date parameters
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date is not None or end_date is not None:
        if start_date is None or end_date is None:
            raise HTTPException(
                status_code=400,
                detail="Both start_date and end_date must be provided together"
            )
        
        # Strip whitespace and parse dates
        try:
            parsed_start_date = date.fromisoformat(start_date.strip())
            parsed_end_date = date.fromisoformat(end_date.strip())
        except ValueError as e:
            raise InvalidDateRangeError(
                f"Invalid date format. Use YYYY-MM-DD format. Error: {str(e)}",
                {"start_date": start_date, "end_date": end_date}
            )
        
        if parsed_start_date > parsed_end_date:
            raise InvalidDateRangeError(
                "start_date must be before or equal to end_date",
                {"start_date": str(parsed_start_date), "end_date": str(parsed_end_date)}
            )
        
        # Get filtered records and return as JSON array
        filtered_records = gl_streamer.get_historical_range(parsed_start_date, parsed_end_date)
        
        return JSONResponse(
            content={
                "count": len(filtered_records),
                "start_date": str(parsed_start_date),
                "end_date": str(parsed_end_date),
                "data": [record.to_dict() for record in filtered_records]
            }
        )
    
    # Otherwise, return buffered records first, then stream new ones
    return StreamingResponse(
        gl_streamer.stream_with_instant_buffer(),
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/health", tags=["health"], summary="Health Check")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns the service status and basic information about the service health.
    """
    return {
        "status": "healthy",
        "service": "QByte GL Data Service",
        "version": "1.0.0",
        "historical_records": len(gl_streamer._historical_batch),
        "total_streamed": gl_streamer.get_total_streamed_count(),
        "total_records": len(gl_streamer._historical_batch) + gl_streamer.get_total_streamed_count(),
        "timestamp": datetime.now().isoformat()
    }


