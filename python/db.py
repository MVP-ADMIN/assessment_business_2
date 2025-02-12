import mysql.connector
from mysql.connector import pooling

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'test',
    'password': 'test',
    'database': 'assessment_business',
    'pool_name': 'mypool',
    'pool_size': 5,
    'pool_reset_session': True,
    'buffered': True,
    'charset': 'utf8mb4'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        raise