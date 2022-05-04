# Built-in modules #
import os


""" File/Dir handlers """

# Check if directory exists #
def DIR_CHECK(path: str) -> bool:
    return os.path.isdir(path)

# Check if file exists #
def FILE_CHECK(path: str) -> bool:
    return os.path.isfile(path)


""" MySQL database queries """

# Create storage database #
def DB_STORAGE(db: str) -> str:
    return f'CREATE TABLE {db}(name VARCHAR(20) PRIMARY KEY NOT NULL, path TINYTEXT NOT NULL, ' \
                            f'ext TINYTEXT NOT NULL, content LONGTEXT NOT NULL);'

# Store data in storage database #
def DB_STORE(db: str, name: str, path: str, ext: str, content: str) -> str:
    return f'INSERT INTO {db} (name, path, ext, content) VALUES (\"{name}\", \"{path}\", \"{ext}\", \"{content}\");'

# Retrieve item from database #
def DB_RETRIEVE(db: str, name: str) -> str:
    return f'SELECT name,path,ext,content FROM {db} WHERE name=\"{name}\";'

# Enumerate contents of database #
def DB_CONTENTS(db: str) -> str:
    return f'SELECT * FROM {db}'

# Delete item from database #
def DB_DELETE(db: str, name: str) -> str:
    return f'DELETE FROM {db} WHERE name=\"{name}\"'
