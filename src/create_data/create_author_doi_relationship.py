import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print, cleaned_data_path
from src.create_data.name_harmonize_authors import combine_author_name, simplify_author_name
from unidecode import unidecode
import re


# Gather the data to show which Paper(DOI) is authored by which Author
# Enter the gathered Data into the AUTHOR_DOI_RELATION table
def create_author_doi_relationship():
    connection = establish_connection()
    counter = 0
    replacing_print("Searching for Author DOI Relationships")
    with open(cleaned_data_path(), encoding="utf-8") as json_file:
        author_doi_dict = {}
        line = json_file.readline()
        # For each line gather the DOI and save the corresponding authors
        # Important DOIs are not unique within this dataset so if the DOI already exists then the authors will be added
        # to the already existing list
        while line:
            counter += 1
            if counter % 25_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            element = json.loads(line)
            doi = element["doi"]
            line = json_file.readline()
            if doi:
                authors = element["authors_parsed"]
                if doi in author_doi_dict.keys():
                    new_authors = author_doi_dict[doi]
                else:
                    new_authors = []
                for author in authors:
                    author = combine_author_name(author)
                    if len(re.findall("[a-zA-Z]", unidecode(author))) > 2:
                        new_authors.append(author)
                author_doi_dict[doi] = sorted(new_authors, key=lambda s: simplify_author_name(unidecode(s.casefold())))
        replacing_print("Inserting Author DOI Relationship into DB")
    # Enter the entries into the table
    # They are entered in groups of maximum 100 entries in order to prevent the sql statement from being too long
    with connection:
        for doi in author_doi_dict.keys():
            authors = author_doi_dict[doi][0:100]
            remaining = author_doi_dict[doi][100:]
            while len(authors) > 0:
                statement = """
                    INSERT OR IGNORE INTO AUTHOR_DOI_RELATION  (idOfDOI,idOfAuthor)
                    SELECT (SELECT d.id
                            FROM DOI d
                            WHERE d.name=?),a.idOfAuthor
                    FROM ALLAUTHORNAMES a
                    WHERE a.name IN ("""
                for i in authors:
                    statement += "?,"
                statement = statement[:-1] + ") GROUP BY a.idOfAuthor"
                connection.execute(statement, ((doi,) + tuple(authors)))
                authors = remaining[0:100]
                remaining = remaining[100:]
