import os


# This file contains a bunch of useful functions that can be used in many files

# Change the cursor a DB returns into a list
# Params: the cursor a DB returns
# Returns the data in the for of a list
def change_cursor_to_list(cursor):
    result_list = []
    for row in cursor:
        result_list.append(row)
    return result_list


# Prints to the console but overwrites the last line written with this function
# This is perfect for counters that need to update
# Params: string is the string that should be printed
def replacing_print(string):
    print(f"\r{string}", end="")


# Returns: the path to the original json file
def original_data_path():
    path = os.path.realpath(__file__)
    path = os.path.dirname(os.path.dirname(path))
    dumpFolderPath = os.path.join(path, "../dumpFolder")
    return os.path.join(dumpFolderPath, "original.json")


# Returns: the path to the cleaned json file
def cleaned_data_path():
    path = os.path.realpath(__file__)
    path = os.path.dirname(os.path.dirname(path))
    dumpFolderPath = os.path.join(path, "../dumpFolder")
    return os.path.join(dumpFolderPath, "cleaned.json")
