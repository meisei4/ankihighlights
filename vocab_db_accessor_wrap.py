import typing
import logging
import datetime
from contextlib import closing
from sqlite3 import Connection


# TODO This whole module needs a Exception handling refactoring
#   majority of the errors i get during tests are related to trying to access a connection to the database or during an access
#   Idea:
#   first provide some way of making a connection here (never call sqlite3.connect(file) on its own without using this module
#   make sure that this module can support multiple connections to the same database file (as long as locks and stuff work?)
#   make sure it also includes file access error Exception handling, missing table errors, and all other errors thrown upwards
#   this way errors will be controlled and handled at the connection leve rather than randomly causing tests to hang


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)
_latest_timestamp: int = -1


def check_and_create_latest_timestamp_table_if_not_exists(connection_injection: Connection) -> None:
    query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='latest_timestamp'
    """
    table_exists = execute_query(connection_injection, query)
    if not table_exists:
        query = """
            CREATE TABLE latest_timestamp (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER
            )
        """
        execute_query(connection_injection, query)
        logger.info("Table 'latest_timestamp' created.")
    else:
        logger.info("Table 'latest_timestamp' already exists.")


def get_word_lookups_after_timestamp(connection_injection: Connection, timestamp: int) -> list[dict]:
    with connection_injection:
        query = f"""
            SELECT LOOKUPS.id, WORDS.word, LOOKUPS.usage, LOOKUPS.timestamp, BOOK_INFO.title, BOOK_INFO.authors
            FROM LOOKUPS 
            JOIN WORDS ON LOOKUPS.word_key = WORDS.id 
            JOIN BOOK_INFO ON LOOKUPS.book_key = BOOK_INFO.id 
            WHERE LOOKUPS.timestamp > {timestamp}
        """
        return execute_query(connection_injection, query)


def get_latest_lookup_timestamp(connection_injection: Connection) -> int:
    with connection_injection:
        query = "SELECT MAX(timestamp) AS timestamp FROM LOOKUPS"
        return execute_query(connection_injection, query)[0]['timestamp']


# TODO the new fixture update in conftest is removing the db at the module scope so this is no longer working,
def set_latest_timestamp(connection_injection: Connection, timestamp: int) -> list[dict]:
    query = f"""
        INSERT INTO latest_timestamp (id, timestamp) 
        VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM latest_timestamp), {timestamp})
    """
    return execute_query(connection_injection, query)


def get_latest_timestamp(connection_injection: Connection) -> typing.Optional:
    query = "SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1"
    rows = execute_query(connection_injection, query)
    if rows:
        return rows[0]['timestamp']
    return None


def execute_query(connection: Connection, query: str) -> list[dict]:
    with closing(connection.cursor()) as cursor:
        logger.debug(f"Executing query: {query}")
        cursor.execute(query)

        if cursor.description is None:
            logger.debug("Query results: None")
            return []

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        logger.debug(f"Query results: {results}")
        connection.commit()
        return results


# AUXILIARIES
def get_table_info(db_connection_injection: Connection) -> dict:
    table_info = {}
    with db_connection_injection:
        cursor = db_connection_injection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            table_columns = {}
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[1]
                data_type = column[2]
                table_columns[column_name] = data_type

            table_info[table_name] = table_columns

    return table_info


def ordinal_suffix(count: int) -> str:
    if 11 <= count <= 13:
        return "th"
    elif count % 10 == 1:
        return "st"
    elif count % 10 == 2:
        return "nd"
    elif count % 10 == 3:
        return "rd"
    else:
        return "th"


def get_timestamp_ms(year, month, day):
    dt = datetime.datetime(year=year, month=month, day=day)
    return int(dt.timestamp() * 1000)
