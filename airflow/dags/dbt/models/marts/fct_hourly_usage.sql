SELECT
    rental_hour,
    CASE
        WHEN rental_hour BETWEEN 7 and 10   THEN 'MORNING'
        WHEN rental_hour BETWEEN 11 and 13  THEN 'LUNCH'
        WHEN rental_hour BETWEEN 18 and 20  THEN 'EVENING'
        ELSE 'OTHER'
    END                                 as time_slot,
    SUM(usage_count)                    as total_usage,
    ROUND(AVG(distance), 2)             as avg_distance,
    ROUND(AVG(duration), 2)             as avg_duration
FROM {{ ref('stg_bike_usage') }}
GROUP BY rental_hour
ORDER BY rental_hour