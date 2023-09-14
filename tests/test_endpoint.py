from src.backend.endpoint_layer.endpoint import app


# thank you to https://flask.palletsprojects.com/en/2.2.x/testing/ for showing me a way to test flask applications


def test_author_with_id_1():
    response = app.test_client().get('/author/1')
    assert response.status_code == 200
    assert b"a a calcaterra" in response.data
    assert b"1" in response.data


def test_search_for_author_with_name_simonL():
    response = app.test_client().get("/author/search/Simon Li")
    assert response.status_code == 200
    assert b"de simon lia" in response.data
    assert b"linwood simon lin" in response.data


def test_spellings_of_author_with_id_24903():
    response = app.test_client().get("/author/spellings/24846")
    assert response.status_code == 200
    assert b"Althaus L." in response.data
    assert b"Althaus L. G." in response.data
    assert b"Althaus Leandro" in response.data
    assert b"Althaus Leandro G." in response.data
    assert b"Althaus Leandro Gabriel" in response.data


def test_collaborators_of_author_with_id_5():
    response = app.test_client().get("/author/collaborators/45611")
    assert response.status_code == 200
    assert b"amarian moskov" in response.data
    assert b"auerbach l b" in response.data
    assert b"averett t d" in response.data
    assert b"berthot j" in response.data


def test_get_papers_of_author_with_id_4():
    response = app.test_client().get("/author/papers/4")
    assert response.status_code == 200
    assert b"" in response.data


def test_get_citation_tree_of_doi_with_id_11():
    response = app.test_client().get("/citation/tree/11")
    assert response.status_code == 200
    assert b"10.1086/340293" in response.data
    assert b"10.1086/187753" in response.data
    assert b"10.1051/0004-6361:20031682" in response.data
    assert b"797864" in response.data
    assert b"807918" in response.data
    assert b"833347" in response.data


def test_search_for_paper_with_name():
    response = app.test_client().get("/paper/search/10.1086/34620")
    assert response.status_code == 200
    assert b"10.1086/346200" in response.data
    assert b"10.1086/346201" in response.data
    assert b"10.1086/346202" in response.data
    assert b"10.1086/346204" in response.data
    assert b"10.1086/346205" in response.data
    assert b"10.1086/346206" in response.data
    assert b"802026" in response.data
    assert b"796053" in response.data
    assert b"797984" in response.data
    assert b"801916" in response.data
    assert b"801813" in response.data
    assert b"801818" in response.data


def test_get_category_with_id_1():
    response = app.test_client().get("/category/1")
    assert response.status_code == 200
    assert b"1" in response.data
    assert b"acc-phys" in response.data


def test_get_neighbors_to_category_with_id_1():
    response = app.test_client().get("/category/neighbours/1")
    assert response.status_code == 200
    assert b"124" in response.data
    assert b"78" in response.data
    assert b"12" in response.data
    assert b"80" in response.data
    assert b"168" in response.data
    assert b"5" in response.data
    assert b"146" in response.data
    assert b"physics.acc-ph" in response.data
    assert b"hep-ex" in response.data
    assert b"atom-ph" in response.data
    assert b"hep-ph" in response.data
    assert b"quant-ph" in response.data
    assert b"astro-ph" in response.data
    assert b"plasm-ph" in response.data


def test_which_categories_are_cited_by_category_with_id_2():
    response = app.test_client().get("/category/cites/2")
    assert response.status_code == 200
    assert b"123" in response.data
    assert b"119" in response.data
    assert b"117" in response.data
    assert b"14" in response.data
    assert b"patt-sol" in response.data
    assert b"nlin.PS" in response.data
    assert b"nlin.CD" in response.data
    assert b"chao-dyn" in response.data


def test_which_category_cites_category_with_id_1():
    response = app.test_client().get("/category/citedBy/1")
    assert response.status_code == 200
    assert b"80" in response.data
    assert b"78" in response.data
    assert b"139" in response.data
    assert b"hep-ph" in response.data
    assert b"hep-ex" in response.data
    assert b"physics.ins-det" in response.data


def test_search_for_categories_with_name_econ():
    response = app.test_client().get("/category/search/econ")
    assert response.status_code == 200
    assert b"econ.EM" in response.data
    assert b"econ.GN" in response.data
    assert b"econ.TH" in response.data


def test_collaboration_network_creation():
    response = app.test_client().get("/network/collaboration")
    assert response.status_code == 200
    assert b"categoryNetwork.ttl" in response.data


def test_citation_network_creation():
    response = app.test_client().get("/network/citation")
    assert response.status_code == 200
    assert b"citationNetwork.ttl" in response.data
