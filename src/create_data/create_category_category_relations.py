import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print, cleaned_data_path


# Gather the data to show how often Categories share the same paper
# For example Category x and y appear together in 10 papers
# Enter the gathered Data into the CATEGORY_CATEGORY_RELATION table
def create_category_category_relations():
    connection = establish_connection()
    replacing_print("Searching for Category-Category Relations")
    with open(cleaned_data_path()) as json_file:
        category_dict = {}
        line_counter = 0
        line = json_file.readline()
        # gather the data
        while line:
            if line_counter % 25_000 == 0:
                replacing_print(f"{line_counter} Number of Lines have been read")
            line_counter += 1
            element = json.loads(line)
            line = json_file.readline()
            categories = sorted(element["categories"].split(" "))
            for i in range(len(categories) - 1):
                if categories[i] not in category_dict.keys():
                    category_dict[categories[i]] = {}
                    for j in range(i + 1, len(categories)):
                        category_dict[categories[i]][categories[j]] = 1
                else:
                    for j in range(i + 1, len(categories)):
                        if categories[j] not in category_dict[categories[i]].keys():
                            category_dict[categories[i]][categories[j]] = 1
                        else:
                            category_dict[categories[i]][categories[j]] += 1
        replacing_print("Inserting Category-Category relationships into DB")
        # enter the data into the Database
        with connection:
            i = 0
            keys = sorted(category_dict.keys())
            for category in keys:
                for category_two in category_dict[category].keys():
                    i += category_dict[category][category_two]
                    params = (category, category_dict[category][category_two], category_two)
                    connection.execute(f"""
                        INSERT INTO CATEGORY_CATEGORY_RELATION  (idOfCategoryOne, idOfCategoryTwo, numberOfSharedPapers)
                        SELECT (SELECT b.id
                        FROM CATEGORY b
                        WHERE b.name = ?), c.id, ?
                        FROM CATEGORY c
                        WHERE c.name = ?;
                    """, params)
        replacing_print(f"Total number of Category-Category relations found: {i}!")


