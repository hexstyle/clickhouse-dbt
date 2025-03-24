{% macro safe_run_query(query) %}
    {{ log("Executing query: " ~ query, info=True) }}
    {% set result = run_query(query) %}
    {{ return(result) }}
{% endmacro %}
