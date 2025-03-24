{{ config(
    materialized='incremental',
    alias='vitrina1',
    unique_key=['report_date_date', 'car_number']
) }}

WITH
    dislocation_data AS (
        SELECT
            car_number,
            date_from,
            date_to,
            operation,
            station
        FROM {{ source('postgres', 'dislocation') }}
        WHERE now() BETWEEN date_from AND date_to
    ),
    passport_data AS (
        SELECT
            car_number,
            date_from,
            date_to,
            car_model
        FROM {{ source('postgres', 'car_passport') }}
        WHERE now() BETWEEN date_from AND date_to
    ),
    fact_load_data AS (
        SELECT
            car_number,
            date_from,
            date_to,
            price,
            station_from,
            cargo
        FROM {{ source('postgres', 'fact_load') }}
        WHERE now() BETWEEN date_from AND date_to
    )

SELECT
    d.car_number,
    now() AS report_date,
    CAST(now() AS DATE) AS report_date_date,
    d.operation,
    d.station,
    cp.car_model,
    fl.price,
    fl.station_from,
    fl.cargo
FROM dislocation_data d
         LEFT JOIN passport_data cp ON d.car_number = cp.car_number
         LEFT JOIN fact_load_data fl ON d.car_number = fl.car_number
WHERE d.car_number IS NOT NULL

