import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print,cleaned_data_path,change_cursor_to_list,databases_path

if __name__ == '__main__':
    connection = establish_connection("scad")
    labels_pred = []
    labels_true = []
    with connection:
        results = connection.execute("""
            SELECT *
            FROM AUTHOR_GROUND_TRUTH_RELATION
            """)
        results=change_cursor_to_list(results)
        for r in results:
            for i in range(r[2]):
                labels_pred.append(r[0])
                labels_true.append(r[1])
    with open(databases_path()+"/results.txt", "w", encoding="utf-8") as f:
        f.write(",".join(map(str, labels_true)) + "\n")
        f.write(",".join(map(str, labels_pred)) + "\n")
