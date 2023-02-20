from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list


# returns the domain Network data
def domain_network():
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT *
            FROM CATEGORY_CATEGORY_RELATION ccr
        """)
    return change_cursor_to_list(result)


# returns all categories
def categories():
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT id, name
            FROM CATEGORY
        """)
    return change_cursor_to_list(result)


# returns the category with id "category_id"
def category_from_db(category_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT id, name
            FROM CATEGORY
            WHERE id = ?
        """, [category_id])
    return change_cursor_to_list(result)


# returns the categories where the name is a substring of "name"
def search_db_for_categories(name):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT id, name
            FROM CATEGORY
            WHERE name LIKE ?
        """, ["%" + name + "%"])
    return change_cursor_to_list(result)


# returns the categories which neighbor the category with id "category_id" in the domain network
def get_neighbouring_domain_network_categories(category_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT c.id, c.name, ccr.numberOfSharedPapers 
            FROM CATEGORY_CATEGORY_RELATION ccr JOIN CATEGORY c ON c.id =ccr.idOfCategoryOne 
            WHERE ccr.idOfCategoryTwo = ?
        UNION 
            SELECT c.id, c.name, ccr.numberOfSharedPapers 
            FROM CATEGORY_CATEGORY_RELATION ccr JOIN CATEGORY c ON c.id = ccr.idOfCategoryTwo 
            WHERE ccr.idOfCategoryOne = ?
        ORDER BY ccr.numberOfSharedPapers DESC 
        """, (category_id, category_id))
    return change_cursor_to_list(result)


# returns the categories which the category with id "category_id" cites
def category_cites(category_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT  c.id, c.name 
            FROM CATEGORY_DOI_RELATION cdr Join DOI_CITES_DOI dcd  ON cdr.idOfDOI  = dcd.doiId
            JOIN CATEGORY_DOI_RELATION cdr2  ON cdr2.idOfDOI = dcd.citesDoiId JOIN CATEGORY c ON c.id =cdr2.idOfCategory 
            WHERE cdr.idOfCategory = ?
            GROUP BY c.id
            ORDER BY COUNT(*) DESC 
        """, [category_id])
    return change_cursor_to_list(result)


# returns the categories which the category with id "category_id" is cited by
def category_is_cited_by(category_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT  c.id, c.name 
            FROM CATEGORY_DOI_RELATION cdr Join DOI_CITES_DOI dcd  ON cdr.idOfDOI  = dcd.doiId
            JOIN CATEGORY_DOI_RELATION cdr2  ON cdr2.idOfDOI = dcd.citesDoiId JOIN CATEGORY c ON c.id =cdr.idOfCategory 
            WHERE cdr2.idOfCategory = ?
            GROUP BY c.id
            ORDER BY COUNT(*) DESC 
        """, [category_id])
    return change_cursor_to_list(result)
