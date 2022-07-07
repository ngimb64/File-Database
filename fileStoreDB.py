# Built-In Modules #
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
import Modules.Globals as Globals
from Modules.utils import PrintErr, QueryHandler,  SystemCmd


# Pseudo-Constants #
DB_NAME = 'Storage'


"""
################
Function Index #
########################################################################################################################
GetFileNameFromIndex  -  Finds file name in storage location based on passed in index.
DeleteStorageFile  -  Delete file stored in the storage database.
StoreStorageFile  -  Stores file in the storage database.
ExtractStorageFile  -  Extracts file from the storage database to Dock.
ListStorageDB  -  Queries database for list of all files and displays as enumerated list to the user.
MainMenu  -  Display command options and receives input on what command to execute.
main  -  Prompts user for password to access database, ensures critical directories are created, checks id database \
         exists & creates if non-existent, and calls MainMenu().
########################################################################################################################
"""


"""
########################################################################################################################
Name:       GetFileNameFromIndex
Purpose:    Finds file name in storage location based on passed in index.
Parameters: The integer representing the row in the storage database where the file is stored.
Returns:    The actual file name.
########################################################################################################################
"""
def GetFilenameFromIndex(file: int) -> str:
    # Format query to list all the contents of storage database #
    list_query = Globals.DB_CONTENTS(DB_NAME)
    # Execute query to list the contents of storage database #
    rows = QueryHandler(DB_NAME, list_query, fetchall=True)

    # If no rows are returned #
    if not rows:
        PrintErr(f'Database - {DB_NAME} database is empty', 2)
        return

    files = []
    # Populate file names from db to list #
    [files.append(row[0]) for row in rows]

    try:
        # Assign file name with full path as designated index #
        filename = files[file]
    # If trying to access index that does not exist #
    except IndexError as index_err:
        PrintErr(f'Index error - {index_err}', 2)
        return

    return filename


"""
########################################################################################################################
Name:       DeleteStorageFile
Purpose:    Delete file stored in the storage database.
Parameters: Nothing
Returns:    Nothing
########################################################################################################################
"""
def DeleteStorageFile():
    # Prompt user for file name/number and type #
    file_name = input('File name or number to delete?\n')
    file_type = input('\nFile type (TEXT or IMAGE)?\n')

    # If the file type is not in options #
    if file_type not in ('TEXT', 'IMAGE'):
        PrintErr(f'Invalid input detected => {file_type}', 2)
        return

    # If the user entered a number #
    if file_name.isdigit():
        # Get the file name from specified row index #
        file_name = GetFilenameFromIndex(int(file_name))

    # Format query to delete item in storage database #
    delete_query = Globals.DB_DELETE(DB_NAME, file_name)
    # Execute query to delete item in storage database #
    QueryHandler(DB_NAME, delete_query)

    print(f'\n$ {file_name} has been successfully deleted from {DB_NAME} database $')


