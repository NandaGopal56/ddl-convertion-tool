import json
from config import mysql_config, postgres_config, oracle_config, sqlserver_config, setup_logger, save_ddl_to_file
from psycopg2.extras import DictCursor
import logging

logging.getLogger().addHandler(logging.StreamHandler())
logger = setup_logger()

# Load the data type mappings from the configuration file
with open('datatype_mappings.json', 'r') as file:
    datatype_mappings = json.load(file)['data_type_mappings']

# Define database connection details (replace with your actual connection details)
database_configs = {
    'mysql': mysql_config,
    'postgres': postgres_config,
    'oracle': oracle_config,
    'sqlserver': sqlserver_config
}

def get_connection(db_type):
    if db_type == 'mysql':
        import mysql.connector
        return mysql.connector.connect(**database_configs[db_type])
    elif db_type == 'postgres':
        import psycopg2
        return psycopg2.connect(**database_configs[db_type])
    elif db_type == 'oracle':
        import cx_Oracle
        return cx_Oracle.connect(**database_configs[db_type])
    elif db_type == 'sqlserver':
        import pyodbc
        return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={database_configs[db_type]["host"]};'
            f'DATABASE={database_configs[db_type]["database"]};'
            f'UID={database_configs[db_type]["user"]};'
            f'PWD={database_configs[db_type]["password"]}'
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def get_source_ddl(conn, db_type, table_name):
    if db_type == 'mysql':
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        data = cursor.fetchall()
    elif db_type == 'postgres':
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale,
                   column_default, is_nullable, ordinal_position
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
        """, (table_name))
        data = cursor.fetchall()

    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    cursor.close()
    return data

def get_columns(conn, db_type, table_name, schema_name):
    if db_type == 'mysql':
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE,
                   COLUMN_DEFAULT, IS_NULLABLE, ORDINAL_POSITION
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (schema_name, table_name))
        columns = cursor.fetchall()
    elif db_type == 'postgres':
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale,
                   column_default, is_nullable, ordinal_position
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
        """, (schema_name, table_name))
        columns = cursor.fetchall()
        columns = [{k.upper(): v for k, v in column.items()} for column in columns]
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    cursor.close()
    return columns



def map_data_type(source_db_type, target_db_type, data_type):
    # Convert to lowercase for case insensitivity
    source_db_type = source_db_type.lower()
    target_db_type = target_db_type.lower()
    data_type = data_type.lower()
    
    # Check if the data type exists for the source_db_type in mappings
    if datatype_mappings.get(data_type):
        logger.info(f'MATCH FOUND in json config for the datatype {data_type}: {datatype_mappings.get(data_type)}')
        # Retrieve the dictionary of mappings for the data type
        data_type_mappings = datatype_mappings[data_type]
        
        # Check if the target_db_type exists in the mappings for this data type
        if target_db_type in data_type_mappings:
            logger.info(f'For {data_type} in source, the correspnding datatype in {target_db_type} is {data_type_mappings[target_db_type]}')
            return data_type_mappings[target_db_type]
        else:
            logger.info(f'For {data_type} in source, the correspnding datatype in {target_db_type} not found so returning TEXT')
            # If target_db_type not found, return a default value or handle as needed
            return 'TEXT'  # Default to TEXT if no specific mapping found for target DB type
    else:
        logger.info(f'MATCH NOT FOUND in json config for the datatype {data_type}')
        # If data_type not found in mappings, use custom mapping function
        return custom_map_data_type(source_db_type, target_db_type, data_type)


def custom_map_data_type(source_db_type, target_db_type, mysql_type):
    # Custom fallback mapping function from MySQL to PostgreSQL types
    if source_db_type == 'mysql' and target_db_type == 'postgres':
        if 'int' in mysql_type:
            return 'INTEGER'
        elif mysql_type == 'year':
            return 'INTEGER'
        elif mysql_type.startswith('varchar'):
            return 'VARCHAR(255)'  # Default to VARCHAR with length 255
        elif mysql_type.startswith('char'):
            return 'CHAR(10)'  # Default to CHAR with length 10
        elif mysql_type.startswith('decimal'):
            return 'DECIMAL(10, 2)'  # Default to DECIMAL with precision 10 and scale 2
        elif mysql_type == 'text':
            return 'TEXT'
        elif mysql_type == 'blob':
            return 'BYTEA'  # PostgreSQL BYTEA for BLOB
        else:
            return 'TEXT'  # Default to TEXT for unknown types
    else:
        # Handle other source and target combinations or default to TEXT
        return 'TEXT'

