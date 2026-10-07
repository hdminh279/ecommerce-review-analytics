WITH base AS (
    SELECT * FROM {{ ref('int_category_monthly_metrics') }}
)

SELECT
    category,
    review_year,
    review_month,
    review_month_date,
    total_reviews,
    positive_count,
    negative_count,
    uncertain_count
FROM base
ORDER BY category, review_month_date
