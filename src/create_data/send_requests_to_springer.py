from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list, replacing_print
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time


# send Requests to springer.com and return the DOIs of the paper it cites
# Params: doi_entry is a tuple of address and id of the paper that is being cited
# Returns: the id of the original paper and all the DOIs of the papers that are being referenced
#          If something goes wrong then a tuple of the original id and None will be returned
def send_req(doi_entry):
    try:
        html = requests.get(doi_entry[0], timeout=4).content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        tags = soup.select("p[class=\"c-article-references__links u-hide-print\"]>a[data-doi]")
    except:
        return doi_entry[1], None
    return doi_entry[1], tags


# This function is here to determine to which Domains are the most common within the DOI Table
# The results were printed into the console
# With this function the decision was made to send requests to springer.
# The decision was made due to the amount of Papers they have
# and the ease of which to extract the DOI of referenced papers
# The most common
def determine_common_doi_domain():
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT address
            FROM DOI
            WHERE address is NOT  NULL
        """)
    urls = change_cursor_to_list(result)
    domain_dict = {}
    for url in urls:
        domain = url[0].split("/")[2]
        if domain in domain_dict.keys():
            domain_dict[domain] += 1
        else:
            domain_dict[domain] = 1
    for domain in domain_dict.keys():
        if domain_dict[domain] > 100000:
            print(f"{domain} {domain_dict[domain]}")


# Save the citation Dict to the Database
# Params: citation_dict is the dict that should be saved
def save_to_db(citation_dict):
    connection = establish_connection()
    with connection:
        for paper in citation_dict.keys():
            sql_statement = f"""
                INSERT INTO DOI_CITES_DOI (doiId, citesDoiId)
                SELECT {paper}, id
                FROM DOI
                WHERE name  IN (""" + str(citation_dict[paper])[1:-1] + ")"
            connection.execute(sql_statement)
            params = (paper,)
            # Insert all the DOIs that have been cited (so that no endless loop occurs)
            connection.execute("""
                INSERT INTO DOI_CITED (doiId)
                VALUES (?)
            """, params)


# Returns the number of springer requests that have yet not been fulfilled
def count_remaining_springer_requests():
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            SELECT count(*)
            FROM DOI
            WHERE address LIKE "%link.springer.com%" AND id NOT IN
                (SELECT doiId
                    FROM DOI_CITED)
        """)
    return change_cursor_to_list(result)[0][0]


# Send requests to springer.com in order to get all the citations
def send_req_to_springer():
    connection = establish_connection()
    # get all the URLs of DOIs that are on Springer.com that have not been requested yet
    max_workers = 40
    while count_remaining_springer_requests() > 0:
        with connection:
            result = connection.execute("""
                SELECT address, id
                FROM DOI
                WHERE address LIKE "%link.springer.com%" AND id NOT IN
                    (SELECT doiId
                    FROM DOI_CITED)
            """)
        doi_entries = change_cursor_to_list(result)[0:1000]
        citation_dict = {}
        executor = ThreadPoolExecutor(max_workers=max_workers)
        counter = 0
        # send all the requests to springer.com
        start = time.time()
        for request_result in executor.map(send_req, doi_entries):
            counter += 1
            if counter % 1 == 0:
                current_time = time.time()
                replacing_print(f"{(current_time - start) / counter * 100} {counter}")
            citation_dict[request_result[0]] = []
            if request_result[1]:
                for tag in request_result[1]:
                    citation_dict[request_result[0]].append(tag["data-doi"])
        if max_workers < 200:
            max_workers += 10
        # save all the data
        save_to_db(citation_dict)
