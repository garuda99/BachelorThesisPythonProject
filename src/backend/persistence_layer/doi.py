from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list


# returns the papers (DOI) where the name is a substring of "name"
def search_db_for_doi(name):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT d.id, d.name
            FROM DOI d
            WHERE d.name LIKE ?
    """, ["%" + name + "%"])
    return change_cursor_to_list(result)


