-- DDL for commondatatypes from postgres to mysql
-- Source DDL (from postgres):
CREATE TABLE commondatatypes (col_tinyint smallint NOT NULL, col_smallint smallint, col_int integer NOT NULL, col_bigint bigint, col_boolean smallint, col_decimal numeric, col_float real NOT NULL, col_double double precision, col_date date, col_datetime timestamp without time zone, col_timestamp timestamp without time zone, col_time time without time zone, col_year integer, col_char character(10), col_varchar character varying(255) NOT NULL, col_binary bytea, col_varbinary bytea, col_blob bytea, col_text text, col_enum character varying(50) NOT NULL, col_set character varying);

-- Target DDL (to mysql):
CREATE TABLE commondatatypes_new(
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
    col_char VARCHAR(10),
    col_varchar VARCHAR(255) NOT NULL,
    col_binary BLOB,
    col_varbinary BLOB,
    col_blob BLOB,
    col_text varchar(255) DEFAULT 'Gopal',
    col_enum VARCHAR(50) DEFAULT 'PwC' NOT NULL,
    col_set VARCHAR(255)
);
