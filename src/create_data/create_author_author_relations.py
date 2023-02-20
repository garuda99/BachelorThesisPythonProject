from src.create_data.useful_functions import replacing_print, cleaned_data_path
from src.create_data.create_sqlite import establish_connection
import json
from src.create_data.name_harmonize_authors import combine_author_name, simplify_author_name
from unidecode import unidecode
import re


# Gather the data to show which Author works with which Author
# Enter the gathered Data into the AUTHOR_WORKS_WITH_AUTHOR table
def create_author_author_relations():
    connection = establish_connection()
    with open(cleaned_data_path(), encoding="utf-8") as json_file:
        counter = 0
        line = json_file.readline()
        author_dict = {}
        # For each paper it is noted which authors work with which author. This is stored in the author_dict
        # Note that the name of each author is sorted by their simplified format
        # It is also counts the number of times that authors have worked together
        while line:
            element = json.loads(line)
            line = json_file.readline()
            counter += 1
            if counter % 25_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            authors = element["authors_parsed"]
            new_authors = []
            for author in authors:
                author = combine_author_name(author)
                if len(re.findall("[a-zA-Z]", unidecode(author))) > 2:
                    new_authors.append(author)
            new_authors = sorted(new_authors, key=lambda s: simplify_author_name(unidecode(s.casefold())))
            for i in range(len(new_authors) - 1):
                if new_authors[i] not in author_dict.keys():
                    author_dict[new_authors[i]] = {}
                    for j in range(i + 1, len(new_authors)):
                        author_dict[new_authors[i]][new_authors[j]] = 1
                else:
                    for j in range(i + 1, len(new_authors)):
                        if new_authors[j] not in author_dict[new_authors[i]].keys():
                            author_dict[new_authors[i]][new_authors[j]] = 1
                        else:
                            author_dict[new_authors[i]][new_authors[j]] += 1
        # Print all the entries into the database
        replacing_print("Printing into DB")
        counter = 0
        with connection:
            for author in author_dict.keys():
                counter += 1
                if counter % 25 == 0:
                    replacing_print(f"{counter} Author author relationships have been entered into DB")
                params = (author,)
                sql_statement_first_half = """
                        INSERT INTO AUTHOR_WORKS_WITH_AUTHOR (idOfAuthorOne, idOfAuthorTwo, numberOfPapers)
                        SELECT (SELECT a.idOfAuthor
                        FROM ALLAUTHORNAMES a WHERE a.name= ?),b.idOfAuthor,
                        CASE """
                sql_statement_second_half = """
                        FROM ALLAUTHORNAMES b WHERE b.name IN ("""
                for second_author in author_dict[author].keys():
                    if re.search("\"", second_author):
                        name = " ? "
                        params += (second_author, second_author)
                    else:
                        name = f"\"{second_author}\""
                    sql_statement_first_half += f" WHEN b.name = {name} THEN {author_dict[author][second_author]} "
                    sql_statement_second_half += f"{name},"
                sql_statement_first_half += """
                        END AS numberOfPapers"""
                sql_statement = sql_statement_first_half + sql_statement_second_half[:-1] + """
                        )ON CONFLICT (idOfAuthorOne,idOfAuthorTwo)
                         DO UPDATE SET numberOfPapers = numberOfPapers + excluded.numberOfPapers;"""
                connection.execute(sql_statement, params)
        # The idOfAuthorOne should be smaller than idOfAuthorTwo
        # The entries that are the wrong way around will be flipped
        with connection:
            connection.execute("""INSERT INTO AUTHOR_WORKS_WITH_AUTHOR (idOfAuthorTwo, idOfAuthorOne, numberOfPapers)
                SELECT * FROM
                AUTHOR_WORKS_WITH_AUTHOR awwa 
                WHERE idOfAuthorOne > idOfAuthorTwo
                ON CONFLICT (idOfAuthorOne,idOfAuthorTwo) DO UPDATE SET numberOfPapers = numberOfPapers + excluded.numberOfPapers;
            """)
        with connection:
            connection.execute("""DELETE
                FROM AUTHOR_WORKS_WITH_AUTHOR 
                WHERE idOfAuthorTwo < idOfAuthorOne 
            """)
        # If an author works with themselves then the entry should be deleted.
        # Most likely this is the result of bad data
        with connection:
            connection.execute("""DELETE
                FROM AUTHOR_WORKS_WITH_AUTHOR 
                WHERE idOfAuthorTwo = idOfAuthorOne 
            """)
