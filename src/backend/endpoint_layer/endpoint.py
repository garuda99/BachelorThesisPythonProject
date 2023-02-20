from flask import Flask, Response
import json
from src.backend.validation_layer import validation
from src.backend.exception.validation_exception import ValidationException
from src.backend.exception.empyt_result_exception import EmptyResultException
from src.backend.exception.too_large_result_exception import TooLargeResultException
from src.backend.endpoint_layer.citation_tree_response_node import CitationTreeResponseNode

# thank you to https://flask.palletsprojects.com/en/2.2.x/quickstart/ and
# https://www.softwaretestinghelp.com/python-flask-tutorial/ for providing an easy tutorial on the flask basics
app = Flask(__name__)


# a collection of Endpoints
# all of which return 404 if no return value can be found
# all of which return 400 if the request is not valid

# returns the author with id "author_id"
@app.route("/author/<author_id>")
def get_author(author_id):
    try:
        return generate_id_name_response(validation.get_author(author_id))
    except (EmptyResultException, ValidationException, TooLargeResultException) as e:
        return generate_response(e.message), e.errorCode


# returns the authors which contain "name" as a substring of their name
@app.route("/author/search/<path:name>")
def search_authors(name):
    try:
        return generate_id_name_array_response(validation.search_authors(name))
    except EmptyResultException as e:
        return generate_response(e.message), e.errorCode


# returns the different spellings of an author with id "author_id"
@app.route("/author/spellings/<author_id>")
def get_different_spelling_of_same_author(author_id):
    try:
        return generate_id_name_array_response(validation.get_different_spelling_of_same_author(author_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# get the authors that the author with id "author_id" collaborated with
@app.route("/author/collaborators/<author_id>")
def get_frequent_collaborators(author_id):
    try:
        return generate_id_name_array_response(validation.get_frequent_collaborators(author_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# get the papers (DOI) that the author with id "author_id" authored
@app.route("/author/papers/<author_id>")
def get_papers_for_author(author_id):
    try:
        return generate_id_name_array_response(validation.get_papers_for_author(author_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# for a paper (DOI) return the citationTree with the id "doi_id"
@app.route("/citation/tree/<doi_id>")
def get_citation_tree(doi_id):
    try:
        return generate_citation_tree_response(doi_id, validation.get_citation_tree(doi_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# returns papers (DOI) where the "name" is a substring of the DOI
@app.route("/paper/search/<path:name>")
def search_papers(name):
    try:
        return generate_id_name_array_response(validation.search_papers(name))
    except EmptyResultException as e:
        return generate_response(e.message), e.errorCode


# returns the category with id "category_id"
@app.route("/category/<category_id>")
def get_category(category_id):
    try:
        return generate_id_name_response(validation.get_category(category_id))
    except (EmptyResultException, ValidationException, TooLargeResultException) as e:
        return generate_response(e.message), e.errorCode


# returns the categories which neighbor the category with id "category_id" in the Domain Network
@app.route("/category/neighbours/<category_id>")
def get_neighbouring_categories(category_id):
    try:
        return generate_id_name_array_response(validation.get_neighbouring_categories(category_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# returns the categories that the category with id "category_id" cites
@app.route("/category/cites/<category_id>")
def get_category_cites(category_id):
    try:
        return generate_id_name_array_response(validation.get_category_cites(category_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# returns the categories that the category with id "category_id" is cited by
@app.route("/category/citedBy/<category_id>")
def get_category_cited_by(category_id):
    try:
        return generate_id_name_array_response(validation.get_category_cited_by(category_id))
    except (EmptyResultException, ValidationException) as e:
        return generate_response(e.message), e.errorCode


# returns categories where the name is a substring of "name"
@app.route("/category/search/<path:name>")
def search_categories(name):
    try:
        return generate_id_name_array_response(validation.search_categories(name))
    except EmptyResultException as e:
        return generate_response(e.message), e.errorCode


# creates a file with the domain network and returns the path to the file
@app.route("/network/collaboration")
def create_domain_network():
    try:
        return generate_response(validation.create_domain_network())
    except EmptyResultException as e:
        return generate_response(e.message), e.errorCode


# creates a file with the citation network and returns the path to the file
@app.route("/network/citation")
def create_citation_network():
    try:
        return generate_response(validation.create_citation_network())
    except EmptyResultException as e:
        return generate_response(e.message), e.errorCode


# returns a flask response with the data as a json with an id and a name
def generate_id_name_response(data):
    return generate_response({"id": data[0][0], "name": data[0][1]})


# returns a flask response with the data as a json of ids and names
def generate_id_name_array_response(data):
    result_list = []
    for r in data:
        result_list.append({"id": r[0], "name": r[1]})
    return generate_response(result_list)


# returns a flask response with the data as a list of CitationTreeResponseNodes
def generate_citation_tree_response(doiId, data):
    result_list = []
    for entry in data:
        if int(entry[0]) == int(doiId):
            result_list.append(CitationTreeResponseNode(entry[1], -1, entry[2]).node_to_dict())
        else:
            result_list.append(CitationTreeResponseNode(entry[1], entry[0], entry[2]).node_to_dict())
    return generate_response(result_list)


# this is inspired by https://stackoverflow.com/a/25860353 which helped me fix a bug
# change the data into a json and return a flask response
def generate_response(data):
    response = Response(json.dumps(data))
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    return response
