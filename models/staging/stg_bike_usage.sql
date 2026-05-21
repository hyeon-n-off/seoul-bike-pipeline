SELECT
    RENTAL_DATE                              as rental_date,
    RENTAL_HOUR                              as rental_hour,
    STATION_ID                               as station_id,
    STATION_NAME                             as station_name,

    CASE
        WHEN RENTAL_TYPE = '정기권' THEN 'REGULAR'
        WHEN RENTAL_TYPE = '일일권' THEN 'DAILY'
        ELSE 'OTHER'
    END                                      as rental_type,
    CASE
        WHEN UPPER(GENDER) = 'M' THEN 'M'
        WHEN UPPER(GENDER) = 'F' THEN 'F'
        ELSE 'UNKNOWN'
    END                                      as gender,
    AGE_GROUP                                as age_group,
    USAGE_COUNT                              as usage_count,
    EXERCISE_AMOUNT                          as exercise_amount,
    CARBON_AMOUNT                            as carbon_amount,
    DISTANCE                                 as distance,
    DURATION                                 as duration
FROM {{ source('bike', 'RAW_BIKE_USAGE') }}
WHERE usage_count > 0
    AND duration > 0
    AND distance >= 0