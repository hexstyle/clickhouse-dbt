--liquibase formatted sql
--changeset system:online_reporting.vitrina1 stripComments:false splitStatements:false context:casual runAlways:false runOnChange:true failOnError:true

CREATE TABLE IF NOT EXISTS online_reporting.vitrina1 ON CLUSTER 'global_cluster'
(
    car_number String,
    report_date DateTime,
    operation String,
    station String,
    car_model String,
    price Decimal(18,2),
    station_from String,
    cargo String
    )
    ENGINE = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/vitrina1', '{cluster}{replica}')
    PARTITION BY toYYYYMMDD(report_date)
    ORDER BY (car_number);
/*
-- dbt все равно создаст, но это как пример, с возможностью переопределения схемы в клике без участия dbt
-- в таком случае в модели dbt указываем ветку {% if is_incremental() %} скрипт обновления {% else %} скрипт добавления {% endif %}
 */
