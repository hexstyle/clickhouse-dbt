-- Создание таблиц справочников
CREATE TABLE IF NOT EXISTS sp_station (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(30)
    );
CREATE TABLE IF NOT EXISTS car (
    code VARCHAR(10) PRIMARY KEY
    );
CREATE TABLE IF NOT EXISTS sp_etsng_cargo (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(30)
    );
CREATE TABLE IF NOT EXISTS sp_car_operation (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(30)
    );

--уникальный gits индекс по датам
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Создание основных таблиц с уникальностью по car_number в пределах диапазонов дат
CREATE TABLE IF NOT EXISTS dislocation (
    id bigint GENERATED ALWAYS AS IDENTITY,
    car_number VARCHAR(10),
    date_from TIMESTAMP,
    date_to TIMESTAMP,
    operation VARCHAR(3),
    station VARCHAR(10),
    PRIMARY KEY (car_number, date_from),
    EXCLUDE USING GIST (
        car_number WITH =,
        tsrange(date_from, date_to) WITH &&
        )
    ); 
CREATE TABLE IF NOT EXISTS car_passport (
    id bigint GENERATED ALWAYS AS IDENTITY,
    car_number VARCHAR(10),
    date_from TIMESTAMP,
    date_to TIMESTAMP,
    car_model VARCHAR(10),
    PRIMARY KEY (car_number, date_from),
    EXCLUDE USING GIST (
        car_number WITH =,
        tsrange(date_from, date_to) WITH &&
        )
    );
CREATE TABLE IF NOT EXISTS fact_load (
    id bigint GENERATED ALWAYS AS IDENTITY,
    car_number VARCHAR(10),
    date_from TIMESTAMP,
    date_to TIMESTAMP,
    price DECIMAL(18,2),
    station_from VARCHAR(10),
    station_to VARCHAR(10),
    cargo VARCHAR(10),
    PRIMARY KEY (car_number, date_from),
    EXCLUDE USING GIST (
        car_number WITH =,
        tsrange(date_from, date_to) WITH &&
        )
    );


CREATE USER airuser WITH PASSWORD 'airpass';
CREATE DATABASE airflow_db WITH OWNER airuser;

CREATE DATABASE openmetadata_db WITH OWNER 'user';
