from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list, replacing_print


def evaluate_frequent_collaborators():
    totalCounter = 0
    differentCounter = 0
    connection = establish_connection()
    with connection:
        authorIds = connection.execute("""
            SELECT id
            FROM AUTHOR
        """)
    authorIds = change_cursor_to_list(authorIds)
    for authorId in authorIds:
        if authorId[0] % 250 == 0:
            replacing_print(
                f"Number of authors that have been evaluated: {authorId[0]}. Percentage of frequent collaborators with different order: {(differentCounter / totalCounter) * 100}%")
        with connection:
            frequent_collaborators = connection.execute("""SELECT a.id, a.name, awwa.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorTwo = a.id
                WHERE (awwa.idOfAuthorOne  = ?)
            UNION 
                SELECT a.id, a.name, awwa.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorOne = a.id
                WHERE (awwa.idOfAuthorTwo  = ?)
            ORDER BY awwa.numberOfPapers DESC, a.name ASC
        """, [authorId[0], authorId[0]])
            collaborators = connection.execute("""SELECT a.id, a.name, awwa.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorTwo = a.id
                WHERE (awwa.idOfAuthorOne  = ?)
            UNION 
                SELECT a.id, a.name, awwa.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorOne = a.id
                WHERE (awwa.idOfAuthorTwo  = ?)
            ORDER BY a.name ASC
            """, [authorId[0], authorId[0]])
        frequent_collaborators = change_cursor_to_list(frequent_collaborators)
        collaborators = change_cursor_to_list(collaborators)
        harmonized_id_list = []
        non_harmonized_id_list = []
        for author in frequent_collaborators[:10]:
            harmonized_id_list.append(author[0])
        for author in collaborators[:10]:
            non_harmonized_id_list.append(author[0])
        if harmonized_id_list != non_harmonized_id_list:
            differentCounter += 1
        totalCounter += 1
    replacing_print(f"Final percentage of frequent collaborators with changed order: {(differentCounter / totalCounter) * 100}%")



if __name__ == '__main__':
    evaluate_frequent_collaborators()

