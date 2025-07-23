from src.create_data.create_sqlite import create_all_tables, establish_connection
from src.create_data.main_create_data import check_if_table_is_empty, check_if_author_tables_are_empty
from src.create_data.useful_functions import replacing_print, cleaned_data_path, original_data_path
from src.create_data.get_all_categories import create_category_dict
from src.create_data.name_harmonize_authors import name_harmonize_authors
from src.create_data.name_harmonize_authors import combine_author_name
import xmltodict
import json
import os
import re
from unidecode import unidecode


def main():
    db_name= "scad"
    connection = establish_connection(db_name)
    if not os.path.exists(cleaned_data_path(db_name)):
        xml_to_json(original_data_path(db_name), cleaned_data_path(db_name))
    create_all_tables(connection)
    if check_if_table_is_empty("CATEGORY",connection):
        replacing_print("Starting to Collect Categories")
        create_category_dict(connection,db_name)
    if check_if_table_is_empty("AUTHOR_GROUND_TRUTH",connection):
        replacing_print("Starting to Collect Ground Truth")
        collect_ground_truth(connection,db_name)
    if check_if_author_tables_are_empty(connection) and check_if_table_is_empty("AUTHOR_GROUND_TRUTH_RELATION",connection):
        replacing_print("Getting authors and harmonizing them")
        name_harmonize_authors(connection,db_name)
        

def process_authors(authors_obj):
    authors = authors_obj.get("author", [])
    if not isinstance(authors, list):
        authors = [authors]
    authors_parsed = []
    for a in authors:
        name = a.get("@name", "")
        author_id = a.get("@id", "")

        last, first = name.split(",", 1) if "," in name else (name, "")
        last = last.strip()
        first = first.strip()

        authors_parsed.append({
            "author_id": author_id,
            "parsed": [last, first, ""]
        })
    return authors_parsed

def xml_to_json(xml_path, output_path):
    with open(xml_path, 'r', encoding='utf-8') as f:
        data = xmltodict.parse(f.read())
    publications = data['publications']['publication']
    with open(output_path, 'w', encoding='utf-8') as out:
        for pub in publications:
            authors_data = pub.get("authors", {})
            authors = process_authors(authors_data)

            for author in authors:
                entry = {
                    "authors_parsed": [author["parsed"]],
                    "author_id": author["author_id"],
                    "categories": ""
                }
                json.dump(entry, out)
                out.write('\n')


def collect_ground_truth(connection= None, db_name = None):
    if not connection:
        connection = establish_connection()
    with open(cleaned_data_path(db_name), encoding="utf-8") as json_file:
        author_id_dict = {}
        counter = 0
        line = json_file.readline()
        while line:
            element = json.loads(line)
            line = json_file.readline()
            counter += 1
            if counter % 250_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            aut= element["authors_parsed"][0]
            author = combine_author_name(aut)
            author_name = unidecode(author)
            if len(re.findall("[a-zA-Z]", author_name)) > 2 and len(re.findall("[0-9]", author_name)) == 0:
                author_id = element["author_id"]
                if author_id in author_id_dict.keys():
                    author_id_dict[author_id]+=1
                else:
                    author_id_dict[author_id] = 1

    replacing_print("Begin inserting into DB")
    with connection:
        for author_id in sorted(author_id_dict.keys()):
            params = (author_id, author_id_dict[author_id])
            connection.execute("""
                INSERT INTO AUTHOR_GROUND_TRUTH values
                     (Null,?,?);
                """, params)


if __name__ == '__main__':
    main()