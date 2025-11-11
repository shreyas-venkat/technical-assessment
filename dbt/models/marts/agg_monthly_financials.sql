{{ config(materialized='table') }}

with gl_transactions as (
    select * from {{ ref('fct_gl_transactions') }}
),

monthly_summary as (
    select
        fiscal_year,
        fiscal_month,
        transaction_year,
        transaction_month,
        state,
        basin,
        account_type,
        
        -- Financial metrics
        count(*) as transaction_count,
        sum(debit_amount) as total_debits,
        sum(credit_amount) as total_credits,
        sum(net_amount) as net_amount,
        avg(absolute_amount) as avg_transaction_size,
        
        -- Revenue metrics
        sum(case when is_revenue then net_amount else 0 end) as total_revenue,
        
        -- Expense metrics  
        sum(case when is_expense then abs(net_amount) else 0 end) as total_expenses,
        
        -- Capex metrics
        sum(case when is_capex then abs(net_amount) else 0 end) as total_capex,
        
        -- Well metrics
        count(distinct well_id) as unique_wells,
        count(distinct lease_name) as unique_leases,
        
        -- Data quality
        min(transaction_date) as earliest_transaction,
        max(transaction_date) as latest_transaction,
        
        current_timestamp as created_at
        
    from gl_transactions
    group by 1, 2, 3, 4, 5, 6, 7
)

select * from monthly_summary
