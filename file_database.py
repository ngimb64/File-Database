# pylint: disable=W0106,E1101,E0401
""" Built-in modules """
import base64
import logging
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from shlex import quote
from threading import BoundedSemaphore
from urllib.request import pathname2url
# External Modules #
import cv2
from pyfiglet import Figlet
# Custom Modules #
from Modules.utils import DbConnectionHandler, db_error_query, query_select_all, \
                          query_item_delete, query_item_fetch, query_db_create, query_store_item, \
                          print_err, query_handler


# Global variables #
DB_NAME = 'storage'


def get_by_index(file: int, db_conn: sqlite3):
    """
    Finds file name in storage location based on passed in index.

    :param file:  The integer representing the row in the storage database where the file is stored.
    :param db_conn:  The protected database connection to be interacted with.
    :return: The actual file name on success and prints error on failure.
    """
    # Get formatted query to retrieve the contents of database #
    list_query = query_select_all()
    # Execute query to list the contents of storage database #
    rows = query_handler(db_conn, list_query, fetch='all')

    # If no rows are returned #
    if not rows:
        return print_err(f'{DB_NAME} database currently has no data stored in it', 2)

    # Populate file names from db to list #
    files = [row[0] for row in rows]

    try:
        # Assign file name with full path as designated index #
        filename = files[file]

    # If trying to access index that does not exist #
    except IndexError as index_err:
        logging.error('Index error accessing file index: %s\n\n', index_err)
        return print_err(f'Index error accessing file index: {index_err}', 2)

    return filename


def delete_file(db_conn: sqlite3):
    """
    Delete file stored in the storage database.

    :param db_conn:  The protected database connection to be interacted with.
    :return:  Prints success or error message.
    """
    # Prompt user for file name/number and type #
    file_name = input('File name or number to delete?\n')
    file_type = input('\nFile type (TEXT or IMAGE)?\n')

    # If the file type is not in options #
    if file_type not in ('TEXT', 'IMAGE'):
        return print_err(f'Invalid input detected: {file_type}', 2)

    # If the user entered a number #
    if file_name.isdigit():
        # Get the file name from specified row index #
        file_name = get_by_index(int(file_name), db_conn)

    # Get formatted query to delete item from database #
    delete_query = query_item_delete()
    # Execute query to delete item in storage database #
    query_handler(db_conn, delete_query, file_name)

    return print(f'\n[!] {file_name} has been successfully deleted from {DB_NAME} database')


def store_file(path_regex, db_conn: sqlite3):
    """
    Stores files in the storage database.

    :param path_regex:  Compiled regex pattern to match file path.
    :param db_conn:  The protected database connection to be interacted with.
    :return:  Prints success or error message.
    """
    name, ext = [], []

    store_path = input('Enter the absolute path of directory to store files or '
                       'hit enter to store files from the Dock directory:\n')
    prompt = input('\nShould the files being stored be deleted after storage operation (y or n)? ')
    print('')

    # If one of the options was not selected #
    if prompt not in ('y', 'n'):
        return print_err('Improper input .. pick y or n', 2)

    # If the user selects the Dock directory #
    if store_path == '':
        # Get the current working directory and append Dock path #
        file_path = curr_path / 'Dock'
    # If path regex fails #
    elif not re.search(path_regex, store_path):
        # Return error #
        return print_err(f'Regex failed to match path to be stored: {store_path}', 2)
    # If proper path was passed in #
    else:
        file_path = Path(store_path)

    allowed_ext = ('.txt', '.py', '.html', '.jpg', '.png', '.jpeg')
    extensions = {'txt': 'TEXT', 'py': 'TEXT', 'html': 'TEXT', 'jpg': 'IMAGE',
                  'png': 'IMAGE', 'jpeg': 'IMAGE'}

    print(f'Storing files in {str(file_path.resolve())}:\n'
          f'{(19 + len(str(file_path.resolve()))) * "*"}\n')

    # Iterate through the file names in path #
    for file in os.scandir(str(file_path.resolve())):
        # If file does not have supported file type #
        if not file.name.endswith(allowed_ext):
            continue

        # Split the file name and extension #
        res = file.name.split('.')

        # If the filename contains more than one period for extension #
        if not re.search(r'^[^.]{1,30}\.[a-z]{2,4}$', file.name):
            # Remove the extension from list #
            file_ext = res.pop()
            # Append the last member in list as extension #
            ext.append(file_ext)
            # Re-append remaining name #
            parse_name = ''.join(res)
            # Append fixed name to list #
            name.append(parse_name)
            # Format the new path with parsed data #
            src_file = file_path / file.name
            dest_file = file_path / f'{parse_name}.{file_ext}'
            # Rename the file to new name #
            os.rename(str(src_file.resolve()), str(dest_file.resolve()))

        # If the file name only has a single period for file ext #
        else:
            # Append name to name list #
            name.append(res[0])
            # Append extension to extension list #
            ext.append(res[1])

    # Iterate through file names and extensions #
    for file_name, file_ext in zip(name, ext):
        # If current file extension in defined dict #
        if file_ext in extensions:
            ext_type = extensions[file_ext]
        # If file extension not in defined dict #
        else:
            return print_err(f'File {file_name} has extension type '
                             f'{file_ext} that is not supported', 2)

        # Format the current file path #
        current_file = file_path / f'{file_name}.{file_ext}'

        # If image file #
        if ext_type == 'IMAGE':
            # Get the image data #
            img = cv2.imread(str(current_file.resolve()))

            # If jpg image #
            if file_ext == 'jpg':
                file_string = base64.b64encode(cv2.imencode('.jpg', img)[1])
            # If jpeg image #
            elif file_ext == 'jpeg':
                file_string = base64.b64encode(cv2.imencode('.jpeg', img)[1])
            # If png image #
            elif file_ext == 'png':
                file_string = base64.b64encode(cv2.imencode('.png', img)[1])
            # If unsupported image type #
            else:
                return print_err('Unsupported image file type detected', 2)

        # If text file #
        elif ext_type == 'TEXT':
            with current_file.open('rb') as file:
                file_string = base64.b64encode(file.read())

        # For other file types #
        else:
            return print_err('Unsupported file extension type detected', 2)

        # Get formatted query to store item in database #
        insert_query = query_store_item()
        # Store the current iteration in database #
        query_handler(db_conn, insert_query, f'{file_name}.{file_ext}', str(file_path.resolve()),
                      ext_type, file_string.decode())

        # Print success and delete stored file from Dock #
        print(f'File => {file_name}.{file_ext} Stored')

        # If the user wants the files deleted after storage #
        if prompt == 'y':
            # Delete the current file #
            os.remove(str(current_file.resolve()))

    return print(f'\n[!] All files in {str(file_path.resolve())} have been stored in {DB_NAME} '
                 'database')


