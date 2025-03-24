#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
    sleep 2
done

echo "Initializing Airflow database..."
airflow db init

echo "Creating admin user..."
# Попытка создать администратора, если пользователь уже существует – не прерывает выполнение
airflow users create \
  --username "${AIRFLOW_ADMIN_USERNAME}" \
  --firstname "Admin" \
  --lastname "User" \
  --role Admin \
  --email "${AIRFLOW_ADMIN_EMAIL}" \
  --password "${AIRFLOW_ADMIN_PASSWORD}" || true

echo "Starting command: $@"
exec "$@"
