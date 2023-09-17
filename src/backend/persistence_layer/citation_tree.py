from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import change_cursor_to_list


# thank you to https://learnsql.com/blog/do-it-in-sql-recursive-tree-traversal/ for showing me how to do recursion in
# SQL

# returns the citation tree for the paper with the id "doi_id"
def citation_tree(doi_id):
    connection = establish_connection()
    with connection:
        result = connection.execute("""
            WITH tree (doiId, citesDoiId,title,depth) AS (
                SELECT dcd.doiId, dcd.citesDoiId,d.title,  1
                FROM DOI_CITES_DOI dcd JOIN DOI d on dcd.citesDoiId = d.id
                WHERE dcd.doiId = ?
                    UNION
                SELECT dcd2.doiId, dcd2.citesDoiId, d2.title, t.depth +1
                FROM DOI_CITES_DOI dcd2 JOIN DOI d2 ON dcd2.citesDoiId =d2.id JOIN tree t ON t.citesDoiId = dcd2.doiId
                WHERE t.depth<10)
            SELECT *
            FROM tree
            """, (doi_id,))
    return change_cursor_to_list(result)
