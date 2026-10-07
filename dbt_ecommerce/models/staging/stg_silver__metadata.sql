WITH source AS (
    SELECT * FROM {{ source('amazon_datalake', 'silver_metadata') }}
),

cleaned AS (
    SELECT
        TRIM(parent_asin) AS parent_asin,
        TRIM(COALESCE(title, 'Unknown Product')) AS title,
        TRIM(COALESCE(main_category, 'General')) AS main_category,
        categories,
        features,
        details
    FROM source
    WHERE parent_asin IS NOT NULL
)

SELECT * FROM cleaned
