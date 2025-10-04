import psycopg2
import pandas as pd

DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'cine_dw',
    'user': 'dw_admin',
    'password': 'dw_pass_2024'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def query_to_df(query):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
