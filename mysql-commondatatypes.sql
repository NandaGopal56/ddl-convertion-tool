-- Active: 1718298846625@@13.232.200.186@3306@mydatabase
-- Get columns information
SELECT *
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'mydatabase' AND TABLE_NAME = 'CommonDataTypes';

-- Get table information
SELECT *
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'mydatabase' AND TABLE_NAME = 'CommonDataTypes';

drop table commondatatypes


-- Generated by the database client.
CREATE TABLE commondatatypes(
     col_tinyint SMALLINT NOT NULL,
    col_smallint SMALLINT,
    col_int INT DEFAULT 45 NOT NULL,
    col_bigint BIGINT,
    col_boolean SMALLINT,
    col_decimal NUMERIC,
    col_float REAL NOT NULL,
    col_double DOUBLE,
    col_date DATE,
    col_datetime TIMESTAMP DEFAULT '2024-12-31 00:00:00',
    col_timestamp TIMESTAMP DEFAULT '2024-12-31 12:00:00',
    col_time TIME,
    col_year INT,
    col_char TEXT,
    col_varchar VARCHAR(255) NOT NULL,
    col_binary BLOB,
    col_varbinary BLOB,
    col_blob BLOB,
    col_text varchar(255) DEFAULT 'Gopal',
    col_enum VARCHAR(255) DEFAULT 'PwC' NOT NULL,
    col_set VARCHAR(255)
);