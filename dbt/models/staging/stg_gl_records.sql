{{ config(materialized='view') }}

with source_data as (
    select * from {{ source('raw', 'gl_records') }}
),

cleaned as (
    select
        gl_entry_id,
        journal_batch,
        journal_entry,
        transaction_date::date as transaction_date,
        posting_date::date as posting_date,
        account_code,
        account_name,
        account_type,
        debit_amount::decimal(15,2) as debit_amount,
        credit_amount::decimal(15,2) as credit_amount,
        net_amount::decimal(15,2) as net_amount,
        well_id,
        lease_name,
        property_id,
        afe_number,
        jib_number,
        cost_center,
        journal_source,
        transaction_type,
        description,
        fiscal_period,
        fiscal_year,
        fiscal_month,
        state,
        county,
        basin,
        created_timestamp::timestamp as created_timestamp,
        created_by,
        last_modified::timestamp as last_modified,
        ingested_at::timestamp as ingested_at,
        source
    from source_data
    where transaction_date is not null
      and account_code is not null
)

select * from cleaned
