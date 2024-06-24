-- DDL for commondatatypes from mysql to postgres
-- Source DDL (from mysql):
None

-- Target DDL (to postgres):
CREATE TABLE commondatatypes_new(
    col_tinyint SMALLINT NOT NULL,
    col_smallint SMALLINT,
    col_int INTEGER DEFAULT '45' NOT NULL,
    col_bigint BIGINT,
    col_boolean SMALLINT,
    col_decimal DECIMAL(10, 0),
    col_float DOUBLE PRECISION NOT NULL,
    col_double DOUBLE PRECISION,
    col_date DATE,
    col_datetime TIMESTAMP DEFAULT '2024-12-31 00:00:00',
    col_timestamp TIMESTAMP DEFAULT '2024-12-31 12:00:00',
    col_time TIME,
    col_year INTEGER,
    col_char TEXT,
    col_varchar VARCHAR(255) NOT NULL,
    col_binary BYTEA,
    col_varbinary BYTEA,
    col_blob BYTEA,
    col_text VARCHAR(255) DEFAULT 'Gopal',
    col_enum VARCHAR(255) DEFAULT 'PwC' NOT NULL,
    col_set VARCHAR(255)
);
