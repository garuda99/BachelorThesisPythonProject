# a class which turns the data into a format accepted by the frontend
class CitationTreeResponseNode:
    def __init__(self, node_id, parent_id, title):
        self.node_id = int(node_id)
        self.parent_id = int(parent_id)
        self.title = title
        if len(title) > 40:
            self.shortTitle = title[0:40] + "..."
        else:
            self.shortTitle = title

    # Returns the node as a Dict
    # Which is the perfect format for the frontend Tree
    def node_to_dict(self):
        return {"id": self.node_id,
                "parentId": self.parent_id,
                "title": self.title,
                "shortTitle": self.shortTitle}
