# File Database #
![alt text](https://github.com/ngimb64/File-Database/blob/main/FileDatabase.gif?raw=true)
![alt text](https://github.com/ngimb64/File-Database/blob/main/FileDatabase.png?raw=true)

&#9745;&#65039; Bandit verified<br>
&#9745;&#65039; Synk verified<br>
&#9745;&#65039; Pylint verified 9.79/10

## Prereqs
This program runs on Windows and Linux, written in Python 3.9

## Purpose
This program is a local file storage database for storage using MySQL standard query language.

## Installation
- Run the setup.py script to build a virtual environment and install all external packages in the created venv.

> Example: `python3 setup.py venv`

- Once virtual env is built traverse to the (Scripts-Windows or bin-Linux) directory in the environment folder just created.
- For Windows in the Scripts directory, for execute the `./activate` script to activate the virtual environment.
- For Linux in the bin directory, run the command `source activate` to activate the virtual environment.

## How to use
- Open up Command Prompt (CMD) or terminal
- Traverse to the directory containing the program and execute in shell
- Execute to access the command menu

## Function Layout
-- file_database.py --
> get_by_index &nbsp;-&nbsp; Finds file name in storage location based on passed in index.

> delete_file &nbsp;-&nbsp; Delete file stored in the storage database.

> store_file &nbsp;-&nbsp; Stores file in the storage database.

> extract_file &nbsp;-&nbsp; Extracts file from the storage database to Dock.

> list_storage &nbsp;-&nbsp; Queries database for list of all files and displays as enumerated list 
> to the user.

> main_menu &nbsp;-&nbsp; Display command options and receives input on what command to execute.

> main &nbsp;-&nbsp; Ensures critical directories are created, checks id database exists & creates 
> if non-existent, and calls MainMenu().

-- globals.py --
> dir_check &nbsp;-&nbsp; Check if directory exists.

> file_check &nbsp;-&nbsp; Check if file exists.

> db_storage &nbsp;-&nbsp; MySQL query to create the Storage table.

> db_store &nbsp;-&nbsp; MySQL query to store data into the Storage database.

> db_retrieve &nbsp;-&nbsp; MySQL query to retrieve item from storage database.

> db_contents &nbspl-&nbsp; MySQL query to retrieve all contents of storage database.

> db_delete &nbsp;-&nbsp; MySQL query to delete item from storage database.

-- utils.py --
> print_err &nbsp;-&nbsp; Displays error message via stderr for supplied time interval.

> query_handler &nbsp;-&nbsp; Facilitates MySQL database query execution.

> system_cmd &nbsp;-&nbsp; Execute shell-escaped system command.