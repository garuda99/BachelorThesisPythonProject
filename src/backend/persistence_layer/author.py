from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list


# returns the author with id "author_id" from the Database
def get_author_from_db(author_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT a.id, a.name
            FROM AUTHOR a
            WHERE a.id = ?
    """, [author_id])
    return change_cursor_to_list(result)


# returns the authors which contain "name" as a substring of their name
def search_db_for_authors(name):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT a.id, a.name
            FROM AUTHOR a
            WHERE a.name LIKE ?
    """, ["%" + name + "%"])
    return change_cursor_to_list(result)


# returns the harmonized versions of the author with id "author_id"
def name_harmonized_authors(author_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT a.id, a.name
            FROM ALLAUTHORNAMES a
            WHERE a.idOfAuthor = ?
    """, [author_id])
    return change_cursor_to_list(result)


# returns the frequent collaborators of the author with id "author_id"
def frequent_collaborators(author_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""SELECT a.id, a.name, awwa.numberOfPapers
            FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorTwo = a.id
            WHERE (awwa.idOfAuthorOne  = ?)
        UNION 
            SELECT a.id, a.name, awwa.numberOfPapers
            FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorOne = a.id
            WHERE (awwa.idOfAuthorTwo  = ?)
        ORDER BY awwa.numberOfPapers DESC  
    """, [author_id, author_id])
    return change_cursor_to_list(result)


# returns the papers that the author with id "author_id" authored
def papers_for_author(authorId):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT d.id, d.name 
            FROM AUTHOR_DOI_RELATION adr JOIN DOI d ON adr.idOfDOI = d.id 
            WHERE adr.idOfAuthor = ?
        """, (authorId,))
    return change_cursor_to_list(result)
