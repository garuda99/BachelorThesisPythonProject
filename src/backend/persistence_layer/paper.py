from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list


# returns the paper with id "id"
def get_paper_from_db(paper_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT d.id,d.name ,d.title
            FROM DOI d
            WHERE d.id = ?
    """, [paper_id])
    return change_cursor_to_list(result)
