# Built-In Modules #
import os
import sqlite3
import shlex
import sys
import time
from sqlite3 import Warning, Error, DatabaseError, IntegrityError, \
                    ProgrammingError, OperationalError, NotSupportedError
from subprocess import Popen, CalledProcessError, TimeoutExpired, SubprocessError
from threading import BoundedSemaphore


"""
################
Function Index #
########################################################################################################################
PrintErr  -  Displays error message for supplied time interval.
QueryHandler  -  Facilitates MySQL database query execution.
SystemCmd  -  Execute shell-escaped system command.
########################################################################################################################
"""


"""
########################################################################################################################
Name        PrintErr
Purpose:    Displays error message for supplied time interval.
Parameters: The message to be displayed and the time interval to be displayed in seconds.
Returns:    None
########################################################################################################################
"""
def PrintErr(msg: str, seconds: int):
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)
    time.sleep(seconds)


"""
########################################################################################################################
Name:       QueryHandler
Purpose:    Facilitates MySQL database query execution.
Parameters: Database to execute query, query to be executed, hashed password, create toggle, fetchone toggle, and \
            fetchall toggle.
Returns:    None
########################################################################################################################
"""
def QueryHandler(db: str, query: str, create=False, fetchone=False, fetchall=False):
    # Change directory #
    os.chdir('Dbs')
    # Sets maximum number of allowed db connections #
    maxConns = 1
    # Locks allowed connections to database #
    sema_lock = BoundedSemaphore(value=maxConns)

    # Attempts to connect, continues if already connected #
    with sema_lock:
        try:
            # Connect to passed in database #
            conn = sqlite3.connect(f'{db}.db')
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
        except (Warning, Error, DatabaseError, IntegrityError,
                ProgrammingError, OperationalError, NotSupportedError) as err:
            # Prints general error #
            PrintErr(f'Database error occurred - {err}', 2)
            # Moves back a directory #
            os.chdir('..')

        # Close connection #
        conn.close()


"""
########################################################################################################################
Name:       SystemCmd
Purpose:    Execute shell-escaped system command.
Parameters: Command to be executed, standard output, standard error, execution timeout.
Returns:    None
########################################################################################################################
"""
def SystemCmd(cmd: str, stdout, stderr, exec_time: int):
    # Shell escape command string #
    exe = shlex.quote(cmd)

    command = Popen(exe, stdout=stdout, stderr=stderr, shell=True)
    try:
        command.communicate(exec_time)

    # Handles process timeouts and errors #
    except (SubprocessError, TimeoutExpired, CalledProcessError, OSError, ValueError):
        command.kill()
        command.communicate()
