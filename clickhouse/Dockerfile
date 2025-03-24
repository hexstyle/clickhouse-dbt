FROM clickhouse/clickhouse-server:25.1.5 

ARG CLICKHOUSE_SERVER_ID
ARG CLICKHOUSE_WRITE_PASSWORD
ARG CLICKHOUSE_READ_PASSWORD

ENV CLICKHOUSE_SERVER_ID=${CLICKHOUSE_SERVER_ID}
ENV CLICKHOUSE_WRITE_PASSWORD=${CLICKHOUSE_WRITE_PASSWORD}
ENV CLICKHOUSE_READ_PASSWORD=${CLICKHOUSE_READ_PASSWORD}

RUN apt-get update && apt-get install -y gettext-base curl openssh-server openssh-client rsync netcat gosu  && rm -rf /var/lib/apt/lists/*


# Разрешаем root-доступ по SSH (для автоматического входа без пароля)
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

# Создаём каталог для SSH-ключей и настраиваем права
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
# копируем готовые ключи
COPY .ssh/id_rsa /root/.ssh/id_rsa
COPY .ssh/id_rsa.pub /root/.ssh/id_rsa.pub
COPY .ssh/authorized_keys /root/.ssh/authorized_keys

RUN chmod 600 /root/.ssh/id_rsa \
    && chmod 600 /root/.ssh/authorized_keys \
    && chmod 644 /root/.ssh/id_rsa.pub
# Генерируем SSH-ключи
#RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" \
#    && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \

COPY config.xml /etc/clickhouse-server/config.d/config.xml.template
RUN envsubst < /etc/clickhouse-server/config.d/config.xml.template > /etc/clickhouse-server/config.d/config.xml
RUN rm -rf /etc/clickhouse-server/config.d/config.xml.template

COPY users.xml /etc/clickhouse-server/users.d/users.xml.template
RUN envsubst < /etc/clickhouse-server/users.d/users.xml.template > /etc/clickhouse-server/users.d/users.xml
RUN rm -rf /etc/clickhouse-server/users.d/users.xml.template


EXPOSE 22
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
