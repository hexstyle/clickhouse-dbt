--liquibase formatted sql
--changeset system:online_reporting.sync_log stripComments:false splitStatements:false context:casual runAlways:false runOnChange:true failOnError:true

CREATE TABLE online_reporting.sync_log ON CLUSTER 'write_cluster'
(
    partition String,         -- Название партиции (например, '202402')
    sync_time DateTime DEFAULT now(),  -- Время успешной синхронизации
    row_count UInt64,         -- Количество записей в партиции
    size_bytes UInt64,        -- Размер партиции в байтах
    error_message String,     -- Текст ошибки (если есть)
    error_time DateTime DEFAULT now()  -- Время последней ошибки
)
    ENGINE = MergeTree()
ORDER BY (sync_time, partition);