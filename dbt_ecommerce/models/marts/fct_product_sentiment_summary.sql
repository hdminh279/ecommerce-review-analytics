WITH reviews AS (
    SELECT * FROM {{ ref('stg_gold__fact_reviews') }}
),

metadata AS (
    SELECT * FROM {{ ref('stg_silver__metadata') }}
),

product_agg AS (
    SELECT
        parent_asin,
        category,
        COUNT(*) AS total_reviews,
        SUM(CASE WHEN sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) AS negative_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    GROUP BY parent_asin, category
),

with_metadata AS (
    SELECT
        p.parent_asin,
        p.category,
        COALESCE(m.title, 'Unknown Product') AS title,
        m.main_category,
        p.negative_count,
        p.total_reviews,
        ROUND(p.negative_count * 100.0 / NULLIF(p.total_reviews, 0), 2) AS negative_rate,
        p.avg_rating,
        DENSE_RANK() OVER (PARTITION BY p.category ORDER BY p.negative_count DESC) AS rank_negative_volume
    FROM product_agg p
    LEFT JOIN metadata m ON p.parent_asin = m.parent_asin
)

SELECT * FROM with_metadata
ORDER BY negative_count DESC
