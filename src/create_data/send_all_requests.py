from src.create_data.send_get_requests import send_doi_requests
from src.create_data.send_requests_to_springer import send_req_to_springer
from src.create_data.create_author_doi_relationship import create_author_doi_relationship
from src.create_data.useful_functions import replacing_print
from src.create_data.create_data import check_if_table_is_empty

def main():
    replacing_print("send DOI requests")
    send_doi_requests(5000)
    if check_if_table_is_empty("AUTHOR_DOI_RELATION"):
        replacing_print("create author doi relationship")
        create_author_doi_relationship()
    replacing_print("send requests to springer")
    send_req_to_springer()


if __name__ == '__main__':
    main()