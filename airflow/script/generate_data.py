import random
import string
import psycopg2
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Параметры подключения к Postgres
POSTGRES_HOST = 'postgres'
POSTGRES_DB   = 'dwh'  # Или какая у вас БД
POSTGRES_USER = 'user'
POSTGRES_PASS = 'password'
POSTGRES_PORT = 5432

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0
}

def generate_random_data():
    """
    Генерирует случайные записи и вставляет их в три таблицы:
    dislocation, car_passport, fact_load.
    """

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASS
    )
    conn.autocommit = False  # используем транзакции
    cur = conn.cursor()

    # Случайно определяем, сколько записей сгенерим сейчас (до 50К).
    batch_size = random.randint(1, 50000)

    for _ in range(batch_size):
        # 1) Генерируем случайные поля
        car_number = str(random.randint(10000, 99000))

        # Генерируем date_from в прошлом
        now_ts = datetime.now()
        # date_from от '2025-01-01' до текущего момента
        # для простоты берём randint между start_date (фиксируем её как 2025-01-01) и now()
        start_date_limit = datetime(2025, 1, 1)
        total_secs = int((now_ts - start_date_limit).total_seconds())
        rand_offset_secs = random.randint(0, max(0, total_secs))  # неотрицательный
        date_from = start_date_limit + timedelta(seconds=rand_offset_secs)

        # Генерируем date_to > date_from
        # Но если случайно выйдем за now(), ставим '9999-12-31 23:59:59'
        time_delta = random.randint(0, 3600 * 24 * 30)  # до 30 дней
        raw_date_to = date_from + timedelta(seconds=time_delta)
        if raw_date_to > now_ts:
            date_to = datetime(9999, 12, 31, 23, 59, 59)
        else:
            date_to = raw_date_to

        # Случайные поля для таблиц
        station       = str(random.randint(1, 20000))
        station_from  = str(random.randint(1, 20000))
        operation     = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
        car_model     = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        price         = round(random.uniform(1000, 999999), 2)
        cargo         = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

        # 2) Выбираем таблицу, куда вставим (случайным образом)
        #    (Или можете вставлять во все таблицы сразу — зависит от бизнес-логики).
        table_choice = random.choice(['dislocation', 'car_passport', 'fact_load'])

        # 3) "Подрезаем" пересекающийся интервал (для той же car_number)
        #    Если у нас EXCLUDE USING GIST(...), то Postgres выбросит ошибку
        #    при пересечении. Мы вручную "обрезаем" существующую запись.
        #    Для упрощения меняем date_to у всех пересекающихся записей.
        check_overlap_sql = f"""
            SELECT id, date_from, date_to 
            FROM {table_choice}
            WHERE car_number = %s
              AND tsrange(date_from, date_to) && tsrange(%s, %s)
        """
        cur.execute(check_overlap_sql, (car_number, date_from, date_to))
        rows = cur.fetchall()
        for r in rows:
            old_id, old_from, old_to = r
            # "Подрезаем" существующую запись так, чтобы её date_to = new_date_from
            update_sql = f"""
                UPDATE {table_choice}
                   SET date_to = %s
                 WHERE id = %s
            """
            cur.execute(update_sql, (date_from, old_id))

        # 4) Вставляем новую запись.
        if table_choice == 'dislocation':
            insert_sql = f"""
                INSERT INTO dislocation (car_number, date_from, date_to, operation, station)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (car_number, date_from, date_to, operation, station))

        elif table_choice == 'car_passport':
            insert_sql = f"""
                INSERT INTO car_passport (car_number, date_from, date_to, car_model)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_sql, (car_number, date_from, date_to, car_model))

        else:  # 'fact_load'
            insert_sql = f"""
                INSERT INTO fact_load (car_number, date_from, date_to, price, station_from, cargo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (car_number, date_from, date_to, price, station_from, cargo))

    conn.commit()
    cur.close()
    conn.close()
