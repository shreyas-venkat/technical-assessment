-- Raw tables for ingested data
-- These tables store data exactly as received from source systems

USE raw;

-- GL Records from FastAPI service
CREATE TABLE IF NOT EXISTS gl_records (
    -- Primary identifiers
    gl_entry_id INTEGER PRIMARY KEY,
    journal_batch VARCHAR NOT NULL,
    journal_entry VARCHAR NOT NULL,
    
    -- Dates
    transaction_date DATE NOT NULL,
    posting_date DATE NOT NULL,
    
    -- Account information
    account_code VARCHAR NOT NULL,
    account_name VARCHAR NOT NULL,
    account_type VARCHAR NOT NULL,
    
    -- Financial amounts
    debit_amount DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    credit_amount DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    net_amount DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    
    -- Oil & Gas specific fields
    well_id VARCHAR,
    lease_name VARCHAR,
    property_id VARCHAR,
    afe_number VARCHAR,
    jib_number VARCHAR,
    cost_center VARCHAR,
    
    -- Transaction metadata
    journal_source VARCHAR,
    transaction_type VARCHAR,
    description TEXT,
    
    -- Fiscal period information
    fiscal_period VARCHAR,
    fiscal_year INTEGER,
    fiscal_month INTEGER,
    
    -- Geographic information
    state VARCHAR(2),
    county VARCHAR,
    basin VARCHAR,
    
    -- Audit fields
    created_timestamp TIMESTAMP,
    created_by VARCHAR,
    last_modified TIMESTAMP,
    
    -- Pipeline metadata
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR DEFAULT 'fastapi'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_gl_records_transaction_date ON gl_records(transaction_date);
CREATE INDEX IF NOT EXISTS idx_gl_records_account_code ON gl_records(account_code);
CREATE INDEX IF NOT EXISTS idx_gl_records_well_id ON gl_records(well_id);
CREATE INDEX IF NOT EXISTS idx_gl_records_basin ON gl_records(basin);
CREATE INDEX IF NOT EXISTS idx_gl_records_fiscal_year_month ON gl_records(fiscal_year, fiscal_month);
