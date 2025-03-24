{{ config(
    materialized='incremental',
    incremental_strategy='append',
    database='online_reporting',
    alias='vitrina1_write',
    engine="ReplacingMergeTree()",
    order_by='(car_number)',
    partition_by="toYYYYMMDD(report_date)",
    on_cluster='write_cluster',
    post_hook=[
      "{% if execute %} {{ sync_partitions('online_reporting','vitrina1') }} {% endif %}"
    ]
) }}

SELECT
    car_number,
    report_date_date as report_date,
    operation,
    station,
    car_model,
    price,
    station_from,
    cargo
{% if is_incremental() %}
FROM postgresql('postgres:5432','dwh','vitrina1',
    '{{ env_var("POSTGRES_USER") }}','{{ env_var("POSTGRES_PASSWORD") }}')
{% else %}
FROM cluster('read_cluster',online_reporting.vitrina1) 
{% endif %}
WHERE car_number IS NOT NULL