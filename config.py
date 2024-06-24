import logging
from datetime import datetime


# MySQL connection details
mysql_config = {
    'user': 'root',
    'password': 'rootpassword',
    'host': 'localhost',
    'database': 'mydatabase'
}

# PostgreSQL connection details
postgres_config = {
    'user': 'user',
    'password': 'password',
    'host': 'localhost',
    'database': 'mydatabase'
}

oracle_config = {
        'user': 'your_oracle_user',
        'password': 'your_oracle_password',
        'dsn': 'your_oracle_dsn'
    }

sqlserver_config = {
        'user': 'your_sqlserver_user',
        'password': 'your_sqlserver_password',
        'host': 'your_sqlserver_host',
        'database': 'your_sqlserver_database'
    }

def setup_logger():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p')

    # Create file handler with timestamped filename
    current_time = datetime.now().strftime('%d-%m-%Y_%I-%M-%S_%p')
    log_filename = f'logs/logfile_{current_time}.log'
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)

    return logger

def save_ddl_to_file(table_name, source_ddl, target_ddl, source_db_type, target_db_type):
    # Function to save DDL statements to a file
    filename = f"{table_name}_output.sql"

    with open(filename, 'w') as f:
        f.write(f"-- DDL for {table_name} from {source_db_type} to {target_db_type}\n")
        f.write(f"-- Source DDL (from {source_db_type}):\n")
        f.write(f"{source_ddl}\n\n")
        f.write(f"-- Target DDL (to {target_db_type}):\n")
        f.write(f"{target_ddl}\n")