from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list


# returns the whole citation network
def citation_network():
    connection = establish_connection()
    with connection:
        graph = connection.execute("""
            SELECT cdr.idOfCategory, cdr2.idOfCategory, count(*)
            FROM CATEGORY_DOI_RELATION cdr Join DOI_CITES_DOI dcd  ON cdr.idOfDOI  = dcd.doiId
                JOIN CATEGORY_DOI_RELATION cdr2  ON cdr2.idOfDOI = dcd.citesDoiId 
            GROUP BY cdr.idOfCategory, cdr2.idOfCategory """)
    return change_cursor_to_list(graph)


