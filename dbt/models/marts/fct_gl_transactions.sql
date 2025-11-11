{{ config(materialized='table') }}

with gl_records as (
    select * from {{ ref('stg_gl_records') }}
),

enriched as (
    select
        gl_entry_id,
        journal_batch,
        journal_entry,
        transaction_date,
        posting_date,
        account_code,
        account_name,
        account_type,
        debit_amount,
        credit_amount,
        net_amount,
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
        
        -- Derived fields
        case 
            when debit_amount > 0 then 'DEBIT'
            when credit_amount > 0 then 'CREDIT'
            else 'ZERO'
        end as transaction_side,
        
        abs(net_amount) as absolute_amount,
        
        -- Date dimensions
        extract(year from transaction_date) as transaction_year,
        extract(month from transaction_date) as transaction_month,
        extract(quarter from transaction_date) as transaction_quarter,
        extract(dayofweek from transaction_date) as transaction_day_of_week,
        
        -- Business logic flags
        case when account_type = 'REVENUE' then true else false end as is_revenue,
        case when account_type = 'EXPENSE' then true else false end as is_expense,
        case when account_type = 'CAPEX' then true else false end as is_capex,
        
        created_timestamp,
        created_by,
        last_modified,
        ingested_at,
        source
        
    from gl_records
)

select * from enriched
