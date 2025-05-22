import psycopg2
import logging

class DatabaseConnection:
    _instance = None
    _connection = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_connection(self, config):
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    dbname=config["db_connection"]["dbname"],
                    user=config["db_connection"]["user"],
                    password=config["db_connection"]["password"],
                    host=config["db_connection"]["host"],
                    port=config["db_connection"]["port"],
                )
            except Exception as e:
                logging.error(f"Error connecting to database: {str(e)}")
                raise
        return self._connection

    def close_connection(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None 