"""
########################################################################################################################
Name:       StoreStorageFile
Purpose:    Stores files in the storage database.
Parameters: Regex pattern to match file path and path to the current working dir.
Returns:    Nothing
########################################################################################################################
"""
def StoreStorageFile(path_regex: str, cwd: str):
    name, ext = [], []

    path = input('Enter the absolute path of directory to store files or '
                 'hit enter to store files from the Dock directory:\n')
    prompt = input('\nShould the files being stored be deleted after storage operation? ')
    print('')

    # If one of the options was not selected #
    if prompt not in ('y', 'n'):
        PrintErr('Improper input, pick y or n', 2)
        return

    # If the user selects the Dock directory #
    if path == '':
        # Get the current working directory and append Dock path #
        file_path = f'{cwd}\\Dock'
    # If path regex fails #
    elif not re.search(path_regex, path):
        PrintErr(f'Regex failed to match {path} to be stored', 2)
        return
    # If proper path was passed in #
    else:
        file_path = path

    print(f'Storing files in {file_path}:\n{(19 + len(file_path)) * "*"}\n')

    # Iterate recursively through the file names in path
    for _, _, filenames in os.walk(file_path):
        for file in filenames:
            # Split the file name and extension #
            res = file.split('.')

            # If the filename contains more than one period for extension #
            if not re.search(r'^[^.]{1,30}\.[a-z]{2,4}$', file):
                # Append the last member in list as extension #
                ext.append(res[-1])
                # Remove the extension from list #
                e = res.pop()

                parse_name = ''
                # Iterate through split chunks #
                for chunk in res:
                    # Append chunk to result name #
                    parse_name += chunk

                # Append fixed name to list #
                name.append(parse_name)
                # Rename the file to new name #
                os.rename(f'{file_path}\\{file}', f'{file_path}\\{parse_name}.{e}')
            else:
                # Append name to name list #
                name.append(res[0])
                # Append extension to extension list #
                ext.append(res[1])

    extensions = {'txt': 'TEXT', 'py': 'TEXT',
                  'html': 'TEXT', 'jpg': 'IMAGE',
                  'png': 'IMAGE', 'jpeg': 'IMAGE'}

    # Iterate through file names and extensions #
    for n, e in zip(name, ext):
        # If current file extension in defined dict #
        if e in extensions.keys():
            ext_type = extensions[e]
        # If file extension not in defined dict #
        else:
            PrintErr('Improper file extension format', 2)
            return

        # Format file path of current iteration #
        current_file = f'{file_path}\\{n}.{e}'

        # If image file #
        if ext_type == 'IMAGE':
            # Get the image data #
            img = cv2.imread(current_file)

            # If jpg image #
            if e == 'jpg':
                file_string = base64.b64encode(cv2.imencode('.jpg', img)[1])
            # If jpeg image #
            elif e == 'jpeg':
                file_string = base64.b64encode(cv2.imencode('.jpeg', img)[1])
            # If png image #
            elif e == 'png':
                file_string = base64.b64encode(cv2.imencode('.png', img)[1])
            # If unsupported image type #
            else:
                PrintErr('Image type error - Unsupported image file type detected', 2)
                return

        # If text file #
        elif ext_type == 'TEXT':
            with open(current_file, 'rb') as file:
                file_string = base64.b64encode(file.read())

        # For other file types #
        else:
            PrintErr('Improper type - Unsupported file extension type detected', 2)
            return

        insert_query = Globals.DB_STORE(DB_NAME, f'{n}.{e}', file_path, ext_type, file_string.decode())
        QueryHandler(DB_NAME, insert_query)

        # Print success and delete stored file from Dock #
        print(f'File => {n}.{e} Stored')

        # If the user wants the files deleted after storage #
        if prompt == 'y':
            # Delete the current file #
            os.remove(f'{file_path}\\{n}.{e}')

    print(f'\n$ All files in {file_path} have been stored in {DB_NAME} database $')


"""
########################################################################################################################
Name:       ExtractStorageFile
Purpose:    Extracts file from the storage database to Dock.
Parameters: Path to current working dir.
Returns:    Nothing
########################################################################################################################
"""
def ExtractStorageFile(cwd: str):
    # Prompt user for file name/number and type #
    file_name = input('File name or number to extract?\n')
    file_type = input('\nFile type (TEXT or IMAGE)?\n')

    # If the file type is not in options #
    if file_type not in ('TEXT', 'IMAGE'):
        PrintErr(f'Invalid input detected => {file_type}', 2)
        return

    # If the user entered a number #
    if file_name.isdigit():
        # Get the file name from specified row index #
        file_name = GetFilenameFromIndex(int(file_name))

    # Format query to list all the contents of storage database #
    item_query = Globals.DB_RETRIEVE(DB_NAME, file_name)
    # Execute query to list the contents of storage database #
    row = QueryHandler(DB_NAME, item_query, fetchone=True)

    # If entry in storage database was noe retrieved #
    if not row:
        PrintErr('Database - Queried database entry does not exist', 2)
        return

    # If the retrieved rows file extension is the same as users input #
    if row[2] == file_type:
        # Set the file string the content column in retrieved row #
        file_string = row[3]

        # Decode from base64 #
        decoded_text = base64.b64decode(file_string)
        try:
            with open(f'{cwd}/Dock/{file_name}', 'wb') as out_file:
                out_file.write(decoded_text)

        # If file IO error occurs #
        except IOError as io_err:
            PrintErr(f'File IO error occurred - {io_err}', 2)
            return
    # If there is a file extension mismatch #
    else:
        PrintErr(f'File type - Improper file extension entered for file name {row[2]}', 2)
        return

    print(f'\n$ {file_name} successfully extracted from {DB_NAME} database $')


