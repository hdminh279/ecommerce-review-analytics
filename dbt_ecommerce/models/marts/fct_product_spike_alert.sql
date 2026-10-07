WITH monthly_metrics AS (
    SELECT * FROM {{ ref('int_product_monthly_metrics') }}
),

metadata AS (
    SELECT * FROM {{ ref('stg_silver__metadata') }}
),

with_rolling_baseline AS (
    SELECT
        parent_asin,
        category,
        review_month_date,
        monthly_reviews,
        monthly_positive_count,
        monthly_negative_count,
        monthly_uncertain_count,
        monthly_neg_rate,
        monthly_pos_rate,
        monthly_avg_rating,
        -- Rolling 3-Month Lookback Baseline (Excluding Current Month)
        COUNT(monthly_neg_rate) OVER (
            PARTITION BY parent_asin 
            ORDER BY review_month_date 
            ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
        ) AS baseline_history_months,
        ROUND(AVG(monthly_neg_rate) OVER (
            PARTITION BY parent_asin 
            ORDER BY review_month_date 
            ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
        ), 2) AS baseline_avg_neg_rate,
        ROUND(STDDEV_SAMP(monthly_neg_rate) OVER (
            PARTITION BY parent_asin 
            ORDER BY review_month_date 
            ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
        ), 4) AS baseline_std_neg_rate
    FROM monthly_metrics
),

with_z_score AS (
    SELECT
        b.*,
        -- Statistical Z-score calculation with zero-division safeguard
        CASE
            WHEN baseline_history_months >= 2 AND baseline_std_neg_rate > 0.001 THEN
                ROUND((monthly_neg_rate - baseline_avg_neg_rate) / baseline_std_neg_rate, 2)
            ELSE 0.0
        END AS z_score,
        -- Absolute spike jump in percentage points
        ROUND(monthly_neg_rate - COALESCE(baseline_avg_neg_rate, 0.0), 2) AS neg_rate_jump_pts
    FROM with_rolling_baseline b
),

with_spike_detection AS (
    SELECT
        z.*,
        m.title,
        m.main_category,
        -- Anomaly Detection Flag: Z >= 2.0 with statistical volume safeguards
        CASE
            WHEN z.z_score >= 2.0 
             AND z.monthly_reviews >= 10 
             AND z.monthly_negative_count >= 4 
             AND z.baseline_history_months >= 2 
             AND z.neg_rate_jump_pts >= 15.0
            THEN 1
            ELSE 0
        END AS is_negative_spike,
        -- Severity classification
        CASE
            WHEN z.z_score >= 3.0 AND z.monthly_reviews >= 15 THEN 'CRITICAL_SURGE'
            WHEN z.z_score >= 2.0 AND z.monthly_reviews >= 10 THEN 'WARNING_SPIKE'
            ELSE 'STABLE'
        END AS alert_severity
    FROM with_z_score z
    LEFT JOIN metadata m ON z.parent_asin = m.parent_asin
)

SELECT * FROM with_spike_detection
WHERE is_negative_spike = 1 OR alert_severity != 'STABLE'
ORDER BY z_score DESC, monthly_negative_count DESC
