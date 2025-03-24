FROM apache/airflow:2.10.5

USER root

RUN apt-get update && apt-get install -y curl wget rsync \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    build-essential zlib1g-dev  \
    libncurses5-dev libgdbm-dev  \
    libnss3-dev libreadline-dev  \
    libsqlite3-dev wget libbz2-dev \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y git && \
    apt-get clean 
    
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


USER airflow
# Обновляем PATH, чтобы включить директорию с пользовательскими бинарниками pip
ENV PATH=/home/airflow/.local/bin:$PATH
# Устанавливаем dbt (это установит пакет в домашнюю директорию airflow)
RUN pip install dbt-core dbt-postgres dbt-clickhouse

# Ставим все необходимо для интеграции с OpenMetadata
RUN pip install "openmetadata-ingestion[clickhouse]==1.6.5" \
    "openmetadata-ingestion[postgres]==1.6.5" \
    "openmetadata-ingestion[dbt]==1.6.5" \
    "openmetadata-managed-apis==1.6.5"



ENTRYPOINT ["/entrypoint.sh"]
