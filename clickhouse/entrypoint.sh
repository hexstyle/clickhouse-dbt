#!/bin/bash
set -e

# Запускаем SSH-сервер
service ssh start

for server in clickhouse1 clickhouse2 clickhouse3; do
    ssh-keyscan $server >> /root/.ssh/known_hosts 2>/dev/null
done

# Проверяем, существует ли директория /run/clickhouse
if [ ! -d "/run/clickhouse" ]; then
    echo "🔹 Creating /run/clickhouse directory..."
    mkdir -p /run/clickhouse
    chmod 755 /run/clickhouse
fi


# Проверяем права на директорию с данными ClickHouse
chown -R clickhouse:clickhouse /var/lib/clickhouse /var/log/clickhouse-server

echo "Запускаем под пользователем clickhouse"
exec gosu clickhouse clickhouse-server --config-file=/etc/clickhouse-server/config.xml
