# a node of a tree for determining if different names belong to the same person
class Node:
    def __init__(self, name, parent):
        self.parent = parent
        self.mergeable = True
        self.name = name
        self.children = []  # array of child nodes
        self.children_len = []  # array of the number of names in a full name
        self.longest_possible_child = []  # the name longest name of a child (theoretical)

    # add a child to a Node or one of its children
    # this is done to create a tree like structure of similar names
    def add_child(self, author):
        # if there are no children then append the child
        if len(self.children) == 0:
            self.children.append(Node(author, self))
            self.children_len.append(len(author.split(" ")))
            self.longest_possible_child = author.split(" ")
        else:
            # check if any of the children names start the same
            # if yes then append the author to the child recursively
            b = True
            for child in self.children:
                if author.startswith(child.name):
                    if b:
                        child.add_child(author)
                        b = False
                    else:
                        print("error there should only be one child that matches with the current author")
            # if no child matches the current author then the current node gets another child
            if b:
                self.children.append(Node(author, self))
                self.children_len.append(len(author.split(" ")))
                split_author = author.split(" ")
                for i in range(len(split_author)):
                    if i < len(self.longest_possible_child):
                        if len(self.longest_possible_child[i]) < len(split_author[i]):
                            self.longest_possible_child[i] = split_author[i]
                    else:
                        self.longest_possible_child.append(split_author[i])

    # figure out if the children can be merged or not
    def set_mergeable(self):
        # check if all node can be merged
        # this is done by figuring out if all names match with the longest possible name
        for child in self.children:
            splitname = child.name.split(" ")
            i = 0
            while i < len(splitname) and self.mergeable:
                if not self.longest_possible_child[i].startswith(splitname[i]):
                    self.mergeable = False
                i += 1
        # if the node can not be merged due to a conflict then all parents also can not be merged
        if not self.mergeable:
            parent = self.parent
            while parent is not None:
                parent.mergeable = False
                parent = parent.parent

    # print a Node and its children recursively
    def print_rec(self):
        for child in self.children:
            child.print_rec()
        print(f"{self.name}: {self.mergeable} {self.longest_possible_child}")
        for child in self.children:
            print(f"  child: {child.name}")
