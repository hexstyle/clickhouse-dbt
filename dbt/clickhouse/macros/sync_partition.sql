{{ log("Измененные партиции: " ~ changed_partitions | join(', '), info=True) }}

{% macro sync_partition(partition, table, database) %}
    {% do log('Starting FREEZE PARTITION on clickhouse1', info=True) %}

    -- Выполняем команду FREEZE PARTITION на clickhouse1
    {% set freeze_query %}
ALTER TABLE {{ database }}.{{ table }}_write FREEZE PARTITION '{{ partition }}' WITH NAME '{{ table }}_{{ partition }}';
{% endset %}

    {% do run_query(freeze_query) %}

    {% do log('Partition frozen. Now syncing data to clickhouse2...', info=True) %}

    -- Определяем путь к замороженной партиции
    {% set freeze_path = '/var/lib/clickhouse/shadow/{{ table }}_{{ partition }}/' %}
    
    -- Выполняем rsync через run_query()
    {% set rsync_sql %}
    SYSTEM system(rsync -avz clickhouse1:{{ freeze_path }} clickhouse2:/var/lib/clickhouse/shadow/)
    {% endset %}

    {% do log("Executing rsync: " ~ rsync_sql, info=True) %}
    {% do run_query(rsync_sql) %}

    {% do log('Partition synced successfully to clickhouse2! Now extracting...', info=True) %}

    -- Разархивируем партицию в store/
    {% set extract_sql %}
    SYSTEM system(ssh clickhouse2 "sudo mv /var/lib/clickhouse/shadow/{{ table }}_{{ partition }}/* /var/lib/clickhouse/store/")
    {% endset %}

    {% do log("Executing mv: " ~ extract_sql, info=True) %}
    {% do run_query(extract_sql) %}


    {% do log('Partition extracted successfully! Now attaching...', info=True) %}

    -- Подключаем партицию на clickhouse2
    {% set attach_query %}
ALTER TABLE {{ database }}.{{ table }} ON CLUSTER read_cluster ATTACH PARTITION '{{ partition }}';
{% endset %}

    {% do run_query(attach_query) %}

    {% do log('Partition successfully attached to {{ table }} on clickhouse2!', info=True) %}
    {{ return('ok') }}
{% endmacro %}
