import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print, cleaned_data_path, change_cursor_to_list


def add_titles_to_doi():
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
            title = element["title"]
            line = json_file.readline()
            if doi is not None and title is not None:
                doi_dict[doi] = title
        replacing_print("Inserting DOI into DB")
        # Enter the DOI into the DB
        with connection:
            result = connection.execute("""
            SELECT *
            FROM DOI
            """)
            if len(change_cursor_to_list(result)[0]) < 4:
                connection.execute("""
                    ALTER TABLE DOI
                    ADD title TEXT""")
            for doi in doi_dict:
                params = (doi_dict[doi], doi)
                connection.execute(f"""
                    UPDATE DOI 
                    SET title = ? 
                    WHERE name = ?
                        """, params)
            replacing_print(f"All Titles have been entered!")


