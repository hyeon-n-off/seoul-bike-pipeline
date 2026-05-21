SELECT DISTINCT
    station_id,
    station_name
FROM {{ ref('stg_bike_usage') }}
ORDER BY station_id