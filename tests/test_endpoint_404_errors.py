from src.backend.endpoint_layer.endpoint import app


def test_author_with_id_12374902():
    response = app.test_client().get('/author/12374902')
    assert response.status_code == 404


def test_search_for_author_with_name_simon_linder():
    response = app.test_client().get("/author/search/simon linder")
    assert response.status_code == 404


def test_spellings_of_author_with_id_0():
    response = app.test_client().get("/author/spellings/0")
    assert response.status_code == 404


def test_collaborators_of_author_with_id_0():
    response = app.test_client().get("/author/collaborators/0")
    assert response.status_code == 404


def test_get_papers_of_author_with_id_402384023():
    response = app.test_client().get("/author/papers/402384023")
    assert response.status_code == 404
    assert b"" in response.data


def test_get_citation_tree_of_doi_with_id_1000000():
    response = app.test_client().get("/citation/tree/1000000")
    assert response.status_code == 404


def test_search_for_paper_with_unknown_name():
    response = app.test_client().get("/paper/search/10.1086/3462011")
    assert response.status_code == 404


def test_get_category_with_id_0():
    response = app.test_client().get("/category/0")
    assert response.status_code == 404


def test_get_neighbors_to_category_with_id_1324():
    response = app.test_client().get("/category/neighbours/1324")
    assert response.status_code == 404


def test_which_categories_are_cited_by_category_with_id_0():
    response = app.test_client().get("/category/cites/0")
    assert response.status_code == 404


def test_which_category_cites_category_with_id_11231():
    response = app.test_client().get("/category/citedBy/11231")
    assert response.status_code == 404


def test_search_for_categories_with_name_econ_abc():
    response = app.test_client().get("/category/search/econ.abc")
    assert response.status_code == 404
