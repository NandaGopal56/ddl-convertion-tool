import json
from config import mysql_config, postgres_config, oracle_config, sqlserver_config
from psycopg2.extras import DictCursor

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
    
def get_columns(conn, db_type, table_name, schema_name):
    # Retrieve column information from the database
    

    if db_type == 'mysql':
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (schema_name, table_name))

    elif db_type == 'postgres':
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
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
    # Map data type based on the source and target database types
    if source_db_type in datatype_mappings and data_type in datatype_mappings[source_db_type]:
        return datatype_mappings[source_db_type][data_type].get(target_db_type, 'TEXT')
    else:
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


def generate_create_table_sql(columns, target_conn, target_db_type):
    # Generate SQL to create table based on target database type
    table_columns = []
    for column in columns:
        print(column)
        col_name = column['COLUMN_NAME']
        data_type = column['DATA_TYPE']

        # Map data type to target database type
        target_data_type = map_data_type('mysql', target_db_type, data_type)

        # Handle specific cases for length, precision, scale, etc.
        if data_type.startswith('varchar'):
            max_length = column['CHARACTER_MAXIMUM_LENGTH']
            target_data_type = f"VARCHAR({max_length})"
        elif data_type == 'decimal':
            precision = column['NUMERIC_PRECISION']
            scale = column['NUMERIC_SCALE']
            target_data_type = f"DECIMAL({precision}, {scale})"

        table_columns.append(f"{col_name} {target_data_type}")

    # Create the SQL statement using regular string concatenation
    create_table_sql = (
        "CREATE TABLE CommonDataTypes (\n"
        "    " + ",\n    ".join(table_columns) + "\n"
        ");"
    )

    # Execute the SQL to create table in the target database
    # cursor = target_conn.cursor()
    # cursor.execute(create_table_sql)
    # target_conn.commit()
    # cursor.close()

    return create_table_sql


def main():
    # Specify source and target database types
    source_db_type = 'postgres'  # Replace with your source database type
    target_db_type = 'mysql'  # Replace with your target database type
    table_name = 'commondatatypes'  # Replace with your table name

    # source_db_type = 'mysql'  # Replace with your source database type
    # target_db_type = 'postgres'  # Replace with your target database type
    # table_name = 'CommonDataTypes'  # Replace with your table name

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

    # Generate SQL for target database
    create_table_sql_statement = generate_create_table_sql(columns, target_conn, target_db_type)

    # Output the CREATE TABLE statement
    print(f"{target_db_type.upper()} CREATE TABLE statement:")
    print(create_table_sql_statement)

    # Close connections
    source_conn.close()
    target_conn.close()

if __name__ == "__main__":
    main()

