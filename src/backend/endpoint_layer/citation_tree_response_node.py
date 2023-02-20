# a class which turns the data into a format accepted by the frontend
class CitationTreeResponseNode:
    def __init__(self, node_id, parent_id, name):
        self.node_id = int(node_id)
        self.parent_id = int(parent_id)
        self.name = name

    # Returns the node as a Dict
    # Which is the perfect format for the frontend Tree
    def node_to_dict(self):
        return {"id": self.node_id,
                "parentId": self.parent_id,
                "name": self.name}
