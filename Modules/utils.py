""" Built-in modules """
import os
import shlex
import sqlite3
import sys
import time
from sqlite3 import Error, DatabaseError, IntegrityError, ProgrammingError, \
                    OperationalError, NotSupportedError
from subprocess import Popen, CalledProcessError, TimeoutExpired, SubprocessError
from threading import BoundedSemaphore


def print_err(msg: str, seconds):
    """
    Displays error message via stderr for supplied time interval.

    :param msg:  The error message to be displayed.
    :param seconds:  The time interval the error message will be displayed.
    :return:  Nothing
    """
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)
    time.sleep(seconds)


def query_handler(curr_db: str, query: str, create=False, fetchone=False, fetchall=False):
    """
    Facilitates MySQL database query execution.

    :param curr_db:  The database where the query will be executed.
    :param query:  The query that will be executed.
    :param create:  Boolean toggle for creation function.
    :param fetchone:  Boolean toggle for fetching a row.
    :param fetchall:  Boolean toggle for fetching all rows.
    :return:  Nothing
    """
    # Change directory #
    os.chdir('Dbs')
    # Sets maximum number of allowed db connections #
    max_conns = 1
    # Locks allowed connections to database #
    sema_lock = BoundedSemaphore(value=max_conns)

    # Attempts to connect, continues if already connected #
    with sema_lock:
        try:
            # Connect to passed in database #
            conn = sqlite3.connect(f'{curr_db}.db')
        # If database already exists #
        except Error:
            pass

        # Executes query passed in #
        try:
            db_call = conn.execute(query)

            # If creating database close connection
            # and moves back a directory #
            if create:
                conn.close()
                os.chdir('..')
                return

            # Fetches entry from database then closes
            # connection and moves back a directory #
            elif fetchone:
                row = db_call.fetchone()
                conn.close()
                os.chdir('..')
                return row

            # Fetches all database entries then closes
            # connection and moves back a directory #
            elif fetchall:
                rows = db_call.fetchall()
                conn.close()
                os.chdir('..')
                return rows

            # Commit query to db #
            conn.commit()
            # Move back a directory #
            os.chdir('..')

        # Database query error handling #
        except (Error, DatabaseError, IntegrityError, ProgrammingError,
                OperationalError, NotSupportedError) as err:
            # Prints general error #
            print_err(f'Database error occurred - {err}', 2)
            # Moves back a directory #
            os.chdir('..')

        # Close connection #
        conn.close()


def system_cmd(cmd: str, stdout, stderr, exec_timeout: int):
    """
    Execute shell-escaped system command.

    :param cmd:  The command syntax to be executed.
    :param stdout:  Where standard output is directed to.
    :param stderr:  Where standard error is directed to.
    :param exec_timeout:  The execution timeout
    :return:
    """
    # Shell-escape command syntax passed in #
    syntax = shlex.quote(cmd)

    # Create the subprocess instance #
    with Popen(syntax, stdout=stdout, stderr=stderr, shell=True) as command:
        try:
            # Execute command #
            command.communicate(timeout=exec_timeout)

        # Handles process timeouts and errors #
        except (SubprocessError, TimeoutExpired, CalledProcessError, OSError, ValueError):
            command.kill()
            command.communicate()
