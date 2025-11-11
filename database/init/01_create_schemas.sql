-- Initialize DuckDB schemas for Dakota Analytics pipeline
-- This script creates the foundational schema structure

-- Raw data schema - for ingested data from external sources
CREATE SCHEMA IF NOT EXISTS raw;

-- Staging schema - for cleaned and standardized data
CREATE SCHEMA IF NOT EXISTS staging;

-- Marts schema - for business logic and analytics-ready tables
CREATE SCHEMA IF NOT EXISTS marts;

-- Metadata schema - for pipeline metadata and data quality
CREATE SCHEMA IF NOT EXISTS metadata;

-- Set default schema
USE raw;
