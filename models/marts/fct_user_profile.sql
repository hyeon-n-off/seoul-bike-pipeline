SELECT
    gender,
    age_group,
    SUM(usage_count)                        as total_usage,
    ROUND(AVG(distance), 2)                 as avg_distance,
    ROUND(AVG(duration), 2)                 as avg_duration,
    ROUND(SUM(carbon_amount), 2)            as total_carbon_amount
FROM {{ ref('stg_bike_usage') }}
WHERE gender != 'UNKNOWN'
GROUP BY gender, age_group
ORDER BY gender, age_group