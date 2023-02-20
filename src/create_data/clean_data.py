import json
from src.create_data.useful_functions import replacing_print, cleaned_data_path, original_data_path


# Removes very similar entries from the original.json Dataset and creates the cleaned.json file
# If a paper is entered twice each time with one of them being a newer Version of the same paper,
#   then one of the entries is removed. (Only if they are very similar)
def clean_data():
    counter = 0
    replacing_print("Searching for Author DOI Relationships")
    doi_dict = {}
    # create a dict which contains a list of ids of the papers that are have the same doi,title,authors and categories
    # most entries will only have one Id (because they are unique)
    # If a dict entry is a list of at least 2 IDs then one might need to be deleted
    with open(original_data_path()) as json_file:
        line = json_file.readline()
        while line:
            counter += 1
            if counter % 25_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            element = json.loads(line)
            total = str(element["doi"]) + element["title"] + str(element["authors_parsed"]) + element["categories"]
            if total in doi_dict.keys():
                doi_dict[total].append(element["id"])
            else:
                doi_dict[total] = [element["id"]]
            line = json_file.readline()
    replacing_print(f"number of entries that could be deleted: {counter - len(doi_dict.keys())}")

    list_of_all_ids = []
    list_of_id_groups = []
    line_dict = {}
    # Create two Lists list_of_all_ids contains all the Ids that must be further inspected
    # list_of_id_groups contains all the Ids that must be further inspected but as a list of lists
    # In each of the sublists the Ids are of papers that are similar/identical
    for i in doi_dict.keys():
        if len(doi_dict[i]) > 1:
            list_of_id_groups.append(doi_dict[i])
            for j in doi_dict[i]:
                list_of_all_ids.append(j)
    # create a line_dict which stores the whole json entry of the Ids which are further analyzed
    with open(original_data_path()) as json_file:
        line = json_file.readline()
        counter = 0
        while line:
            counter += 1
            if counter % 25_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            element = json.loads(line)
            if element["id"] in list_of_all_ids:
                line_dict[element["id"]] = line
            line = json_file.readline()
    # check if the entries are similar enough for all except one to be deleted
    # the IDs of the entries that will be deleted are saved in the delete_list
    delete_list = []
    for i in list_of_id_groups:
        element1 = json.loads(line_dict[i[0]])
        for entry in i[1:]:
            matching = True
            element2 = json.loads(line_dict[entry])
            if element1["journal-ref"] and element2["journal-ref"] and not (
                    element1["journal-ref"] == element2["journal-ref"]):
                matching = "journal-ref"
            if element1["report-no"] and element2["report-no"] and not (element1["report-no"] == element2["report-no"]):
                matching = "report-no"
            if matching == True:
                delete_list.append(element2["id"])
    # write the original data into the newly created cleaned.json file
    # the lines that are deemed to be too similar will be left out
    # this is inspired by https://stackoverflow.com/a/4710090
    with open(original_data_path(), "r", encoding="utf-8") as json_file:
        line = json_file.readline()
        with open(cleaned_data_path(), "w+", encoding="utf-8")as write_file:
            counter = 0
            while line:
                counter += 1
                if counter % 25_000 == 0:
                    replacing_print(f"{counter:_} Lines have been read")
                element = json.loads(line)
                if not element["id"] in delete_list:
                    write_file.write(line)
                line = json_file.readline()