"""
########################################################################################################################
Name:       ListStorageDB
Purpose:    Queries database for list of all files and displays as enumerated list to the user.
Parameters: Nothing
Returns:    Nothing
########################################################################################################################
"""
def ListStorageDB():
    # Format query to list all the contents of storage database #
    list_query = Globals.DB_CONTENTS(DB_NAME)
    # Execute query to list the contents of storage database #
    rows = QueryHandler(DB_NAME, list_query, fetchall=True)

    print('\nFiles Available:\n-=-=-=-=-=-=-=-=-=->')
    [print(f'{index}  =>  {row[0]}') for index, row in enumerate(rows)]
    time.sleep(3)


"""
########################################################################################################################
Name:       MainMenu
Purpose:    Display command options and receives input on what command to execute.
Parameters: Command syntax tuple and path to current working dir.
Returns:    Nothing
########################################################################################################################
"""
def MainMenu(syntax_tuple: tuple, path: str):
    # If OS is Windows #
    if os.name == 'nt':
        # Set path regex and clear display command syntax #
        re_path = re.compile(r'^[A-Z]:(?:\\[a-zA-Z\d_\"\' .,\-]{1,30}){1,12}')
        cmd = syntax_tuple[0]
    # If OS is Linux #
    else:
        # Set path regex and clear display command syntax #
        re_path = re.compile(r'^(?:\\[a-zA-Z\d_\"\' .,\-]{1,30}){1,12}')
        cmd = syntax_tuple[1]

    # Set the program name banner #
    custom_fig = Figlet(font='roman', width=130)

    while True:
        # Clears screen per loop for clean display #
        SystemCmd(cmd, None, None, 2)

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
            ListStorageDB()
        # If file contents are to be retrieved #
        elif prompt == 'o':
            ExtractStorageFile(path)
        # If file contents are to be stored #
        elif prompt == 's':
            StoreStorageFile(re_path, path)
        # If the file contents are to be deleted #
        elif prompt == 'd':
            DeleteStorageFile()
        # If the program is to be exited #
        elif prompt == 'e':
            sys.exit(0)
        # If improper operation was supplied #
        else:
            PrintErr('Improper operation specified', 0.5)

        time.sleep(2)


"""
########################################################################################################################
Name:       main
Purpose:    Ensures critical directories are created, checks id database exists & creates if non-existent, \
            and calls MainMenu().
Parameters: Nothing
Returns:    Nothing
########################################################################################################################
"""
def main():
    # Commands tuple #
    cmds = ('cls', 'clear')
    # Get current working directory #
    cwd = os.getcwd()

    # Iterate through program dirs #
    for db in ('Dock', 'Dbs'):
        # If the directory does not exist #
        if not Globals.DIR_CHECK(db):
            # Create the missing dir #
            os.mkdir(db)

    try:
        os.chdir('Dbs')
        # Confirm database exists #
        dburi = 'file:{}?mode=rw'.format(pathname2url(f'{DB_NAME}.db'))
        sqlite3.connect(dburi, uri=True)
        os.chdir(cwd)

    # If storage database does not exist #
    except sqlite3.OperationalError:
        os.chdir(cwd)
        # Format storage database creation query #
        create_query = Globals.DB_STORAGE(DB_NAME)
        # Create storage database #
        QueryHandler(DB_NAME, create_query, create=True)

    MainMenu(cmds, cwd)


if __name__ == '__main__':
    # Set the log file name #
    logging.basicConfig(level=logging.DEBUG, filename='.\\FileDbLog.log')

    while True:
        try:
            main()

        # If Ctrl + C is detected #
        except KeyboardInterrupt:
            print('\n Ctrl + C detected .. exiting')
            break

        # Unknown exception handler #
        except Exception as err:
            PrintErr(f'Unknown exception occurred - {err}', 2)
            logging.exception(f'Unknown exception occurred - {err}\n\n')
            continue

    sys.exit(0)
