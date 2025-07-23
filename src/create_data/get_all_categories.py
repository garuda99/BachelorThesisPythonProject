import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print,cleaned_data_path


# Create a Dict of all categories and how often they occur
# Enter the data into the DB
def create_category_dict(connection = None,db_name = None):
    if not connection:
        connection = establish_connection()
    counter = 0
    replacing_print("Searching for Categories")
    with open(cleaned_data_path(db_name)) as json_file:
        category_dict = {}
        line = json_file.readline()
        # Enter the categories into the Dict
        while line:
            counter += 1
            if counter % 25_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            element = json.loads(line)
            line = json_file.readline()
            categories = element["categories"]
            for category in categories.split(" "):
                if category in category_dict.keys():
                    category_dict[category] += 1
                else:
                    category_dict[category] = 1
        # Save the categories into the DB
        replacing_print("Inserting Categories into DB")
        with connection:
            i = 0
            keys = sorted(category_dict.keys())
            for category in keys:
                i += category_dict[category]
                params = (category, category_dict[category])
                connection.execute(f"""
                    INSERT INTO CATEGORY values
                        (NULL,?,?);
                    """, params)
            replacing_print(f"Total number of Categories found: {i}! Total types of Categories {len(keys)}")


