from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list, replacing_print


# Evaluates the effect name harmonization has on frequent collaborators and prints the results
def evaluate_name_harmonization_with_frequent_collaborators():
    totalCounter = 0
    differentCounter = 0
    differentCounter2 = 0
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
                f"Number of authors that have been evaluated: {authorId[0]}. Percentage of changed frequent collaborators: {(differentCounter / totalCounter) * 100}%")
        with connection:
            harmonized_authors = connection.execute("""SELECT a.id, a.name, awwa.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorTwo = a.id
                WHERE (awwa.idOfAuthorOne  = ?)
            UNION 
                SELECT a.id, a.name, awwa.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR awwa JOIN AUTHOR a ON awwa.idOfAuthorOne = a.id
                WHERE (awwa.idOfAuthorTwo  = ?)
            ORDER BY awwa.numberOfPapers DESC, a.id ASC
        """, [authorId[0], authorId[0]])
            non_harmonized_authors = connection.execute("""SELECT a.idOfAuthor, a.name, awwanh.numberOfPapers
                    FROM AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED awwanh JOIN ALLAUTHORNAMES a ON awwanh.idOfAuthorTwo = a.id JOIN ALLAUTHORNAMES a2 ON awwanh.idOfAuthorOne = a2.id
                    WHERE (a2.idOfAuthor   = ?)
                UNION 
                    SELECT a.idOfAuthor, a.name, awwanh.numberOfPapers
                    FROM AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED awwanh JOIN ALLAUTHORNAMES a ON awwanh.idOfAuthorOne = a.id JOIN ALLAUTHORNAMES a2 ON awwanh.idOfAuthorTwo = a2.id 
                    WHERE (a2.idOfAuthor = ?)
                ORDER BY awwanh.numberOfPapers DESC, a.idOfAuthor ASC
            """, [authorId[0], authorId[0]])
        harmonized_authors = change_cursor_to_list(harmonized_authors)
        non_harmonized_authors = change_cursor_to_list(non_harmonized_authors)
        i = 0
        b = True
        harmonized_id_list = []
        non_harmonized_id_list = []
        for author in harmonized_authors[:10]:
            harmonized_id_list.append(author[0])
        for author in non_harmonized_authors[:10]:
            non_harmonized_id_list.append(author[0])
        if harmonized_id_list != non_harmonized_id_list:
            differentCounter2 += 1
        for author in harmonized_authors[:10]:
            if i < len(non_harmonized_authors) and author[0] != non_harmonized_authors[i][0]:
                b = False
            i += 1
            while i < len(non_harmonized_authors) and non_harmonized_authors[i - 1][0] == non_harmonized_authors[i][0]:
                i += 1
        totalCounter += 1
        if not b:
            differentCounter += 1
    replacing_print(f"Final percentage of changed frequent collaborators: {(differentCounter / totalCounter) * 100}%")
    print()
    print(
        f"Final percentage of changed frequent collaborators: {(differentCounter2 / totalCounter) * 100}% (not ignoring duplicates)")


if __name__ == '__main__':
    evaluate_name_harmonization_with_frequent_collaborators()
