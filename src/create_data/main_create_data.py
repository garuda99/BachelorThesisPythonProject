from src.create_data.create_sqlite import create_all_tables, establish_connection
from src.create_data.get_all_categories import create_category_dict
from src.create_data.name_harmonize_authors import name_harmonize_authors
from src.create_data.useful_functions import replacing_print, change_cursor_to_list, cleaned_data_path
from src.create_data.create_author_author_relations import create_author_author_relations
from src.create_data.create_category_category_relations import create_category_category_relations
from src.create_data.get_all_doi import get_all_doi
from src.create_data.clean_data import clean_data
from src.create_data.create_category_doi_relationship import create_doi_category_relations
from src.create_data.create_non_harmonized_collaborators import create_non_harmonized_author_author_relations
from src.create_data.add_titles_to_doi import add_titles_to_doi
import os


# The main function of the createData folder
# Everything will be created so that the API has data that can be accessed
def main(db_name = None):
    connection = establish_connection(db_name)
    if not os.path.exists(cleaned_data_path()):
        replacing_print("Cleaning Data")
        clean_data()
    replacing_print("Creating all DB Tables")
    create_all_tables(connection)
    if check_if_table_is_empty("CATEGORY"):
        replacing_print("Starting to Collect Categories")
        create_category_dict()
    if check_if_author_tables_are_empty():
        replacing_print("Getting authors and harmonizing them")
        name_harmonize_authors()
    if check_if_table_is_empty("AUTHOR_WORKS_WITH_AUTHOR"):
        replacing_print("Creating author-author relations")
        create_author_author_relations()
    if check_if_table_is_empty("AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED"):
        replacing_print("Creating author-author-non-harmonized relations")
        create_non_harmonized_author_author_relations()
    if check_if_table_is_empty("CATEGORY_CATEGORY_RELATION"):
        replacing_print("Create category-category relations")
        create_category_category_relations()
    if check_if_table_is_empty("DOI"):
        replacing_print("Get all DOI")
        get_all_doi()
    if check_if_table_is_empty("CATEGORY_DOI_RELATION"):
        create_doi_category_relations()
    if check_if_titles_are_in_doi():
        add_titles_to_doi()


# Checks if a table DOI has title entries
# Returns true if table DOI has not all title entries
# Returns false if the table DOI has all title entries
def check_if_titles_are_in_doi(connection = None):
    if not connection:
        connection = establish_connection()
    with connection:
        result = connection.execute("""
        SELECT *
        FROM DOI
        """)
        if len(change_cursor_to_list(result)[0]) < 4:
            return True
        else:
            result = connection.execute("""
            SELECT COUNT(*)
            FROM DOI
            WHERE title is NULL
            """)
            if change_cursor_to_list(result)[0][0] > 0:
                return True
            else:
                return False


# Checks if a table is empty
# Parameter table_name is the name of the table that should be checked.
# Returns true if table has no entries
# Returns false if the table has one or more entries
def check_if_table_is_empty(table_name, connection = None):
    if not connection:
        connection = establish_connection()
    with connection:
        result = change_cursor_to_list(connection.execute("SELECT COUNT(*) FROM " + table_name))
    if result[0][0] > 0:
        return False
    else:
        return True


# Checks if all author tables are empty
# Returns false if all tables are filled
# Returns true and clears all tables if only some are filled if none are filled then true is also returned
def check_if_author_tables_are_empty(connection = None):
    if not (check_if_table_is_empty("AUTHOR",connection) or check_if_table_is_empty("ALLAUTHORNAMES",connection) or check_if_table_is_empty(
            "AUTHOR_CATEGORY",connection)):
        return False
    if check_if_table_is_empty("AUTHOR",connection) and check_if_table_is_empty("ALLAUTHORNAMES",connection) and check_if_table_is_empty(
            "AUTHOR_CATEGORY",connection):
        return True
    else:
        drop_author_tables(connection)
        create_all_tables(connection)
        return True


# Drops all author tables
def drop_author_tables(connection = None):
    if not connection:
        connection = establish_connection()
    with connection:
        connection.execute("DROP TABLE AUTHOR")
        connection.execute("DROP TABLE ALLAUTHORNAMES")
        connection.execute("DROP TABLE AUTHOR_CATEGORY")


# Runs the main function which runs the all the functions in the correct order
# This is done to extract all the necessary information for the database and API
if __name__ == '__main__':
    main()
