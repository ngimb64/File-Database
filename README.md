<div align="center" style="font-family: monospace">
<h1>File Database</h1>
&#9745;&#65039; Bandit verified &nbsp;|&nbsp; &#9745;&#65039; Synk verified &nbsp;|&nbsp; &#9745;&#65039; Pylint verified 9.93/10
</div><br>

![alt text](https://github.com/ngimb64/File-Database/blob/main/FileDatabase.gif?raw=true)
![alt text](https://github.com/ngimb64/File-Database/blob/main/FileDatabase.png?raw=true)

## Purpose
This program is a local file storage database for storage utilizing the MySQL standard query language.

## Prereqs
This program runs on Windows 10 and Debian-based Linux, written in Python 3.9 and updated to version 3.10.6

## Installation
- Run the setup.py script to build a virtual environment and install all external packages in the created venv.

> Examples:<br> 
>       &emsp;&emsp;- Windows:  `python setup.py venv`<br>
>       &emsp;&emsp;- Linux:  `python3 setup.py venv`

- Once virtual env is built traverse to the (Scripts-Windows or bin-Linux) directory in the environment folder just created.
- For Windows, in the venv\Scripts directory, execute `activate` or `activate.bat` script to activate the virtual environment.
- For Linux, in the venv/bin directory, execute `source activate` to activate the virtual environment.
- If for some reason issues are experienced with the setup script, the alternative is to manually create an environment, activate it, then run pip install -r packages.txt in project root.
- To exit from the virtual environment when finished, execute `deactivate`.

## How to use
- Once the virtual environment is activated, traverse to the directory containing the program and execute in shell
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

-- utils.py --

> db_error_query &nbsp;-&nbsp; Looks up the exact error raised by database error catch-all handler.

> query_db_create &nbsp;-&nbsp; MySQL query to create the Storage table.

> query_item_delete &nbsp;-&nbsp; MySQL query to delete item from storage database.

> query_item_fetch &nbsp;-&nbsp; MySQL query to retrieve item from storage database.

> query_select_all &nbspl-&nbsp; MySQL query to retrieve all contents of storage database.

> query_store_item &nbsp;-&nbsp; MySQL query to store data into the Storage database.

> print_err &nbsp;-&nbsp; Displays error message via stderr for supplied time interval.

## Exit Codes
-- file_database.py --
> 0 - Successful operation (__main__, main_menu)<br>
> 1 - Error occurred acquiring semaphore for database connection (main)<br>
> 2 - Critical error occurred during database operation (main)

-- utils.py --
> 3 - Passed in MySQL query is not a complete statement (query_handler)<br>
> 4 - Fetch flag was set to unknown value (query_handler)