import re
from unidecode import unidecode
from src.create_data.node import Node
import json
from src.create_data.create_sqlite import establish_connection
from src.create_data.useful_functions import replacing_print, cleaned_data_path

# thank you to https://www.w3schools.com/python/python_json.asp for providing a quick overview of the json package

# Gather all author data and insert it into the ALLAUTHORNAMES table
# Match different spellings of Authors to the same author.
# Enter these combined names into the AUTHOR table
# Gather all the categories in which a author works in and enter them into the AUTHOR_CATEGORY table
def name_harmonize_authors():
    connection = establish_connection()
    with open(cleaned_data_path(), encoding="utf-8") as json_file:
        # The author dict will contain a simplified name with all the spellings of an author and the categories that
        # he/she works in
        author_dict = {}
        counter = 0
        category_counter = 0
        author_counter = 0
        line = json_file.readline()
        # For each author collect the original spelling and the categories in which he/she works in
        while line:
            element = json.loads(line)
            line = json_file.readline()
            counter += 1
            if counter % 250_000 == 0:
                replacing_print(f"{counter:_} Lines have been read")
            authors = element["authors_parsed"]
            categories = element["categories"]
            for aut in authors:
                author = combine_author_name(aut)
                new_author = unidecode(author)
                # The name of an Author has to be at least 3 letters long
                if len(re.findall("[a-zA-Z]", new_author)) > 2:
                    # In order to make the matching easier all unnecessary symbols are removed with
                    # the simplify_author_name function
                    new_author = simplify_author_name(new_author)
                    if new_author in author_dict.keys():
                        if author in author_dict[new_author]["authors"].keys():
                            author_dict[new_author]["authors"][author] += 1
                        else:
                            author_dict[new_author]["authors"][author] = 1
                        for category in categories.split(" "):
                            if category in author_dict[new_author]["categories"].keys():
                                author_dict[new_author]["categories"][category] += 1
                            else:
                                author_dict[new_author]["categories"][category] = 1
                    else:
                        author_dict[new_author] = {}
                        author_dict[new_author]["categories"] = {}
                        author_dict[new_author]["authors"] = {}
                        author_dict[new_author]["authors"][author] = 1
                        for category in categories.split(" "):
                            author_dict[new_author]["categories"][category] = 1
                else:
                    author_counter += 1
                    category_counter += len(categories.split(" "))
    # detect if an author has multiple entries that could be combined and combine them
    replacing_print("Begin Author Refining")
    refine(author_dict)
    replacing_print("1 out of 2 Refining steps are complete")
    refine2(author_dict)
    # Enter all the data into the DB
    replacing_print("Begin inserting into DB")
    with connection:
        author_id = 0
        for author_type in sorted(author_dict.keys()):
            author_id += 1
            if author_id % 10_000 == 0:
                replacing_print(f"Inserting into DB! {author_id:_} Authors Completed")
            params = (author_id, author_type)
            connection.execute("""
                INSERT INTO AUTHOR values
                     (?,?);
                """, params)
            for author in author_dict[author_type]["authors"].keys():
                params = (author_id, author, author_dict[author_type]["authors"][author])
                connection.execute("""
                    INSERT INTO ALLAUTHORNAMES values
                        (NULL,?,?,?);
                    """, params)
            for category in author_dict[author_type]["categories"].keys():
                params = (author_id, category)
                connection.execute("""
                    INSERT INTO AUTHOR_CATEGORY (idOfAuthor, idOfCategory) 
                        SELECT ?,id
                        FROM CATEGORY
                        WHERE name =?;
                    """, params)
        replacing_print(f"{author_id} Authors inserted into DB")


# combine two entries into one
# For example "Linder S" and "Linder Simon" is the same person and therefore should only have one entry
# Param: first_author is the name of the author that will be merged into.
# Param: author2 is the author that will be merged to the first_author.
# Param: author_dict is the dict in which the authors will be merged
# Returns the name of the new author entry that contains all the information of the merged authors
def merge_authors(first_author, author2, author_dict):
    # combine the author name data
    for author in author_dict[author2]["authors"].keys():
        number_of_author_appearances = author_dict[author2]["authors"][author]
        if author in author_dict[first_author]["authors"].keys():
            author_dict[first_author]["authors"][author] += number_of_author_appearances
        else:
            author_dict[first_author]["authors"][author] = number_of_author_appearances
    # combine the category data
    for category in author_dict[author2]["categories"].keys():
        number_of_category_appearances = author_dict[author2]["categories"][category]
        if category in author_dict[first_author]["categories"].keys():
            author_dict[first_author]["categories"][category] += number_of_category_appearances
        else:
            author_dict[first_author]["categories"][category] = number_of_category_appearances
    # remove that entry that was copied into the other
    del author_dict[author2]
    # create a more appropriate name for the remaining entry
    new_name = combine_names(first_author, author2)
    rename_dict(new_name, first_author, author_dict)
    return new_name


# Rename an entry within the author_dict
# Param: new_name is the name the author should have
# Param: old_name is the name the author currently has
# Param: author_dict is the Dict with all the data
def rename_dict(new_name, old_name, author_dict):
    if new_name != old_name:
        if new_name in author_dict:
            print(f"ERROR {new_name} already exists as {old_name}")
        author_dict[new_name] = author_dict.pop(old_name)


