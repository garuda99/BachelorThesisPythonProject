from src.backend.endpoint_layer.endpoint import app


def test_author_with_id_with_decimal_point():
    response = app.test_client().get('/author/1.0')
    assert response.status_code == 400


def test_spellings_of_author_with_id_as_a_string():
    response = app.test_client().get("/author/spellings/a")
    assert response.status_code == 400


def test_collaborators_of_author_with_id_with_decimal_point():
    response = app.test_client().get("/author/collaborators/5.0")
    assert response.status_code == 400


def test_get_papers_of_author_with_id_with_decimal_point():
    response = app.test_client().get("/author/papers/4.0")
    assert response.status_code == 400
    assert b"" in response.data


def test_get_citation_tree_of_doi_with_id_as_a_string():
    response = app.test_client().get("/citation/tree/v")
    assert response.status_code == 400


def test_get_category_with_id_with_decimal_point():
    response = app.test_client().get("/category/1.0")
    assert response.status_code == 400


def test_get_neighbors_to_category_with_id_as_a_string():
    response = app.test_client().get("/category/neighbours/sdfsf")
    assert response.status_code == 400


def test_which_categories_are_cited_by_category_with_id_with_decimal_point():
    response = app.test_client().get("/category/cites/2.0")
    assert response.status_code == 400


def test_which_category_cites_category_with_id_as_a_string():
    response = app.test_client().get("/category/citedBy/asdawd")
    assert response.status_code == 400
