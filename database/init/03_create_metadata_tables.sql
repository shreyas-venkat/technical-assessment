-- Metadata tables for pipeline monitoring and data quality
USE metadata;

-- Pipeline run tracking
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR PRIMARY KEY,
    pipeline_name VARCHAR NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR NOT NULL, -- 'RUNNING', 'SUCCESS', 'FAILED'
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data quality checks
CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_id VARCHAR PRIMARY KEY,
    table_name VARCHAR NOT NULL,
    check_type VARCHAR NOT NULL, -- 'NOT_NULL', 'UNIQUE', 'RANGE', 'CUSTOM'
    column_name VARCHAR,
    check_query TEXT,
    expected_result VARCHAR,
    actual_result VARCHAR,
    status VARCHAR NOT NULL, -- 'PASS', 'FAIL', 'WARNING'
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    run_id VARCHAR,
    FOREIGN KEY (run_id) REFERENCES metadata.pipeline_runs(run_id)
);

-- Data lineage tracking
CREATE TABLE IF NOT EXISTS data_lineage (
    lineage_id VARCHAR PRIMARY KEY,
    source_table VARCHAR NOT NULL,
    target_table VARCHAR NOT NULL,
    transformation_type VARCHAR, -- 'DIRECT', 'AGGREGATION', 'JOIN', 'FILTER'
    transformation_logic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Connection audit log
CREATE TABLE IF NOT EXISTS connection_audit (
    audit_id VARCHAR PRIMARY KEY,
    connection_type VARCHAR NOT NULL, -- 'READ', 'WRITE', 'ADMIN'
    user_identifier VARCHAR,
    client_info VARCHAR,
    database_name VARCHAR,
    table_accessed VARCHAR,
    operation VARCHAR, -- 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Ingestion watermark tracking (in raw schema for easier access)
USE raw;
CREATE TABLE IF NOT EXISTS metadata_ingestion_log (
    table_name VARCHAR PRIMARY KEY,
    last_ingestion_time TIMESTAMP NOT NULL,
    records_processed INTEGER DEFAULT 0,
    ingestion_status VARCHAR DEFAULT 'success', -- 'success', 'failed', 'partial'
    error_message TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for metadata tables
USE metadata;
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON metadata.pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_start_time ON metadata.pipeline_runs(start_time);
CREATE INDEX IF NOT EXISTS idx_data_quality_checks_status ON metadata.data_quality_checks(status);
CREATE INDEX IF NOT EXISTS idx_data_quality_checks_table ON metadata.data_quality_checks(table_name);
CREATE INDEX IF NOT EXISTS idx_connection_audit_timestamp ON metadata.connection_audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_connection_audit_user ON metadata.connection_audit(user_identifier);

-- Create indexes for raw schema tables
USE raw;
CREATE INDEX IF NOT EXISTS idx_metadata_ingestion_log_table ON raw.metadata_ingestion_log(table_name);