def extract_file(db_conn: sqlite3):
    """
    Extracts file from the storage database to Dock.

    :param db_conn:  The protected database connection to be interacted with.
    :return:  Prints success or error message.
    """
    # Prompt user for file name/number and type #
    file_name = input('File name or number to extract?\n')
    file_type = input('\nFile type (TEXT or IMAGE)?\n')

    # If the file type is not in options #
    if file_type not in ('TEXT', 'IMAGE'):
        return print_err(f'Invalid input detected => {file_type}', 2)

    # If the user entered a number #
    if file_name.isdigit():
        # Get the file name from specified row index #
        file_name = get_by_index(int(file_name), db_conn)

    # Get formatted query to fetch an item #
    item_query = query_item_fetch()
    # Execute query to list contents of single file in storage database #
    row = query_handler(db_conn, item_query, file_name, fetch='one')

    # If entry in storage database was noe retrieved #
    if not row:
        return print_err('Queried database entry does not exist', 2)

    # If the retrieved rows file extension is the same as users input #
    if row[2] == file_type:
        # Set the file string the content column in retrieved row #
        file_string = row[3]
        # Decode from base64 #
        decoded_text = base64.b64decode(file_string)
        # Change back to dock directory #
        os.chdir(str(dock_path.resolve()))
        # Format the file to be extracted path #
        extract_path = dock_path / file_name

        try:
            with extract_path.open('ab') as out_file:
                out_file.write(decoded_text)

        # If file IO error occurs #
        except (IOError, OSError) as file_err:
            logging.error('Error occurred during file operation: %s\n\n', file_err)
            # Change back into base directory #
            os.chdir(str(db_path.resolve()))
            return print_err(f'Error occurred during file operation: {file_err}', 2)

    # If there is a file extension mismatch #
    else:
        return print_err(f'File type - Improper file extension entered for file name {row[2]}', 2)

    # Change back into db directory #
    os.chdir(str(db_path.resolve()))

    return print(f'\n$ {file_name} successfully extracted from {DB_NAME} database $')


def list_storage(db_conn: sqlite3):
    """
    Queries database for list of all files and displays as enumerated list to the user.

    :param db_conn:  The protected database connection to be interacted with.
    :return:  Nothing
    """
    # Get formatted query to fetch all db contents #
    list_query = query_select_all()
    # Execute query to list the contents of storage database #
    rows = query_handler(db_conn, list_query, fetch='all')

    count = 0
    print(f'\nFiles Available:\n{"-=" * 12}->')

    # Iterate through fetched data with corresponding index #
    for index, row in enumerate(rows):
        # If the line count is maxed #
        if count == 60:
            # Wait for user to continue and reset #
            input('[+] Press enter to continue .. ')
            count = 0

        print(f'{index} => {row[0]}')
        count += 1

    time.sleep(3)


