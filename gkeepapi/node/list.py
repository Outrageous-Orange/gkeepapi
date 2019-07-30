import six

from ..entities.node_type import NodeType
from .list_item import ListItem
from .top_level_node import TopLevelNode


class List(TopLevelNode):
    """Represents a Google Keep list."""
    _TYPE = NodeType.List

    def __init__(self, **kwargs):
        super(List, self).__init__(type_=self._TYPE, **kwargs)

    def add(self, text, checked=False, sort=None):
        """Add a new item to the list.

        Args:
            text (str): The text.
            checked (bool): Whether this item is checked.
            sort (int): Item id for sorting.
        """
        node = ListItem(parent_id=self.id, parent_server_id=self.server_id)
        node.checked = checked
        node.text = text
        if sort is not None:
            node.sort = sort
        self.append(node, True)
        self.touch(True)
        return node

    @property
    def text(self):
        return '\n'.join((six.text_type(node) for node in self.items))

    @classmethod
    def items_sort(cls, items):
        """Sort list items, taking into account parent items.

        Args:
            items (list[gkeepapi.node.ListItem]): Items to sort.
        Returns:
            list[gkeepapi.node.ListItem]: Sorted items.
        """

        class t(tuple):
            """Tuple with element-based sorting"""

            def __cmp__(self, other):
                for a, b in six.moves.zip_longest(self, other):
                    if a != b:
                        if a is None:
                            return 1
                        if b is None:
                            return -1
                        return a - b
                return 0

            def __lt__(self, other):
                return self.__cmp__(other) < 0

            def __gt_(self, other):
                return self.__cmp__(other) > 0

            def __le__(self, other):
                return self.__cmp__(other) <= 0

            def __ge_(self, other):
                return self.__cmp__(other) >= 0

            def __eq__(self, other):
                return self.__cmp__(other) == 0

            def __ne__(self, other):
                return self.__cmp__(other) != 0

        def key_func(x):
            if x.indented:
                return t((int(x.parent_item.sort), int(x.sort)))
            return t((int(x.sort),))

        return sorted(items, key=key_func, reverse=True)

    def _items(self, checked=None):
        return self.items_sort([
            node for node in self.children
            if isinstance(node, ListItem) and not node.deleted and (
                    checked is None or node.checked == checked
            )
        ])

    def __str__(self):
        return '\n'.join(([self.title] + [six.text_type(node) for node in self.items]))

    @property
    def items(self):
        """Get all listitems.

        Returns:
            list[gkeepapi.node.ListItem]: List items.
        """
        return self._items()

    @property
    def checked(self):
        """Get all checked listitems.

        Returns:
            list[gkeepapi.node.ListItem]: List items.
        """
        return self._items(True)

    @property
    def unchecked(self):
        """Get all unchecked listitems.

        Returns:
            list[gkeepapi.node.ListItem]: List items.
        """
        return self._items(False)
