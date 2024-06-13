-- DDL for CommonDataTypes from mysql to postgres
-- Source DDL (from mysql):
None

-- Target DDL (to postgres):
CREATE TABLE CommonDataTypes (
    col_tinyint SMALLINT DEFAULT '1'::SMALLINT NOT NULL,
    col_smallint SMALLINT NULL,
    col_int INTEGER NULL,
    col_bigint BIGINT NULL,
    col_boolean SMALLINT NULL,
    col_decimal DECIMAL(10, 2) NULL,
    col_float REAL NOT NULL,
    col_double DOUBLE PRECISION NULL,
    col_date DATE DEFAULT '2024-12-31'::DATE NULL,
    col_datetime TIMESTAMP NULL,
    col_timestamp TIMESTAMP NULL,
    col_time TIME NULL,
    col_year INTEGER NULL,
    col_char CHARACTER DEFAULT 'NGP'::CHARACTER NULL,
    col_varchar VARCHAR(255) DEFAULT 'GOPAL'::CHARACTER VARYING NOT NULL,
    col_binary BYTEA NULL,
    col_varbinary BYTEA NULL,
    col_blob BYTEA NULL,
    col_text TEXT NULL,
    col_enum VARCHAR NULL,
    col_set VARCHAR NULL
);