def main_menu(db_conn: sqlite3):
    """
    Display command options and receives input on what command to execute.

    :param db_conn:  The protected database connection to be interacted with.
    :return:  Nothing
    """
    # If OS is Windows #
    if os.name == 'nt':
        # Set path regex and clear display command syntax #
        re_path = re.compile(r'^[A-Z]:(?:\\[a-zA-Z\d_\"\' .,-]{1,30}){1,12}')
        cmd = quote('cls')
    # If OS is Linux #
    else:
        # Set path regex and clear display command syntax #
        re_path = re.compile(r'^(?:/[a-zA-Z\d_\"\' .,-]{1,30}){1,12}')
        cmd = quote('clear')

    # Set the program name banner #
    custom_fig = Figlet(font='larry3d', width=130)

    while True:
        # Clears screen per loop for clean display #
        os.system(cmd)

        # Print the program name banner #
        print(custom_fig.renderText('$ File Database $'))
        # Print the menu #
        print('''
        #--------------------------#
        |         Commands         | 
        #==========================#
        |    l => List Contents    |
        |    o => Open File        |
        |    s => Store File       |
        |    d => Delete File      |
        |    e => Exit Database    |
        #--------------------------#
        ''')

        prompt = input('[Enter Command]::>> ')

        # If db contents are to be listed #
        if prompt == 'l':
            list_storage(db_conn)
        # If file contents are to be retrieved #
        elif prompt == 'o':
            extract_file(db_conn)
        # If file contents are to be stored #
        elif prompt == 's':
            store_file(re_path, db_conn)
        # If the file contents are to be deleted #
        elif prompt == 'd':
            delete_file(db_conn)
        # If the program is to be exited #
        elif prompt == 'e':
            sys.exit(0)
        # If improper operation was supplied #
        else:
            print_err('Improper operation specified', 0.5)

        time.sleep(2)


def main():
    """
    Ensures critical directories are created, checks id database exists & creates if non-existent, \
    and calls MainMenu().

    :return:  Nothing
    """
    # Assume database exists #
    exists = True
    # Switch into the database directory #
    os.chdir(str(db_path.resolve()))

    try:
        # Format the database file #
        db_name = f'{DB_NAME}.db'
        # Format the database file into uri query #
        dburi = f'file:{pathname2url(db_name)}?mode=rw'
        # Attempt to connect to the database #
        sqlite3.connect(dburi, uri=True)

    # If storage database does not exist #
    except sqlite3.OperationalError:
        # Set boolean for database to be created #
        exists = False

    max_conns = 1
    # Initialize semaphore instance to limit number of connections to database #
    sema_lock = BoundedSemaphore(value=max_conns)

    try:
        # Acquire semaphore lock #
        with sema_lock:
            try:
                # Initialize db connection context manager instance #
                with DbConnectionHandler(f'{DB_NAME}.db') as connection:
                    # If the database does not exist #
                    if not exists:
                        # Get formatted query to create database #
                        create_query = query_db_create()
                        # Create storage database #
                        query_handler(connection, create_query, exec_script=True)

                    # Pass base path and db connection in main #
                    main_menu(connection)

            # If any sqlite3 error occurs during database operation #
            except sqlite3.Error as db_err:
                # Lookup exact database error to log and exit #
                db_error_query(db_err)
                sys.exit(2)

    # If semaphore is attempting to allocate more resources than allowed #
    except ValueError as val_err:
        # Log error and exit #
        logging.error('Database connection semaphore error attempted to acquire more than '
                      'allowed max value %d: %s\n\n', max_conns, val_err)
        sys.exit(1)

    # Switch back to base directory #
    os.chdir(str(path.resolve()))


if __name__ == '__main__':
    # Get the current working directory #
    cwd = Path('.')
    path = Path(str(cwd.resolve()))
    db_path = path / 'Dbs'
    dock_path = path / 'Dock'
    log_file = path / 'filedb_log.log'
    # Set the log file name #
    logging.basicConfig(filename=str(log_file.resolve()),
                        format='%(asctime)s line%(lineno)d::%(funcName)s[%(levelname)s]>>'
                               ' %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Iterate through program dirs #
    for curr_path in (db_path, dock_path):
        # If the directory does not exist #
        if not curr_path.exists():
            # Create the missing dir #
            curr_path.mkdir()

    while True:
        try:
            main()

        # If Ctrl + C is detected #
        except KeyboardInterrupt:
            print('\n\n[!] Ctrl + C detected .. exiting')
            break

        # Unknown exception handler #
        except Exception as err:
            print_err(f'Unknown exception occurred - {err}', 2)
            logging.exception('Unknown exception occurred - %s\n\n', err)
            continue

    sys.exit(0)