# Returns the longer name of two given names which should be used if the names are merged
# Params: name1, name2 the names that need to be compared
# Returns: the longer name
def combine_names(name1, name2):
    if len(name1) > len(name2):
        return name1
    else:
        return name2


# Combine an author name list into a single string
# Param: aut the author list that needs to be combined
# Returns the name of the author as a string
def combine_author_name(aut):
    author = aut[0]
    if aut[1] != "":
        author += " " + aut[1]
    if aut[2] != "":
        author += " " + aut[2]
    return author


# Simplify the name of an Author. This means removing unnecessary symbols and making sure there are no double spaces
# Param: author the name of the author that is simplified
# Returns the simplified name
def simplify_author_name(author):
    author = re.sub("-", " ", author)
    author = re.sub("[\"./,;*~%'\]\[{}=`$^_#+?&@\x7F|]", "", author)
    author = re.sub("<br>", "", author)
    author = re.sub("\\\\", "", author)
    return re.sub(" +", " ", author).strip().lower()


# Combine entries in the author_dict where the names refer to the same author
# Param: author_dict is the dict that is supposed to be refined
def refine(author_dict):
    authors = sorted(author_dict.keys())
    authors_length = len(authors)
    i = 0
    # go through every author and group entry that has the same beginning to the name.
    # "Linder S" will be grouped with "Linder Simon" because they both start with "Linder S"
    while i < authors_length:
        root = Node(authors[i], None)
        i += 1
        # Group the similar names in a tree
        while i < authors_length and authors[i].startswith(root.name):
            root.add_child(authors[i])
            i += 1
        # Figure out which authors can be grouped and merge them
        set_mergeable_rec(root)
        merge_with_parent(root, author_dict)


# Combine entries in the author_dict where the names refer to the same author
# This is just like the refine method but it is slightly more complex
# Param: author_dict is the dict that is supposed to be refined
def refine2(author_dict):
    authors = sorted(author_dict.keys())
    authors_length = len(authors)
    i = 0
    # go through every author
    while i < authors_length:
        author_list = []
        author_list.append(authors[i])
        last_name = authors[i].split(" ")[0]
        i += 1
        # gather all authors with the same last name into the author list
        while i < authors_length and authors[i].split(" ")[0] == last_name:
            author_list.append(authors[i])
            i += 1
        # If there are more than two authors with the same last name then they could possibly be the same person
        if len(author_list) >= 2:
            # The removable_author_list exists in order to prevent an author from being merged twice
            # If an author is merged then the entry is removed from the list and it then can not be merged again
            removable_author_list = author_list.copy()
            # find all authors where each word in the name starts with
            # the same letter as the name in the current author
            for author in author_list:
                split_author = author.split(" ")
                match_string = f"{split_author[0]}"
                for name in split_author[1:]:
                    match_string += " " + str(name[0]) + "[a-zA-Z]{0,}"
                match_string += "$"
                merge_list = [aut for aut in removable_author_list if re.match(match_string, aut)]
                # remove all authors from the merge_list in order to ensure that they can not merge again
                for element in merge_list:
                    removable_author_list.remove(element)
                # if there are multiple authors that may be merged then they have to be analyzed to ensure that there
                # are no conflicts (for example Linder S could be Linder Simon or Linder Stefan)

                # generate the longest possible name that could result in a merge of names
                # "Linder Simon G" and "Linder S Garuda" generates "Linder Simon Garuda"
                if len(merge_list) >= 2:
                    longest_name = merge_list[0].split(" ")
                    for element in merge_list[1:]:
                        element = element.split(" ")
                        for j in range(len(longest_name)):
                            if len(element[j]) > len(longest_name[j]):
                                longest_name[j] = element[j]
                    # if all names of the full name match the names of the longest name then all the names can be merged
                    mergeable = True
                    for element in merge_list:
                        element = element.split(" ")
                        for j in range(len(longest_name)):
                            if not longest_name[j].startswith(element[j]):
                                mergeable = False
                    # merge the names if it is possible
                    if mergeable:
                        for element in merge_list[1:]:
                            merge_list[0] = merge_names(merge_list[0], element, author_dict)


# Recursively check if names of the nodes can be merged and merge them corresponding names in the author_dict
# Params: node is the node that should be merged (and its children as well) if it is allowed to be merged
# Params: author_dict is the dict in which the names need to be merged
def merge_with_parent(node, author_dict):
    for child in node.children:
        merge_with_parent(child, author_dict)
    if (node.parent is not None) and node.parent.mergeable and node.mergeable:
        if [category for category in author_dict[node.name]["categories"] if
            category in author_dict[node.parent.name]["categories"]]:
            node.parent.name = merge_authors(node.parent.name, node.name, author_dict)


# Merge two names in an author_dict
# Params: name1 and name2 are the names that need to be merged
# Params: author_dict is the dict which stores all the authors
# Returns: the name that still exists within the author_dict
def merge_names(name1, name2, author_dict):
    if name1 == name2:
        print(f"ERROR trying to merge the same Name: {name2}")
    if [category for category in author_dict[name1]["categories"] if
        category in author_dict[name2]["categories"]]:
        return merge_authors(name1, name2, author_dict)
    else:
        return name1


# Set all the nodes in a tree to their correct mergeable state.
# This will then indicate if they can be merged or not
# Params: node is the root of the tree which needs to be analyzed
def set_mergeable_rec(node):
    node.set_mergeable()
    for child in node.children:
        set_mergeable_rec(child)
