{{ config(materialized='table') }}

with gl_records as (
    select * from {{ ref('stg_gl_records') }}
),

well_attributes as (
    select
        well_id,
        lease_name,
        property_id,
        state,
        county,
        basin,
        
        -- Aggregated metrics
        count(*) as total_transactions,
        sum(case when account_type = 'REVENUE' then net_amount else 0 end) as total_revenue,
        sum(case when account_type = 'EXPENSE' then abs(net_amount) else 0 end) as total_expenses,
        sum(case when account_type = 'CAPEX' then abs(net_amount) else 0 end) as total_capex,
        
        min(transaction_date) as first_transaction_date,
        max(transaction_date) as last_transaction_date,
        
        -- Well status
        case 
            when max(transaction_date) >= current_date - interval '30 days' then 'ACTIVE'
            when max(transaction_date) >= current_date - interval '90 days' then 'INACTIVE'
            else 'DORMANT'
        end as well_status,
        
        current_timestamp as created_at
        
    from gl_records
    where well_id is not null
    group by 1, 2, 3, 4, 5, 6
)

select * from well_attributes
