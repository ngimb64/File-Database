# pylint: disable=W0106,E1101
""" Built-in modules """
import base64
import logging
import os
import re
import sqlite3
import sys
import time
from urllib.request import pathname2url
# External Modules #
import cv2
from pyfiglet import Figlet
# Custom Modules #
import Modules.globals as globs
from Modules.utils import print_err, query_handler,  system_cmd


# Pseudo-Constants #
DB_NAME = 'Storage'


def get_by_index(file: int):
    """
    Finds file name in storage location based on passed in index.

    :param file:  The integer representing the row in the storage database where the file is stored.
    :return: The actual file name on success and prints error on failure.
    """
    # Format query to list all the contents of storage database #
    list_query = globs.db_contents(DB_NAME)
    # Execute query to list the contents of storage database #
    rows = query_handler(DB_NAME, list_query, fetchall=True)

    # If no rows are returned #
    if not rows:
        return print_err(f'Database - {DB_NAME} database is empty', 2)

    files = []
    # Populate file names from db to list #
    [files.append(row[0]) for row in rows]

    try:
        # Assign file name with full path as designated index #
        filename = files[file]
    # If trying to access index that does not exist #
    except IndexError as index_err:
        return print_err(f'Index error - {index_err}', 2)

    return filename


def delete_file():
    """
    Delete file stored in the storage database.

    :return:  Prints success or error message.
    """
    # Prompt user for file name/number and type #
    file_name = input('File name or number to delete?\n')
    file_type = input('\nFile type (TEXT or IMAGE)?\n')

    # If the file type is not in options #
    if file_type not in ('TEXT', 'IMAGE'):
        return print_err(f'Invalid input detected => {file_type}', 2)

    # If the user entered a number #
    if file_name.isdigit():
        # Get the file name from specified row index #
        file_name = get_by_index(int(file_name))

    # Format query to delete item in storage database #
    delete_query = globs.db_delete(DB_NAME, file_name)
    # Execute query to delete item in storage database #
    query_handler(DB_NAME, delete_query)

    return print(f'\n$ {file_name} has been successfully deleted from {DB_NAME} database $')


def store_file(path_regex, curr_path: str):
    """
    Stores files in the storage database.

    :param path_regex:  Compiled regex pattern to match file path.
    :param curr_path:  Path to the current working directory.
    :return:  Prints success or error message.
    """
    name, ext = [], []

    store_path = input('Enter the absolute path of directory to store files or '
                       'hit enter to store files from the Dock directory:\n')
    prompt = input('\nShould the files being stored be deleted after storage operation (y or n)? ')
    print('')

    # If one of the options was not selected #
    if prompt not in ('y', 'n'):
        return print_err('Improper input, pick y or n', 2)

    # If the user selects the Dock directory #
    if store_path == '':
        # Get the current working directory and append Dock path #
        file_path = f'{curr_path}Dock'
    # If path regex fails #
    elif not re.search(path_regex, store_path):
        return print_err(f'Regex failed to match {store_path} to be stored', 2)
    # If proper path was passed in #
    else:
        file_path = store_path

    allowed_ext = ('.txt', '.py', '.html', '.jpg', '.png', '.jpeg')
    extensions = {'txt': 'TEXT', 'py': 'TEXT',
                  'html': 'TEXT', 'jpg': 'IMAGE',
                  'png': 'IMAGE', 'jpeg': 'IMAGE'}

    print(f'Storing files in {file_path}:\n{(19 + len(file_path)) * "*"}\n')

    # Iterate through the file names in path #
    for file in os.scandir(file_path):
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

            # If the OS is Windows #
            if os.name == 'nt':
                src_file = f'{file_path}\\{file.name}'
                dest_file = f'{file_path}\\{parse_name}.{file_ext}'
            # If the OS is Linux #
            else:
                src_file = f'{file_path}/{file.name}'
                dest_file = f'{file_path}/{parse_name}.{file_ext}'

            # Rename the file to new name #
            os.rename(src_file, dest_file)

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
        # If the OS is Windows #
        if os.name == 'nt':
            # Format file path of current iteration #
            current_file = f'{file_path}\\{file_name}.{file_ext}'
        # If the OS is Linux #
        else:
            current_file = f'{file_path}/{file_name}.{file_ext}'

        # If image file #
        if ext_type == 'IMAGE':
            # Get the image data #
            img = cv2.imread(current_file)

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
                return print_err('Image type error - Unsupported image file type detected', 2)

        # If text file #
        elif ext_type == 'TEXT':
            with open(current_file, 'rb') as file:
                file_string = base64.b64encode(file.read())

        # For other file types #
        else:
            return print_err('Improper type - Unsupported file extension type detected', 2)

        insert_query = globs.db_store(DB_NAME, f'{file_name}.{file_ext}', file_path,
                                      ext_type, file_string.decode())
        query_handler(DB_NAME, insert_query)

        # Print success and delete stored file from Dock #
        print(f'File => {file_name}.{file_ext} Stored')

        # If the user wants the files deleted after storage #
        if prompt == 'y':
            # Delete the current file #
            os.remove(current_file)

    return print(f'\n$ All files in {file_path} have been stored in {DB_NAME} database $')


