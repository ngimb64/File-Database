""" Built-in modules """
import os


def dir_check(path: str) -> bool:
    """
    Check if directory exists.

    :param path:  The path of the directory to be checked.
    :return:  Boolean True/False if directory exists/non-exists.
    """
    return os.path.isdir(path)


def file_check(path: str) -> bool:
    """
    Check if file exists.

    :param path:  The path of the file to be checked.
    :return:  Boolean True/False if file exists/non-exists.
    """
    return os.path.isfile(path)


def db_storage(database: str) -> str:
    """
    MySQL query to create the Storage table.

    :param database:  The database where the table will be created.
    :return:  The formatted query.
    """
    return f'CREATE TABLE {database}(name VARCHAR(20) PRIMARY KEY NOT NULL, path TINYTEXT NOT ' \
           f'NULL,ext TINYTEXT NOT NULL, content LONGTEXT NOT NULL);'


def db_store(database: str, name: str, path: str, ext: str, content: str) -> str:
    """
    MySQL query to store data into the Storage database.

    :param database:  The name of the database.
    :param name:  The name of the item to be stored.
    :param path:  The path of the item to be stored.
    :param ext:  The file extension type of the item to be stored.
    :param content:  The content inside the item to be stored.
    :return:  The formatted query.
    """
    return f'INSERT INTO {database} (name, path, ext, content) VALUES (\"{name}\", \"{path}\",' \
           f' \"{ext}\", \"{content}\");'


def db_retrieve(database: str, name: str) -> str:
    """
    MySQL query to retrieve item from storage database.

    :param database:  The name of the database.
    :param name:  The name of the item to be retrieved.
    :return:  The formatted query.
    """
    return f'SELECT name,path,ext,content FROM {database} WHERE name=\"{name}\";'


def db_contents(database: str) -> str:
    """
    MySQL query to retrieve all contents of storage database.

    :param database:  The name of the database.
    :return:  The formatted query.
    """
    return f'SELECT * FROM {database}'


def db_delete(database: str, name: str) -> str:
    """
    MySQL query to delete item from storage database.

    :param database:  The name of the database.
    :param name:  The name of the item to be deleted.
    :return:  The formatted query.
    """
    return f'DELETE FROM {database} WHERE name=\"{name}\"'
