from .node import Node


class Root(Node):
    """Internal root node."""
    ID = 'root'

    def __init__(self):
        super(Root, self).__init__(id_=self.ID)

    @property
    def dirty(self):
        return False