def get_default_value_as_per_database_type(source_db_type, target_db_type, target_data_type, value):
    if source_db_type =='mysql':
        if target_db_type == 'postgres':
            return_value = f"'{value}'"
            logger.info(f'source is : {source_db_type}, target is {target_db_type}: returning value is {return_value}')
            return return_value
    
    if source_db_type == 'postgres':
        if target_db_type == 'mysql':
            return_value = str(value).split('::')[0]
            logger.info(f'source is : {source_db_type}, target is {target_db_type}: returning value is {return_value}')
            return return_value
    
    # default case shuld be as it is. this is error prone. fix it
    logger.info(f'source is : {source_db_type}, target is {target_db_type}: returning value is {str(value)}')
    return str(value)

def generate_create_table_sql(columns, target_conn, source_db_type, target_db_type, table_name):
    # Sort columns by ORDINAL_POSITION
    columns = sorted(columns, key=lambda x: x['ORDINAL_POSITION'])
    
    table_columns = []
    for column in columns:
        logger.info('-'*10)
        logger.info('-'*10)
        logger.info(column)
        col_name = column['COLUMN_NAME']
        data_type = column['DATA_TYPE']
        target_data_type = map_data_type(source_db_type, target_db_type, data_type)
        
        col_def = f"{col_name} {target_data_type}"
        
        if data_type.startswith('varchar'):
            max_length = column['CHARACTER_MAXIMUM_LENGTH']
            col_def = f"{col_name} VARCHAR({max_length})"
        elif data_type == 'decimal':
            precision = column['NUMERIC_PRECISION']
            scale = column['NUMERIC_SCALE']
            col_def = f"{col_name} DECIMAL({precision}, {scale})"
        
        # Handle default value
        default_value = column['COLUMN_DEFAULT']
        if default_value is not None:
            print(data_type)
            # special condition as mysql text type does not support default values
            if target_db_type == 'mysql' and data_type == 'text':
                col_def = col_def.replace('TEXT', 'varchar(255)')

            col_def += f" DEFAULT {get_default_value_as_per_database_type(source_db_type, target_db_type, target_data_type, default_value)}"
        
        # Handle null/not null constraint
        is_nullable = column['IS_NULLABLE']
        if is_nullable == 'NO':
            col_def += " NOT NULL"
        else:
            pass
        
        table_columns.append(col_def)
    
    create_table_sql = (
        "CREATE TABLE " + table_name + "_new" + "(\n"
        "    " + ",\n    ".join(table_columns) + "\n"
        ");"
    )
    
    # try:
    #     cursor = target_conn.cursor()
    #     cursor.execute(create_table_sql)
    #     target_conn.commit()
    #     cursor.close()
    #     logger.info('Sucessfully created the tbale in target database...')
    # except Exception as e:
    #     pass
    #     logger.info('Error creating the table in target database...')
    #     logger.info(e)

    return create_table_sql



def main():

    # Specify source and target database types
    source_db_type = 'postgres'  # Replace with your source database type
    target_db_type = 'mysql'  # Replace with your target database type
    table_name = 'commondatatypes'  # Replace with your table name

    source_db_type = 'mysql'  # Replace with your source database type
    target_db_type = 'postgres'  # Replace with your target database type
    table_name = 'commondatatypes'  # Replace with your table name

    # Define schema mappings based on the database type
    schema_mappings = {
        'mysql': lambda db_config: db_config['database'],
        'postgres': lambda db_config: 'public',
        'oracle': lambda db_config: db_config['schema'],
        'sqlserver': lambda db_config: db_config['schema']
    }

    # Get the schema name based on the source database type
    schema_name = schema_mappings[source_db_type](database_configs[source_db_type])


    # Connect to source and target databases
    source_conn = get_connection(source_db_type)
    target_conn = get_connection(target_db_type)

    # Get columns from source database
    columns = get_columns(source_conn, source_db_type, table_name, schema_name)

    logger.info(f'Extracted columns from source...{columns}')

    # Generate SQL for target database
    create_table_sql_statement = generate_create_table_sql(columns, target_conn, source_db_type, target_db_type, table_name)

    # Output the CREATE TABLE statement
    logger.info(f"{target_db_type.upper()} CREATE TABLE statement:")
    logger.info(create_table_sql_statement)

    # source_DDL is passed as none for now as for postgres, this code is not implemented to get the ddl. 
    save_ddl_to_file(table_name=table_name, source_ddl=None, target_ddl=create_table_sql_statement, source_db_type=source_db_type, target_db_type=target_db_type)

    # Close connections
    source_conn.close()
    target_conn.close()

if __name__ == "__main__":
    main()

