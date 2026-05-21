SELECT
    station_id,
    station_name,
    SUM(usage_count)                             as total_usage,
    ROUND(AVG(distance), 2)                      as avg_distance,
    ROUND(SUM(carbon_amount), 2)                 as total_carbon_amount,
    RANK() OVER (ORDER BY SUM(usage_count) DESC) as usage_rank
FROM {{ ref('stg_bike_usage') }}
GROUP BY station_id, station_name
ORDER BY usage_rank