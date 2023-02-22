import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print, cleaned_data_path


# Gather the data to show which Categories are used by what Paper(DOI)
# If the DOI appears in more than one entry then only the categories which appear in all entries will be saved
# Enter the gathered Data into the CATEGORY_DOI_RELATION table
def create_doi_category_relations():
    connection = establish_connection()
    replacing_print("Searching for DOI-Category Relations")
    with open(cleaned_data_path()) as json_file:
        doi_dict = {}
        line_counter = 0
        line = json_file.readline()
        # Gather the data
        while line:
            if line_counter % 25_000 == 0:
                replacing_print(f"{line_counter} Number of Lines have been read")
            line_counter += 1
            element = json.loads(line)
            line = json_file.readline()
            categories = sorted(element["categories"].split(" "))
            doi = element["doi"]
            if doi:
                if doi in doi_dict.keys():
                    new_category_list = []
                    for category in categories:
                        if category in doi_dict[doi]:
                            new_category_list.append(category)
                    doi_dict[doi] = new_category_list
                else:
                    doi_dict[doi] = categories
    # Insert the data into the DB
    replacing_print("Inserting DOI-Category relationships into DB")
    with connection:
        for doi in doi_dict.keys():
            connection.execute(""" 
                INSERT INTO CATEGORY_DOI_RELATION (idOfDOI, idOfCategory)
                    SELECT (SELECT d.id
                        FROM DOI d
                        WHERE d.name = ?), c.id 
                    FROM CATEGORY c
                    WHERE c.name  IN (""" + str(doi_dict[doi])[1:-1] + ")", (doi,))
