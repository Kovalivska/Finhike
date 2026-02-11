-- SQL Solution for Finhike Risk Analysis Task
-- Database: PostgreSQL/Snowflake
-- Objective: Calculate client-level metrics from XML credit data

-- Assuming the XML data has been parsed and loaded into the following tables:
-- 1. credit_deals (crdeal data)
-- 2. deal_history (deallife data)

-- Create tables structure (if needed)
/*
CREATE TABLE credit_deals (
    client_id VARCHAR(100),
    deal_id VARCHAR(40),
    transaction_amount DECIMAL(15,2),
    transaction_type INT,
    currency INT,
    collateral_type INT,
    subject_role INT,
    collateral_value DECIMAL(15,2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deal_history (
    deal_id VARCHAR(40),
    period_month INT,
    period_year INT,
    start_date DATE,
    planned_end_date DATE,
    actual_end_date DATE,
    deal_status INT,
    current_limit DECIMAL(15,2),
    planned_payment DECIMAL(15,2),
    current_debt DECIMAL(15,2),
    overdue_debt DECIMAL(15,2),
    days_overdue INT,
    payment_made INT,
    arrears_present INT,
    calculation_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
*/

-- Main query to calculate required client metrics
WITH deal_status_summary AS (
    -- Get the latest status for each deal
    SELECT 
        cd.client_id,
        cd.deal_id,
        cd.transaction_amount,
        dh.actual_end_date,
        dh.overdue_debt,
        dh.days_overdue,
        ROW_NUMBER() OVER (
            PARTITION BY cd.deal_id 
            ORDER BY dh.period_year DESC, dh.period_month DESC
        ) as rn
    FROM credit_deals cd
    LEFT JOIN deal_history dh ON cd.deal_id = dh.deal_id
),
latest_deal_status AS (
    -- Filter to get only the latest record per deal
    SELECT *
    FROM deal_status_summary
    WHERE rn = 1
),
client_metrics AS (
    SELECT 
        client_id,
        
        -- 1. Total count of loans
        COUNT(DISTINCT deal_id) as total_loans_count,
        
        -- 2. Count of closed loans (those with actual_end_date)
        COUNT(DISTINCT CASE 
            WHEN actual_end_date IS NOT NULL 
            THEN deal_id 
        END) as closed_loans_count,
        
        -- 3. Sum of currently expired deals amount over 30+ days
        COALESCE(SUM(CASE 
            WHEN days_overdue > 30 AND overdue_debt IS NOT NULL 
            THEN overdue_debt 
            ELSE 0 
        END), 0) as expired_30_plus_amount
        
    FROM latest_deal_status
    GROUP BY client_id
)
-- Final results with calculated ratios
SELECT 
    client_id,
    total_loans_count,
    closed_loans_count,
    
    -- 2. Ratio of closed loans count over total loans count
    CASE 
        WHEN total_loans_count > 0 
        THEN ROUND(closed_loans_count::DECIMAL / total_loans_count, 4)
        ELSE 0 
    END as closed_loans_ratio,
    
    -- 3. Sum of currently expired deals amount over 30+ days
    ROUND(expired_30_plus_amount, 2) as expired_30_plus_amount
    
FROM client_metrics
ORDER BY client_id;

-- Additional queries for data validation and exploration

-- Query 1: Check data completeness
SELECT 
    'credit_deals' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT client_id) as unique_clients,
    COUNT(DISTINCT deal_id) as unique_deals
FROM credit_deals
UNION ALL
SELECT 
    'deal_history' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT deal_id) as unique_deals,
    NULL as unique_deals
FROM deal_history;

-- Query 2: Data quality checks
SELECT 
    'Deals without history' as check_type,
    COUNT(*) as count
FROM credit_deals cd
LEFT JOIN deal_history dh ON cd.deal_id = dh.deal_id
WHERE dh.deal_id IS NULL

UNION ALL

SELECT 
    'History without deals' as check_type,
    COUNT(*) as count
FROM deal_history dh
LEFT JOIN credit_deals cd ON dh.deal_id = cd.deal_id
WHERE cd.deal_id IS NULL;

-- Query 3: Distribution of deal statuses (for analysis)
SELECT 
    deal_status,
    COUNT(*) as count,
    ROUND(COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER () * 100, 2) as percentage
FROM (
    SELECT 
        dh.deal_status,
        ROW_NUMBER() OVER (
            PARTITION BY dh.deal_id 
            ORDER BY dh.period_year DESC, dh.period_month DESC
        ) as rn
    FROM deal_history dh
) ranked
WHERE rn = 1
GROUP BY deal_status
ORDER BY deal_status;

-- Query 4: Top clients by various metrics
-- Top clients by total loans
SELECT 
    client_id,
    total_loans_count,
    closed_loans_ratio,
    expired_30_plus_amount
FROM (
    SELECT 
        client_id,
        COUNT(DISTINCT deal_id) as total_loans_count,
        COUNT(DISTINCT CASE WHEN actual_end_date IS NOT NULL THEN deal_id END) as closed_loans_count,
        CASE 
            WHEN COUNT(DISTINCT deal_id) > 0 
            THEN ROUND(COUNT(DISTINCT CASE WHEN actual_end_date IS NOT NULL THEN deal_id END)::DECIMAL / COUNT(DISTINCT deal_id), 4)
            ELSE 0 
        END as closed_loans_ratio,
        COALESCE(SUM(CASE WHEN days_overdue > 30 AND overdue_debt IS NOT NULL THEN overdue_debt ELSE 0 END), 0) as expired_30_plus_amount
    FROM latest_deal_status
    GROUP BY client_id
) metrics
ORDER BY total_loans_count DESC
LIMIT 10;

-- Query 5: Export query for final results (formatted for CSV)
SELECT 
    cm.client_id as "Client ID",
    cm.total_loans_count as "Total Loans Count",
    cm.closed_loans_count as "Closed Loans Count", 
    cm.closed_loans_ratio as "Closed Loans Ratio",
    cm.expired_30_plus_amount as "Expired 30+ Days Amount"
FROM (
    SELECT 
        client_id,
        COUNT(DISTINCT deal_id) as total_loans_count,
        COUNT(DISTINCT CASE WHEN actual_end_date IS NOT NULL THEN deal_id END) as closed_loans_count,
        CASE 
            WHEN COUNT(DISTINCT deal_id) > 0 
            THEN ROUND(COUNT(DISTINCT CASE WHEN actual_end_date IS NOT NULL THEN deal_id END)::DECIMAL / COUNT(DISTINCT deal_id), 4)
            ELSE 0 
        END as closed_loans_ratio,
        COALESCE(SUM(CASE WHEN days_overdue > 30 AND overdue_debt IS NOT NULL THEN overdue_debt ELSE 0 END), 0) as expired_30_plus_amount
    FROM latest_deal_status
    GROUP BY client_id
) cm
ORDER BY cm.client_id;
