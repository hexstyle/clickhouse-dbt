{% macro sync_partitions(sync_database, sync_table) %}
    {{ log("📌 Начало синхронизации партиций для " ~ sync_database ~ "." ~ sync_table, info=True) }}

    {# 1. OPTIMIZE TABLE FINAL #}
    {% set optimize_sql %}
    OPTIMIZE TABLE {{ sync_database }}.{{ sync_table }}_write ON CLUSTER write_cluster FINAL;
{% endset %}
    {{ log("📌 Выполняем OPTIMIZE FINAL: " ~ optimize_sql, info=True) }}
    {% do run_query(optimize_sql) %}

    {# 2. Получаем изменённые партиции с прошлого раза #}
    {% set partitions_sql %}
SELECT DISTINCT partition
FROM system.parts
WHERE database = '{{ sync_database }}'
  AND table = '{{ sync_table }}_write'
  AND modification_time > (
    SELECT ifNull(max(sync_time), '1970-01-01 00:00:00')
    FROM {{ sync_database }}.sync_log
    )
    {% endset %}
    {% set partitions_result = safe_run_query(partitions_sql) %}

    {% if partitions_result|length == 0 %}
    {{ log("✅ Нет изменённых партиций. Перенос не требуется.", info=True) }}
    {{ return("SELECT 'Ok'") }}
    {% endif %}

    {# 3. Перебираем найденные партиции и выполняем REPLACE PARTITION #}
    {% for row in partitions_result %}
    {% set part = row['partition'] %}
    {{ log("📌 Обработка партиции: " ~ part, info=True) }}

    {# REPLACE PARTITION #}
    {% set replace_sql %}
ALTER TABLE {{ sync_database }}.{{ sync_table }}
    ON CLUSTER write_cluster REPLACE PARTITION '{{ part }}'
    FROM {{ sync_database }}.{{ sync_table }}_write;
{% endset %}
        {{ log("📌 Выполняем REPLACE PARTITION: " ~ replace_sql, info=True) }}
        {% do run_query(replace_sql) %}

        {# 4. Получаем статистику по партиции #}
        {% set stats_sql %}
SELECT
    partition,
    sum(rows) AS row_count,
    sum(bytes_on_disk) AS size_bytes
FROM system.parts
WHERE database = '{{ sync_database }}'
  AND table = '{{ sync_table }}'
  AND partition = '{{ part }}'
GROUP BY partition;
{% endset %}
        {% set stats_result = safe_run_query(stats_sql) %}
        {% set row_count = stats_result[0]['row_count'] if stats_result|length > 0 else 0 %}
        {% set size_bytes = stats_result[0]['size_bytes'] if stats_result|length > 0 else 0 %}

        {# 5. Логируем результат переноса в sync_log #}
        {% set log_sql %}
        INSERT INTO {{ sync_database }}.sync_log (partition, sync_time, row_count, size_bytes, error_message, error_time)
        VALUES ('{{ part }}', now(), {{ row_count }}, {{ size_bytes }}, '', now());
{% endset %}
        {{ log("📌 Записываем в sync_log: " ~ log_sql, info=True) }}
        {% do run_query(log_sql) %}
    {% endfor %}

    {{ log("✅ Синхронизированы следующие партиции: " ~ partitions_result | map(attribute='partition') | join(', '), info=True) }}
    {{ return("SELECT 'Ok'") }}
{% endmacro %}
