""" Built-in modules """
import logging
import sqlite3
import sys
import time


class DbConnectionHandler:
    """ Acts as custom context manager for easy integrated management of database connections. """
    def __init__(self, db_name):
        """
        Database connection initializer.

        :param db_name:  The string name of the database to be connected to.
        """
        # Set db instance variables #
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)

    def __enter__(self):
        """
        Method for managing what is returned into the context manager as proxy variable(connection).

        :return:  Context instance to be returned to connection variable in context manager.
        """
        # Return the context to the context manager #
        return self.connection

    def __exit__(self, exc_type, exc_val, traceback):
        """
        Method for handling the events that occurs when exiting context manager.

        :param exc_type:  The exception type.
        :param exc_val:  The exception value.
        :param traceback:  Exception traceback occurrence in stack.
        """
        # Close db connection on context manager exit #
        self.connection.close()


def query_handler(connection, query, *args, exec_script=None, fetch=None):
    """
    Database handler to handler various db calls with session locking and error handling.

    :param connection:  The protected database connection to be interacted with.
    :param query:  The query to be executed in the accessed database.
    :param args:  Takes variable length arguments to pass as database parameters.
    :param exec_script:  If set to True, runs executescript instead of execute.
    :param fetch:  If set to one, fetchone is returned. If set to all, fetchall is returned.
    :return:  If fetching data, the fetched data is returned. Otherwise, None.
    """
    # If the passed in MySQL query was not a complete statement #
    if not sqlite3.complete_statement(query):
        logging.error('Passed in query is not a complete MySQL statement: %s\n\n', query)
        print_err(f'Passed in query is not a complete MySQL statement: {query}', None)
        sys.exit(3)

    # Connection context manager auto-handles commits/rollbacks #
    with connection:
        # If query is one-liner #
        if not exec_script:
            # If no args to be parsed into query #
            if not args:
                # Execute SQL query #
                db_call = connection.execute(query)
            # If args are to be parsed into query #
            else:
                # Execute SQL query #
                db_call = connection.execute(query, args)

        # If query is multi-liner script #
        else:
            # Execute SQL script #
            db_call = connection.executescript(query)

        # If the fetch flag is set to "one" #
        if fetch == 'one':
            # Return fetched row #
            return db_call.fetchone()

        # If the fetch flag is set to "all" #
        elif fetch == 'all':
            # Return all fetched rows #
            return db_call.fetchall()

        # If the fetch flag is at default "None" #
        elif not fetch:
            return None

        # If the fetch flag has been set to unknown value #
        else:
            logging.error('Fetch flag is set to unexpected value: %s\n\n', fetch)
            print_err(f'Fetch flag is set to unexpected value: {fetch}', None)
            sys.exit(4)


def db_error_query(db_error):
    """
    Looks up the exact error raised by database error catch-all handler.

    :param db_error:  The database error that occurred to be looked-up.
    :return:  Nothing
    """
    # If query is not a string or multiple queries are passed to execute() #
    if db_error == sqlite3.Warning:
        logging.warning('Db sqlite3 warning: %s\n\n', db_error)
        print_err(f'Db sqlite warning: {db_error}', None)

    # If error occurs during fetch across rollback or is unable to bind parameters #
    elif db_error == sqlite3.InterfaceError:
        logging.error('Db interface error: %s\n\n', db_error)
        print_err(f'Db interface error: {db_error}', None)

    # If data-related error occurs, such as number out of range and overflowed strings #
    elif db_error == sqlite3.DataError:
        logging.error('Db data-related error: %s\n\n', db_error)
        print_err(f'Db data-related error: {db_error}', None)

    # If database operation error occurs, such as a database path not being found or the failed
    # processing of a transaction #
    elif db_error == sqlite3.OperationalError:
        logging.error('Db operational error: %s\n\n', db_error)
        print_err(f'Db operational error: {db_error}', None)

    # If database relational integrity is affected #
    elif db_error == sqlite3.IntegrityError:
        logging.error('Db relational integrity error: %s\n\n', db_error)
        print_err(f'Db relational integrity error: {db_error}', None)

    # If sqlite3 internal error occurs, suggesting a potential runtime library issue #
    elif db_error == sqlite3.InternalError:
        logging.error('Db sqlite3 internal runtime error: %s\n\n', db_error)
        print_err(f'Db sqlite3 internal runtime error: {db_error}', None)

    # If sqlite3 API error occurs, such as trying to operate on a closed connection #
    elif db_error == sqlite3.ProgrammingError:
        logging.error('Db sqlite3 APi operational error: %s\n\n', db_error)
        print_err(f'Db sqlite3 API operational error: {db_error}', None)

    # If a called API method is not supported by the underlying SQLite3 runtime library #
    elif db_error == sqlite3.NotSupportedError:
        logging.error('Db API not supported by sqlite3 runtime library: %s\n\n', db_error)
        print_err(f'Db API not supported by sqlite3 runtime library: {db_error}', None)

    # If unexpected error occurs (shouldn't happen, just in case) #
    else:
        logging.exception('Unexpected database exception: %s\n\n', db_error)
        print_err(f'Unexpected database exception: {db_error}', None)


def query_db_create() -> str:
    """
    MySQL query to create the Storage table.

    :return:  The formatted query.
    """
    return 'CREATE TABLE IF NOT EXISTS storage (' \
               'name VARCHAR(32) PRIMARY KEY NOT NULL,' \
               'path TINYTEXT NOT NULL,' \
               'ext TINYTEXT NOT NULL, content LONGTEXT NOT NULL' \
           ');'


def query_item_delete() -> str:
    """
    MySQL query to delete item from storage database.

    :return:  The formatted query.
    """
    return 'DELETE FROM storage WHERE name=?;'


def query_item_fetch() -> str:
    """
    MySQL query to retrieve item from storage database.

    :return:  The formatted query.
    """
    return 'SELECT name,path,ext,content FROM storage WHERE name=?;'


def query_select_all() -> str:
    """
    MySQL query to retrieve all contents of storage database.

    :return:  The formatted query.
    """
    return 'SELECT * FROM storage;'


def query_store_item() -> str:
    """
    MySQL query to store data into the Storage database.

    :return:  The formatted query.
    """
    return 'INSERT INTO storage (name, path, ext, content) VALUES (?, ?, ?, ?);'


def print_err(msg: str, seconds):
    """
    Displays error message via stderr for supplied time interval.

    :param msg:  The error message to be displayed.
    :param seconds:  The time interval the error message will be displayed or None for no time
                     interval.
    :return:  Nothing
    """
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)
    # If seconds not None #
    if seconds:
        # Sleep passed in interval #
        time.sleep(seconds)
