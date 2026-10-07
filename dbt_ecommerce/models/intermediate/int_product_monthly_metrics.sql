WITH fact_reviews AS (
    SELECT * FROM {{ ref('stg_gold__fact_reviews') }}
),

aggregated AS (
    SELECT
        parent_asin,
        category,
        review_month_date,
        COUNT(*) AS monthly_reviews,
        SUM(CASE WHEN sentiment = 'POSITIVE' THEN 1 ELSE 0 END) AS monthly_positive_count,
        SUM(CASE WHEN sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) AS monthly_negative_count,
        SUM(CASE WHEN sentiment = 'UNCERTAIN' THEN 1 ELSE 0 END) AS monthly_uncertain_count,
        ROUND(AVG(rating), 2) AS monthly_avg_rating,
        ROUND(AVG(sentiment_score), 4) AS monthly_avg_sentiment_score
    FROM fact_reviews
    GROUP BY
        parent_asin,
        category,
        review_month_date
),

with_rates AS (
    SELECT
        *,
        ROUND(monthly_negative_count * 100.0 / NULLIF(monthly_reviews, 0), 2) AS monthly_neg_rate,
        ROUND(monthly_positive_count * 100.0 / NULLIF(monthly_reviews, 0), 2) AS monthly_pos_rate
    FROM aggregated
)

SELECT * FROM with_rates
