from src.backend.persistence_layer.citation_network import citation_network
from src.backend.persistence_layer.category import domain_network, categories, search_db_for_categories, \
    category_from_db, \
    get_neighbouring_domain_network_categories, category_cites, category_is_cited_by
from src.backend.persistence_layer.citation_tree import citation_tree
from src.backend.persistence_layer.author import name_harmonized_authors, frequent_collaborators, get_author_from_db, \
    search_db_for_authors, papers_for_author
from src.backend.persistence_layer.doi import search_db_for_doi
import os
from src.backend.exception.validation_exception import ValidationException
from src.backend.exception.empyt_result_exception import EmptyResultException
from src.backend.exception.too_large_result_exception import TooLargeResultException
from flask_api import status


# This file contains the functions that validate the inputs and forward the request to the persistence layer
# all non commented functions: -validate the parameter (if necessary)
#                              -forwards a request from the endpoint layer to the persistence layer
#                              -ensures the result has the right length
#                              -returns the result to the endpoint layer
#                              -throws a ValidationException if the validation fails
#                              -throws a EmptyResultException if the result is empty
#                              -throws a TooLargeResultException if the result has multiple entries
#                                     and only one was expected

def get_author(author_id):
    if not author_id.isnumeric():
        raise ValidationException(f"Invalid Request! {author_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = get_author_from_db(author_id)
    if len(result) == 0:
        raise EmptyResultException(f"Author with id {author_id} does not exist", status.HTTP_404_NOT_FOUND)
    elif len(result) == 1:
        return result
    else:
        raise TooLargeResultException("Multiple authors were found", status.HTTP_400_BAD_REQUEST)


def search_authors(name):
    result = search_db_for_authors(name.lower())
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException(f"No authors with name {name}", status.HTTP_404_NOT_FOUND)


def get_different_spelling_of_same_author(author_id):
    if not author_id.isnumeric():
        raise ValidationException(f"Invalid Request! {author_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = name_harmonized_authors(author_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("No spellings found", status.HTTP_404_NOT_FOUND)


def get_frequent_collaborators(author_id):
    if not author_id.isnumeric():
        raise ValidationException(f"Invalid Request! {author_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = frequent_collaborators(author_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("No collaborators found", status.HTTP_404_NOT_FOUND)


def get_papers_for_author(author_id):
    if not author_id.isnumeric():
        raise ValidationException(f"Invalid Request! {author_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = papers_for_author(author_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("No papers found", status.HTTP_404_NOT_FOUND)


def get_citation_tree(doi_id):
    if not doi_id.isnumeric():
        raise ValidationException(f"Invalid Request! {doi_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = citation_tree(doi_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("No citation tree found", status.HTTP_404_NOT_FOUND)


def search_papers(name):
    result = search_db_for_doi(name.lower())
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException(f"No papers with name {name}", status.HTTP_404_NOT_FOUND)


def get_categories():
    result = categories()
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("No categories found", status.HTTP_404_NOT_FOUND)


def search_categories(name):
    result = search_db_for_categories(name.lower())
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException(f"No category with name {name}", status.HTTP_404_NOT_FOUND)


def get_category(category_id):
    if not category_id.isnumeric():
        raise ValidationException(f"Invalid Request! {category_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = category_from_db(category_id)
    if len(result) == 0:
        raise EmptyResultException(f"Category with id {category_id} does not exist", status.HTTP_404_NOT_FOUND)
    elif len(result) == 1:
        return result
    else:
        raise TooLargeResultException("Multiple categories were found", status.HTTP_400_BAD_REQUEST)


def get_neighbouring_categories(category_id):
    if not category_id.isnumeric():
        raise ValidationException(f"Invalid Request! {category_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = get_neighbouring_domain_network_categories(category_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("Category not found", status.HTTP_404_NOT_FOUND)


def get_category_cites(category_id):
    if not category_id.isnumeric():
        raise ValidationException(f"Invalid Request! {category_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = category_cites(category_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("Category not found", status.HTTP_404_NOT_FOUND)


def get_category_cited_by(category_id):
    if not category_id.isnumeric():
        raise ValidationException(f"Invalid Request! {category_id} is not a number", status.HTTP_400_BAD_REQUEST)
    result = category_is_cited_by(category_id)
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("Category not found", status.HTTP_404_NOT_FOUND)


# returns the domain network data
def get_domain_network():
    domain_data = domain_network()
    if len(domain_data) > 0:
        return domain_data
    else:
        raise EmptyResultException("No Domain Network found", status.HTTP_404_NOT_FOUND)


# returns the citation network data
def get_citation_network():
    result = citation_network()
    if len(result) > 0:
        return result
    else:
        raise EmptyResultException("No Citation Network found", status.HTTP_404_NOT_FOUND)


# thank you to https://www.youtube.com/watch?v=AXN9gszoti4 which explained how the .ttl format works
# this enabled me to create .ttl files which are used by the GraphDB

# get the domain network and create a .ttl file with the information
# returns the path where the .ttl file is saved
def create_domain_network():
    path = os.path.realpath(__file__)
    path = os.path.dirname(os.path.dirname(path))
    db_path = os.path.join(path, "../../databases/categoryNetwork.ttl")
    try:
        nodes = get_categories()
        edges = get_domain_network()
    except EmptyResultException as e:
        raise EmptyResultException(e.message, e.errorCode)
    with open(db_path, "w+") as ttl_file:
        ttl_file.write("@prefix a: <http://collaborationNode.com/data#> . \n"
                       "@prefix b: <http://collaborationEdge.com/data#> . \n"
                       "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                       "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
        for node in nodes:
            ttl_file.write(f"a:{node[0]} rdfs:label \"{node[1]}\"^^xsd:string .\n")
        ttl_file.write("\n")
        for edge in edges:
            ttl_file.write(f"a:{edge[0]} b:{edge[2]} a:{edge[1]} .\n")
            ttl_file.write(f"a:{edge[1]} b:{edge[2]} a:{edge[0]} .\n")
    return db_path


# get the citation network and create a .ttl file with the information
# returns the path where the .ttl file is saved
def create_citation_network():
    path = os.path.realpath(__file__)
    path = os.path.dirname(os.path.dirname(path))
    db_path = os.path.join(path, "../../databases/citationNetwork.ttl")
    try:
        nodes = get_categories()
        edges = get_citation_network()
    except EmptyResultException as e:
        raise EmptyResultException(e.message, e.errorCode)
    with open(db_path, "w+") as ttl_file:
        ttl_file.write("@prefix a: <http://citationNode.com/data#> . \n"
                      "@prefix b: <http://citationEdge.com/data#> . \n"
                      "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                      "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
        for node in nodes:
            ttl_file.write(f"a:{node[0]} rdfs:label \"{node[1]}\"^^xsd:string .\n")
        ttl_file.write("\n")
        for edge in edges:
            ttl_file.write(f"a:{edge[0]} b:{edge[2]} a:{edge[1]} .\n")
    return db_path