def extract_file(file_path: str):
    """
    Extracts file from the storage database to Dock.

    :param file_path:  The path to the current working directory.
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
        file_name = get_by_index(int(file_name))

    # Format query to list all the contents of storage database #
    item_query = globs.db_retrieve(DB_NAME, file_name)
    # Execute query to list the contents of storage database #
    row = query_handler(DB_NAME, item_query, fetchone=True)

    # If entry in storage database was noe retrieved #
    if not row:
        return print_err('Database - Queried database entry does not exist', 2)

    # If the retrieved rows file extension is the same as users input #
    if row[2] == file_type:
        # Set the file string the content column in retrieved row #
        file_string = row[3]
        # Decode from base64 #
        decoded_text = base64.b64decode(file_string)

        # If the OS is Windows #
        if os.name == 'nt':
            extract_path = f'{file_path}Dock\\{file_name}'
        # If the OS is Linux #
        else:
            extract_path = f'{file_path}Dock/{file_name}'

        try:
            with open(extract_path, 'wb') as out_file:
                out_file.write(decoded_text)

        # If file IO error occurs #
        except (IOError, OSError) as io_err:
            return print_err(f'File IO error occurred - {io_err}', 2)
    # If there is a file extension mismatch #
    else:
        return print_err(f'File type - Improper file extension entered for file name {row[2]}', 2)

    return print(f'\n$ {file_name} successfully extracted from {DB_NAME} database $')


def list_storage():
    """
    Queries database for list of all files and displays as enumerated list to the user.

    :return:  Nothing
    """
    # Format query to list all the contents of storage database #
    list_query = globs.db_contents(DB_NAME)
    # Execute query to list the contents of storage database #
    rows = query_handler(DB_NAME, list_query, fetchall=True)

    print('\nFiles Available:\n-=-=-=-=-=-=-=-=-=->')
    [print(f'{index}  =>  {row[0]}') for index, row in enumerate(rows)]
    time.sleep(3)


def main_menu(syntax_tuple: tuple, current_path: str):
    """
    Display command options and receives input on what command to execute.

    :param syntax_tuple:  Command syntax tuple.
    :param current_path:  Path to current working directory.
    :return:  Nothing
    """
    # If OS is Windows #
    if os.name == 'nt':
        # Set path regex and clear display command syntax #
        re_path = re.compile(r'^[A-Z]:(?:\\[a-zA-Z\d_\"\' .,-]{1,30}){1,12}')
        cmd = syntax_tuple[0]
    # If OS is Linux #
    else:
        # Set path regex and clear display command syntax #
        re_path = re.compile(r'^(?:/[a-zA-Z\d_\"\' .,-]{1,30}){1,12}')
        cmd = syntax_tuple[1]

    # Set the program name banner #
    custom_fig = Figlet(font='roman', width=130)

    while True:
        # Clears screen per loop for clean display #
        system_cmd(cmd, None, None, 2)

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

        prompt = input('#>>: ')

        # If db contents are to be listed #
        if prompt == 'l':
            list_storage()
        # If file contents are to be retrieved #
        elif prompt == 'o':
            extract_file(current_path)
        # If file contents are to be stored #
        elif prompt == 's':
            store_file(re_path, current_path)
        # If the file contents are to be deleted #
        elif prompt == 'd':
            delete_file()
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
    # Commands tuple #
    cmds = ('cls', 'clear')

    # Iterate through program dirs #
    for curr_db in ('Dock', 'Dbs'):
        # If the directory does not exist #
        if not globs.dir_check(curr_db):
            # Create the missing dir #
            os.mkdir(curr_db)

    try:
        os.chdir('Dbs')
        # Confirm database exists #
        db_name = f'{DB_NAME}.db'
        dburi = f'file:{pathname2url(db_name)}?mode=rw'
        sqlite3.connect(dburi, uri=True)
        os.chdir(cwd)

    # If storage database does not exist #
    except sqlite3.OperationalError:
        os.chdir(cwd)
        # Format storage database creation query #
        create_query = globs.db_storage(DB_NAME)
        # Create storage database #
        query_handler(DB_NAME, create_query, create=True)

    main_menu(cmds, path)


if __name__ == '__main__':
    # Get the current working directory #
    cwd = os.getcwd()

    # If the OS is Windows #
    if os.name == 'nt':
        path = f'{cwd}\\'
    else:
        path = f'{cwd}/'

    # Set the log file name #
    logging.basicConfig(level=logging.DEBUG, filename=f'{path}FileDbLog.log')

    while True:
        try:
            main()

        # If Ctrl + C is detected #
        except KeyboardInterrupt:
            print('\n Ctrl + C detected .. exiting')
            break

        # Unknown exception handler #
        except Exception as err:
            print_err(f'Unknown exception occurred - {err}', 2)
            logging.exception('Unknown exception occurred - %s\n\n', err)
            continue

    sys.exit(0)
