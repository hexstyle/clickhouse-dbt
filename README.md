# clickhouse-otus
Запуск проекта:
```
# docker compose up --build --force-recreate  
```
DAG из OpenMetadata настраивается вручную из интерфейса OpenMetadata
Логин/пароль для OpenMetadata стандартные: admin@open-metadata.org / admin
Прочие пароли в файле .env

Цель созданного примера
1) Демонстрация работы ELT с DBT через Airflow.
   1) [Создание витрины из слоя DDS](dbt/postgres/model/vitrina1_pg.sql)
   2) [Перекладывание в ClickHouse](dbt/clickhouse/model/vitrina1_ch.sql) с [созданием клонированием таблиц без дублирования кода](clickhouse/liquibase/dbobjects/vitrina1.sql)
   3) [Настройка и запуск задания DBT](airflow/dags/fill_vitrina_dag.py)
2) Демонстрация обеспечения консистентности данных при передаче из PostgreSQL в ClickHouse.
   1) [Настройка кластеров ClickHouse](clickhouse/config.xml) c [кластером для записи](clickhouse/write_cluster.xml) и [кластером для чтения](clickhouse/read_cluster.xml) 
   2) [Перекладывание из кластера для чтения в кластер для записи путем клонирования партиций](dbt/clickhouse/macros/sync_partitions.sql)
3) Data observability:
   1) Метаданные и статистика хранилищ. Надо настраивать из интерфейса OpenMetadata вручную. DAG создается автоматом.
   2) Причинно-следственные связи метаданных разных таблиц из слоев DWH/DataMart. TODO: импорт DBT pipeline в OpenMetadata
