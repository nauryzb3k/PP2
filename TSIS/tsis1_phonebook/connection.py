import psycopg2
from config import host, port, database, user, password

def get_connection():
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
    )
        print("Connection successful")
        return conn
    
    except Exception as e:
        print("Error: ", e)
        return None