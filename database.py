import psycopg2
from config import DB_CONFIG


def get_connection():
    """
    Creates and returns a PostgreSQL database connection.
    """

    conn = psycopg2.connect(**DB_CONFIG)

    return conn