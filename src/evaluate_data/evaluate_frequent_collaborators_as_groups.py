from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list, replacing_print


def evaluate_freq_collab_as_groups():
    author_counter = 0
    freq_collab_counter = [0] * 10
    total_collab_counter = 0
    connection = establish_connection()
    with connection:
        authorIds = connection.execute("""
            SELECT id
            FROM AUTHOR
        """)
    authorIds = change_cursor_to_list(authorIds)
    for authorId in authorIds:
        author_counter += 1
        if authorId[0] % 250 == 0:
            replacing_print(f"Number of authors that have been evaluated: {authorId[0]}")
        with connection:
            frequent_collab = connection.execute("""
                SELECT a.idOfAuthorTwo as Author, a.numberOfPapers
                FROM AUTHOR_WORKS_WITH_AUTHOR a
                WHERE a.idOfAuthorOne = ?
                UNION 
                Select b.idOfAuthorOne as Author, b.numberOfPapers 
                FROM AUTHOR_WORKS_WITH_AUTHOR b
                WHERE b.idOfAuthorTwo = ?
                ORDER BY a.numberOfPapers DESC, Author ASC""", [authorId[0], authorId[0]])
            frequent_collab = change_cursor_to_list(frequent_collab)
            if len(frequent_collab) > 1:
                common_collabs = connection.execute("""
                    SELECT a.idOfAuthorTwo as Author, a.numberOfPapers
                    FROM AUTHOR_WORKS_WITH_AUTHOR a
                    WHERE a.idOfAuthorOne = ?
                    UNION 
                    Select b.idOfAuthorOne as Author, b.numberOfPapers 
                    FROM AUTHOR_WORKS_WITH_AUTHOR b
                    WHERE b.idOfAuthorTwo = ?
                    ORDER BY a.numberOfPapers DESC, Author ASC
                """, [frequent_collab[0][0], frequent_collab[0][0]])
                common_collabs = change_cursor_to_list(common_collabs)
                i = 0
                for common_collab in common_collabs:
                    if common_collab[0] == frequent_collab[1][0]:
                        if i < 10:
                            freq_collab_counter[i] += 1
                        else:
                            total_collab_counter += 1
                    i += 1
    print()
    print(f"Final percentage of in common frequent collaborators: ")
    for i, value in enumerate(freq_collab_counter):
        print(f"{i + 1}: {(value / author_counter) * 100}n %")
    print()
    print(f"Percentage of in common infrequent collaborators {(total_collab_counter / author_counter)*100}%")


if __name__ == '__main__':
    evaluate_freq_collab_as_groups()
