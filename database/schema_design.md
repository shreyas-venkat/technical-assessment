# DuckDB Schema Design for Dakota Analytics

## Overview

This document describes the database schema design for the Dakota Analytics data pipeline using DuckDB as the analytical data warehouse.

## Design Rationale

### Why DuckDB?

1. **Analytics-First**: Optimized for OLAP workloads and complex analytical queries
2. **Columnar Storage**: Excellent compression and performance for time-series data
3. **Embedded**: No server management overhead, perfect for containerized deployments
4. **dbt Integration**: First-class support for modern data transformation workflows
5. **Performance**: Fast aggregations and joins on large datasets
6. **Simplicity**: File-based, easy backup and deployment

### Schema Architecture

We use a **medallion architecture** with three main layers:

```
Raw Layer → Staging Layer → Marts Layer
   ↓            ↓             ↓
Ingested    Cleaned &     Business
  Data      Validated      Logic
```

## Schema Structure

### 1. Raw Schema (`raw`)

**Purpose**: Store data exactly as received from source systems

**Tables**:
- `gl_records`: General Ledger transactions from FastAPI
- `eia_petroleum`: Petroleum data from EIA API

**Characteristics**:
- Minimal transformations
- Preserves source data types
- Includes ingestion metadata
- Optimized for write performance

### 2. Staging Schema (`staging`)

**Purpose**: Cleaned and standardized data ready for business logic

**Tables** (created by dbt):
- `stg_gl_records`: Cleaned GL data with proper types
- `stg_eia_petroleum`: Standardized EIA data

**Characteristics**:
- Data type conversions
- Basic validation and cleaning
- Consistent naming conventions
- Views for performance

### 3. Marts Schema (`marts`)

**Purpose**: Business-ready tables with applied business logic

**Tables** (created by dbt):
- `fct_gl_transactions`: Fact table for GL transactions
- `dim_wells`: Well dimension with aggregated metrics
- `agg_monthly_financials`: Monthly financial summaries

**Characteristics**:
- Business logic applied
- Optimized for analytics
- Materialized tables for performance
- Rich metadata and documentation

### 4. Metadata Schema (`metadata`)

**Purpose**: Pipeline monitoring and data governance

**Tables**:
- `pipeline_runs`: Track pipeline execution
- `data_quality_checks`: Data quality test results
- `data_lineage`: Track data transformations
- `connection_audit`: Access control and auditing

## Key Design Decisions

### 1. Time-Series Optimization

**Partitioning Strategy**:
- Primary partitioning by `transaction_date` for GL records
- Secondary partitioning by `fiscal_year` and `fiscal_month`
- Indexes on date columns for fast filtering

**Rationale**: Oil & gas financial data is heavily time-based, with most queries filtering by date ranges.

### 2. Oil & Gas Domain Model

**Well-Centric Design**:
- `well_id` as primary business key
- Geographic hierarchy: `state` → `county` → `basin`
- AFE (Authorization for Expenditure) tracking
- JIB (Joint Interest Billing) support

**Rationale**: Reflects real-world oil & gas accounting practices and reporting needs.

### 3. Financial Data Integrity

**Double-Entry Bookkeeping**:
- Separate `debit_amount` and `credit_amount` columns
- Calculated `net_amount` field
- Account type classification
- Audit trail with `created_by` and `last_modified`

**Rationale**: Maintains accounting standards and enables financial reconciliation.

### 4. Data Quality Framework

**Built-in Quality Checks**:
- NOT NULL constraints on critical fields
- UNIQUE constraints on business keys
- Range validation on amounts
- Referential integrity where applicable

**Rationale**: Ensures data reliability for financial reporting and analytics.

## Performance Considerations

### Indexing Strategy

**Primary Indexes**:
- `transaction_date` - Most common filter
- `account_code` - Account-based reporting
- `well_id` - Well-based analytics
- `basin` - Geographic analysis

**Composite Indexes**:
- `(fiscal_year, fiscal_month)` - Period reporting
- `(state, basin)` - Geographic hierarchy

### Compression

**DuckDB Automatic Compression**:
- Columnar storage with automatic compression
- Dictionary encoding for categorical data
- Run-length encoding for repeated values
- Delta compression for numeric sequences

## Access Control

### Authentication Model

Since DuckDB doesn't have built-in authentication, we implement:

1. **API Key System**: SHA-256 hashed keys with permissions
2. **Permission Levels**: `read`, `write`, `admin`
3. **Audit Logging**: All connections and operations logged
4. **Connection Management**: Pooled connections with lifecycle management

### Security Features

- **Connection Auditing**: Track all database access
- **Permission Validation**: Role-based access control
- **API Key Rotation**: Support for key lifecycle management
- **Error Logging**: Security events and failed access attempts

## Backup and Recovery

### File-Based Backup

**Strategy**:
- Regular file system snapshots of `.duckdb` file
- Export critical tables to Parquet for long-term storage
- Version control for schema changes

**Recovery**:
- Point-in-time recovery from file snapshots
- Incremental recovery from Parquet exports
- Schema recreation from initialization scripts

## Monitoring and Observability

### Pipeline Monitoring

- **Run Tracking**: Every pipeline execution logged
- **Data Quality**: Automated quality checks with alerts
- **Performance Metrics**: Query performance and resource usage
- **Lineage Tracking**: Full data transformation history

### Health Checks

- **Connection Health**: Validate database connectivity
- **Schema Integrity**: Verify table structures
- **Data Freshness**: Monitor last update timestamps
- **Quality Metrics**: Track data quality scores

## Future Enhancements

### Scalability

1. **Partitioning**: Implement time-based partitioning for large tables
2. **Archiving**: Move old data to cheaper storage (Parquet/S3)
3. **Replication**: Read replicas for analytical workloads
4. **Sharding**: Distribute data across multiple DuckDB instances

### Advanced Features

1. **Streaming**: Real-time data ingestion with change data capture
2. **ML Integration**: Feature stores and model training data
3. **APIs**: GraphQL or REST APIs for data access
4. **Visualization**: Direct integration with BI tools

This schema design provides a solid foundation for oil & gas analytics while maintaining flexibility for future requirements.
