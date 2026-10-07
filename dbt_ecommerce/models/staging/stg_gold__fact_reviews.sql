WITH source AS (
    SELECT * FROM {{ source('amazon_datalake', 'fact_review_sentiment') }}
),

cleaned AS (
    SELECT
        review_id,
        parent_asin,
        category,
        CAST(review_date AS TIMESTAMP) AS review_date,
        CAST(rating AS FLOAT) AS rating,
        UPPER(TRIM(sentiment)) AS sentiment,
        CAST(sentiment_score AS DOUBLE) AS sentiment_score,
        CAST(confidence AS DOUBLE) AS confidence,
        CAST(is_negative AS INTEGER) AS is_negative,
        -- Date dimension fields
        DATE_TRUNC('month', CAST(review_date AS TIMESTAMP)) AS review_month_date,
        EXTRACT(YEAR FROM CAST(review_date AS TIMESTAMP)) AS review_year,
        EXTRACT(MONTH FROM CAST(review_date AS TIMESTAMP)) AS review_month
    FROM source
    WHERE review_date IS NOT NULL
      AND parent_asin IS NOT NULL
)

SELECT * FROM cleaned
