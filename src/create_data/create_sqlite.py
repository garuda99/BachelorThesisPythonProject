import sqlite3 as sqlite
import os


# thank you to https://towardsdatascience.com/do-you-know-python-has-a-built-in-database-d553989c87bd for providing
# an easy tutorial on how to use SQLite with python

# create all the Tables and Indexes that are used within this code
def create_all_tables():
    connection = establish_connection()
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS AUTHOR (
                id INTEGER PRIMARY KEY,
                name TEXT
            );
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS author_name_index ON AUTHOR (name);
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS CATEGORY (
                id INTEGER PRIMARY KEY,
                name TEXT,
                numberOfOccurrences INTEGER
            );
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS category_name_index ON CATEGORY (name);
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ALLAUTHORNAMES (
                id INTEGER PRIMARY KEY,
                idOfAuthor INTEGER,
                name TEXT,
                numberOfOccurrences INTEGER,
                FOREIGN KEY (idOfAuthor) REFERENCES AUTHOR (id)
            );
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS allAuthorNames_name_index ON ALLAUTHORNAMES (name);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS allAuthorNames_idOfAuthor_index ON ALLAUTHORNAMES (idOfAuthor);
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS AUTHOR_CATEGORY (
                idOfAuthor INTEGER,
                idOfCategory INTEGER,
                FOREIGN KEY (idOfAuthor) REFERENCES AUTHOR (id),
                FOREIGN KEY (idOfCategory) REFERENCES CATEGORY (id),
                PRIMARY KEY (idOfAuthor, idOfCategory)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS AUTHOR_WORKS_WITH_AUTHOR (
                idOfAuthorOne INTEGER,
                idOfAuthorTwo INTEGER,
                numberOfPapers INTEGER,
                FOREIGN KEY (idOfAuthorOne) REFERENCES AUTHOR (id),
                FOREIGN KEY (idOfAuthorTwo) REFERENCES AUTHOR (id),
                PRIMARY KEY (idOfAuthorOne, idOfAuthorTwo)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED (
                idOfAuthorOne INTEGER,
                idOfAuthorTwo INTEGER,
                numberOfPapers INTEGER,
                FOREIGN KEY (idOfAuthorOne) REFERENCES ALLAUTHORNAMES (id),
                FOREIGN KEY (idOfAuthorTwo) REFERENCES ALLAUTHORNAMES (id),
                PRIMARY KEY (idOfAuthorOne, idOfAuthorTwo)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS CATEGORY_CATEGORY_RELATION (
                idOfCategoryOne INTEGER,
                idOfCategoryTwo INTEGER,
                numberOfSharedPapers INTEGER,
                FOREIGN KEY (idOfCategoryOne) REFERENCES CATEGORY (id),
                FOREIGN KEY (idOfCategoryTwo) REFERENCES CATEGORY (id),
                PRIMARY KEY (idOfCategoryOne, idOfCategoryTwo)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS DOI (
                id INTEGER,
                name TEXT NOT NULL,
                address TEXT,
                PRIMARY KEY (id)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS DOI_CITES_DOI (
                doiId INTEGER,
                citesDoiId INTEGER,
                FOREIGN KEY (doiId) REFERENCES DOI (id),
                FOREIGN KEY (citesDoiId) REFERENCES DOI (id),
                PRIMARY KEY (doiId, citesDoiId)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS DOI_CITED (
                doiId INTEGER,
                PRIMARY KEY (doiId),
                FOREIGN KEY (doiId) REFERENCES DOI (id)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS CATEGORY_DOI_RELATION (
                idOfDOI INTEGER,
                idOfCategory INTEGER,
                PRIMARY KEY (idOfDOI,idOfCategory),
                FOREIGN KEY (idOfDOI) REFERENCES DOI (id),
                FOREIGN KEY (idOfCategory) REFERENCES CATEGORY (id)
            );
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS AUTHOR_DOI_RELATION (
                idOfAuthor INTEGER,
                idOfDOI INTEGER,
                PRIMARY KEY (idOfAuthor,idOfDOI),
                FOREIGN KEY (idOfAuthor) REFERENCES AUTHOR (id),
                FOREIGN KEY (idOfDOI) REFERENCES DOI (id)
            );
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS numberOfPapers_index ON AUTHOR_WORKS_WITH_AUTHOR (numberOfPapers);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idOfAuthorOne_index ON AUTHOR_WORKS_WITH_AUTHOR (idOfAuthorOne);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idOfAuthorTwo_index ON AUTHOR_WORKS_WITH_AUTHOR (idOfAuthorTwo);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS numberOfPapers_non_harmonized_index ON AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED (numberOfPapers);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idOfAuthorOne_non_harmonized_index ON AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED (idOfAuthorOne);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idOfAuthorTwo_non_harmonized_index ON AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED (idOfAuthorTwo);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS numberOfSharedCategoryPapers_index ON CATEGORY_CATEGORY_RELATION (numberOfSharedPapers);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idOfCategoryOne_index ON CATEGORY_CATEGORY_RELATION (idOfCategoryOne);
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idOfCategoryTwo_index ON CATEGORY_CATEGORY_RELATION (idOfCategoryTwo);
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS doiName_index ON DOI (name);
        """)


# Drop all tables and Indexes that are used within this program
def drop_all_tables():
    connection = establish_connection()
    with connection:
        index = ["author_name_index", "category_name_index", "allAuthorNames_name_index", "numberOfPapers_index",
                 "idOfAuthorOne_index", "idOfAuthorTwo_index", "numberOfSharedCategoryPapers_index",
                 "idOfCategoryOne_index", "idOfCategoryTwo_index", "doiName_index", "doiWebAddress_index",
                 "numberOfPapers_non_harmonized_index", "idOfAuthorOne_non_harmonized_index",
                 "idOfAuthorTwo_non_harmonized_index", "allAuthorNames_idOfAuthor_index"]
        for i in index:
            connection.execute(f"""
                DROP INDEX IF EXISTS {i}
            """)
        table = ["AUTHOR", "CATEGORY", "ALLAUTHORNAMES", "AUTHOR_CATEGORY", "AUTHOR_WORKS_WITH_AUTHOR",
                 "CATEGORY_CATEGORY_RELATION", "CATEGORY_DOI_RELATION", "DOI", "DOI_CITED", "DOI_CITES_DOI",
                 "AUTHOR_DOI_RELATION","AUTHOR_WORKS_WITH_AUTHOR_NON_HARMONIZED"]
        for i in table:
            connection.execute(f"""
               DROP TABLE IF EXISTS {i}
           """)


# establish a connection to the database
# returns the connection which can be used to make changes to the DB
def establish_connection():
    path = os.path.realpath(__file__)
    path = os.path.dirname(os.path.dirname(path))
    databasePath = os.path.join(path, "../databases/database.db")
    connection = sqlite.connect(databasePath)
    return connection
