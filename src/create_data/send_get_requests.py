import requests
from concurrent.futures import ThreadPoolExecutor
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list, replacing_print
import time
import threading


# this is inspired by https://python.plainenglish.io/send-http-requests-as-fast-as-possible-in-python-304134d46604
# which helped me decide on which threading solution to use for this code and gave an example which inspired my solution


# send a request to dx.doi.org with the doi of the paper
# this will reroute to another page
# Params: doi is the name of a doi and its DB id
# Returns None and the DB id if something goes wrong with the request
# Returns the rerouted URL and the DB id if the request is successful
def send_req(doi):
    try:
        result = requests.get(f"https://dx.doi.org/{doi[0]}", timeout=10)
    except:
        return None, doi[1]
    return result.url, doi[1]


# for each DOI send requests in order to have a URI for the page that contains more information about the given paper
# The result will be saved in the table
# Params: batch_size gives the information about how many requests will be sent before they are saved.
def send_doi_requests(batch_size):
    connection = establish_connection()
    old_length = -1
    new_length = count_empty_doi_address_rows()
    while old_length != new_length:
        with connection:
            result = connection.execute("""
                SELECT name, id
                From DOI 
                WHERE address is NULL
                ORDER BY id asc
                """)
        result = change_cursor_to_list(result)
        first_part = result[0:batch_size]
        second_part = result[batch_size:]
        max_workers = 100
        while len(first_part) > 0:
            executor = ThreadPoolExecutor(max_workers=max_workers)
            url_list = []
            counter = 0
            start_time = time.time()
            for url in executor.map(send_req, first_part):
                counter += 1
                if counter % 250 == 0:
                    current_time = time.time()
                    replacing_print(f"{counter} {current_time - start_time}")
                url_list.append(url)
            end_time = time.time()
            executor.shutdown(wait=True)
            replacing_print(f"{end_time - start_time}")
            with connection:
                for url in url_list:
                    params = url
                    if url[0]:
                        connection.execute("""
                            UPDATE DOI 
                            SET address = ? 
                            WHERE id = ?
                            """, params)
            first_part = second_part[0:batch_size]
            second_part = second_part[batch_size:]
            if max_workers < 100:
                max_workers += 10
        old_length = new_length
        new_length = count_empty_doi_address_rows()
        replacing_print(f"\n{old_length} {new_length}")


# returns the number of Rows in the DOI table where the web address is null
def count_empty_doi_address_rows():
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT *
            FROM DOI
            WHERE address is NULL
        """)
    return len(change_cursor_to_list(result))
