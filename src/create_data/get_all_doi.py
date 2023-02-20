import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print, cleaned_data_path


# Create a Dict of all DOI
# The Dict keys are used as an ordered set the actual value is irrelevant
# Enter the data into the DB
def get_all_doi():
    connection = establish_connection()
    counter = 0
    replacing_print("Searching for DOI")
    # find all DOI
    with open(cleaned_data_path()) as json_file:
        doi_dict = {}
        line = json_file.readline()
        while line:
            counter += 1
            if counter % 25_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            element = json.loads(line)
            doi = element["doi"]
            line = json_file.readline()
            if doi is not None:
                doi_dict[doi] = 1
        replacing_print("Inserting DOI into DB")
        # Enter the DOI into the DB
        with connection:
            for doi in doi_dict:
                params = (doi,)
                connection.execute(f"""
                        INSERT INTO DOI values
                            (NULL,?,NULL);
                        """, params)
            replacing_print(f"All DOI have been found!")

