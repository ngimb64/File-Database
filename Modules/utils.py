# Built-In Modules #
import ctypes
import os
import re
import sqlite3
import shlex
import sys
import time
from getpass import getpass
from sqlite3 import Warning, Error, DatabaseError, IntegrityError, \
                    ProgrammingError, OperationalError, NotSupportedError
from subprocess import Popen, CalledProcessError, TimeoutExpired, SubprocessError
from threading import BoundedSemaphore

# External Modules #
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from keyring import get_password, set_password
from keyring.errors import KeyringError

# Custom Modules #
import Modules.Globals as Globals


"""
################
Function Index #
########################################################################################################################
PasswordInput  -  Receive password input from user, verify with Argon2 hashing algorithm or create new password if \
                  none exist.
PrintErr  -  Displays error message for supplied time interval.
QueryHandler  -  Facilitates MySQL database query execution.
SystemCmd  -  Execute shell-escaped system command.
########################################################################################################################
"""


"""
########################################################################################################################
Name:       PasswordInput
Purpose:    Receive password input from user, verify with Argon2 hashing algorithm or create new password in none exist.
Parameters: Command syntax tuple and boolean toggle switch.
Returns:    Validate input hash and boolean toggle switch.
########################################################################################################################
"""
def PasswordInput(syntax_tuple: tuple) -> bytes:
    count = 0
    # Initialize password hashing algorithm #
    pass_algo = PasswordHasher()

    # If OS is Windows #
    if os.name == 'nt':
        cmd = syntax_tuple[0]
    # If OS is Linux #
    else:
        cmd = syntax_tuple[1]

    while True:
        # Clear display #
        # SystemCmd(cmd, None, None, 2)

        # If user maxed attempts (3 sets of 3 failed password attempts) #
        if count == 12:
            # Code can be added to notify administrator or
            # raise an alert to remote system #

            # Lock the system #
            ctypes.wind11.user32.LockWorkStation()

        # After three password failures #
        elif count in (3, 6, 9):
            PrintErr('Too many login attempts .. 60 second timeout', 0)
            for sec in range(1, 61):
                msg = f'{"!" * sec} sec'
                print(msg, end='\r')
                time.sleep(1)

        # Prompt user for input #
        prompt = getpass('\n\nEnter your unlock password or password for creating keys: ')

        # Check input syntax & length #
        if not re.search(r'^[a-zA-Z0-9_!+$@&(]{12,30}', prompt):
            PrintErr('\n* [ERROR] Invalid password format .. at least 12 to 30 numbers, letters, &'
                     ' _+$@&( special characters allowed *', 2)
            count += 1
            continue

        # If key file exists indicating password is set #
        if Globals.FILE_CHECK('secret.txt'):
            # Attempt to retrieve password hash from key ring #
            try:
                keyring_hash = get_password('FileStoreDB', 'FileStoreUser')
            # If credential manager is missing password hash #
            except KeyringError:
                # Print error & return hashed input #
                print('\n Attempted access to key that does not exist, using input as new password')
                return pass_algo.hash(prompt).encode()

            # Verify input by comparing keyring hash against algo #
            try:
                pass_algo.verify(keyring_hash, prompt)
            except VerifyMismatchError:
                PrintErr('\n* [ERROR] Input does not match password hash *', 2)
                count += 1
                continue

            else:
                # Return hash stored in keyring #
                return keyring_hash.encode()

        # If new password needs to be set #
        else:
            # Confirm users password before setting #
            prompt2 = getpass('Enter password again to confirm: ')

            if not re.search(r'^[a-zA-Z0-9_!+$@&(]{12,30}', prompt2):
                PrintErr('\n* [ERROR] Invalid password format .. at least 12 to 30 numbers, letters, &'
                         ' _+$@&( special characters allowed *', 2)
                count += 1
                continue

                # Confirm the same password was entered twice #
            if prompt != prompt2:
                PrintErr('\n* [ERROR] Two different passwords were entered .. try again *', 2)
                count += 1
                continue

            # Add password hash to key ring #
            set_password('FileStoreDB', 'FileStoreUser', prompt)

            # Return hashed input as bytes #
            return pass_algo.hash(prompt).encode()


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
