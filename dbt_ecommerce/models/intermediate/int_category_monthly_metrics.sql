WITH fact_reviews AS (
    SELECT * FROM {{ ref('stg_gold__fact_reviews') }}
),

aggregated AS (
    SELECT
        category,
        review_year,
        review_month,
        review_month_date,
        COUNT(*) AS total_reviews,
        SUM(CASE WHEN sentiment = 'POSITIVE' THEN 1 ELSE 0 END) AS positive_count,
        SUM(CASE WHEN sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) AS negative_count,
        SUM(CASE WHEN sentiment = 'UNCERTAIN' THEN 1 ELSE 0 END) AS uncertain_count
    FROM fact_reviews
    GROUP BY
        category,
        review_year,
        review_month,
        review_month_date
)

SELECT * FROM aggregated
