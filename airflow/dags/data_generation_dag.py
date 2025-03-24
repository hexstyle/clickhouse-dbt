import random
import string
import psycopg2
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Параметры подключения к Postgres
POSTGRES_HOST = 'postgres'
POSTGRES_DB   = 'dwh'  # Или ваша база
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
    Генерирует до 50k случайных записей в одну из трёх таблиц (dislocation, car_passport, fact_load).
    При этом обрабатываем пересечения интервалов так, чтобы избежать ошибки:
    'range lower bound must be less than or equal to range upper bound'.
    """

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASS
    )
    conn.autocommit = False  # используем транзакцию
    cur = conn.cursor()

    batch_size = random.randint(1, 50000)  # Сколько строк сгенерировать за один запуск

    for _ in range(batch_size):
        car_number = str(random.randint(10000, 99000))

        now_ts = datetime.now()
        start_date_limit = datetime(2025, 1, 1)
        total_secs = int((now_ts - start_date_limit).total_seconds())

        rand_offset_secs = random.randint(0, max(0, total_secs))
        date_from = start_date_limit + timedelta(seconds=rand_offset_secs)

        # Генерируем date_to, которое может быть до 30 дней после date_from
        time_delta = random.randint(0, 3600 * 24 * 30)
        raw_date_to = date_from + timedelta(seconds=time_delta)
        if raw_date_to > now_ts:
            # Если выходим за текущее время, ставим верхнюю границу "максимальную"
            date_to = datetime(9999, 12, 31, 23, 59, 59)
        else:
            date_to = raw_date_to

        station       = str(random.randint(1, 20000))
        station_from  = str(random.randint(1, 20000))
        operation     = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
        car_model     = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        price         = round(random.uniform(1000, 999999), 2)
        cargo         = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

        table_choice = random.choice(['dislocation', 'car_passport', 'fact_load'])

        # Ищем пересекающиеся записи
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
            # Рассматриваем три случая:
            # 1) Если new_date_from <= old_from, значит новая запись начинается раньше или ровно с existing-отрезком
            #    - для упрощения "убираем" старую запись (можно и по-другому).
            if date_from <= old_from:
                delete_sql = f"DELETE FROM {table_choice} WHERE id = %s"
                cur.execute(delete_sql, (old_id,))
            # 2) Если new_date_from >= old_to, тогда нет реального пересечения (только соприкосновение или вообще не пересекается).
            #    - ничего не делаем.
            elif date_from >= old_to:
                pass
            # 3) В противном случае (old_from < new_date_from < old_to), подрезаем старую запись:
            else:
                update_sql = f"UPDATE {table_choice} SET date_to = %s WHERE id = %s"
                cur.execute(update_sql, (date_from, old_id))

        # Теперь вставляем новую запись
        if table_choice == 'dislocation':
            insert_sql = """
                INSERT INTO dislocation (car_number, date_from, date_to, operation, station)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (car_number, date_from, date_to, operation, station))

        elif table_choice == 'car_passport':
            insert_sql = """
                INSERT INTO car_passport (car_number, date_from, date_to, car_model)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_sql, (car_number, date_from, date_to, car_model))

        else:  # fact_load
            insert_sql = """
                INSERT INTO fact_load (car_number, date_from, date_to, price, station_from, cargo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (car_number, date_from, date_to, price, station_from, cargo))

    conn.commit()
    cur.close()
    conn.close()


with DAG(
        dag_id='data_generation_dag',
        default_args=default_args,
        schedule_interval=timedelta(seconds=5),  # каждые 5 секунд
        catchup=False,
        max_active_runs=1
) as dag:

    generate_task = PythonOperator(
        task_id='generate_data_task',
        python_callable=generate_random_data
    )

    generate_task
