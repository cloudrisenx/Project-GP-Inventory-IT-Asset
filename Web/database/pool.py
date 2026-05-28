import psycopg2
from psycopg2 import pool
from config import Config
import logging

logger = logging.getLogger(__name__)
_connection_pool = None

def init_pool():
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                Config.DB_POOL_MINCONN,
                Config.DB_POOL_MAXCONN,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            logger.info("Database connection pool created successfully.")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise e

def get_db_connection():
    if _connection_pool is None:
        init_pool()
    try:
        conn = _connection_pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}")
        return None

def release_db_connection(conn):
    if _connection_pool and conn:
        try:
            _connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error releasing connection to pool: {e}")

def close_pool():
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        logger.info("Database connection pool closed.")
