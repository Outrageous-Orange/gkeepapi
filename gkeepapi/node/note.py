from .list_item import ListItem
from .top_level_node import TopLevelNode
from ..entities.node_type import NodeType


class Note(TopLevelNode):
    """Represents a Google Keep note."""
    _TYPE = NodeType.Note

    def __init__(self, **kwargs):
        super(Note, self).__init__(type_=self._TYPE, **kwargs)

    def _get_text_node(self):
        node = None
        for child_node in self.children:
            if isinstance(child_node, ListItem):
                node = child_node
                break

        return node

    @property
    def text(self):
        node = self._get_text_node()

        if node is None:
            return self._text
        return node.text

    @text.setter
    def text(self, value):
        node = self._get_text_node()
        if node is None:
            node = ListItem(parent_id=self.id)
            self.append(node, True)
        node.text = value
        self.touch(True)

    def __str__(self):
        return '\n'.join([self.title, self.text])
