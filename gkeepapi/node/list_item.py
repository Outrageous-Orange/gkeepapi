from .. import exception
from ..entities.node_type import NodeType
from ..node.node import Node


class ListItem(Node):
    """Represents a Google Keep listitem.
    Interestingly enough, :class:`Note`s store their content in a single
    child :class:`ListItem`.
    """

    def __init__(self, parent_id=None, parent_server_id=None, super_list_item_id=None, **kwargs):
        super(ListItem, self).__init__(type_=NodeType.ListItem, parent_id=parent_id, **kwargs)
        self.parent_item = None
        self.parent_server_id = parent_server_id
        self.super_list_item_id = super_list_item_id
        self.prev_super_list_item_id = None
        self._subitems = {}
        self._checked = False

    def _load(self, raw):
        super(ListItem, self)._load(raw)
        self.prev_super_list_item_id = self.super_list_item_id
        self.super_list_item_id = raw.get('superListItemId') or None
        self._checked = raw.get('checked', False)

    def save(self, clean=True):
        ret = super(ListItem, self).save(clean)
        ret['parentServerId'] = self.parent_server_id
        ret['superListItemId'] = self.super_list_item_id
        ret['checked'] = self._checked
        return ret

    def add(self, text, checked=False, sort=None):
        """Add a new sub item to the list. This item must already be attached to a list.

        Args:
            text (str): The text.
            checked (bool): Whether this item is checked.
            sort (int): Item id for sorting.
        """
        if self.parent is None:
            raise exception.InvalidException('Item has no parent')
        node = self.parent.add(text, checked, sort)
        self.indent(node)
        return node

    def indent(self, node, dirty=True):
        """Indent an item. Does nothing if the target has subitems.

        Args:
            node (gkeepapi.node.ListItem): Item to indent.
            dirty (bool): Whether this node should be marked dirty.
        """
        if node.subitems:
            return

        self._subitems[node.id] = node
        node.super_list_item_id = self.id
        node.parent_item = self
        if dirty:
            node.touch(True)

    def dedent(self, node, dirty=True):
        """Dedent an item. Does nothing if the target is not indented under this item.

        Args:
            node (gkeepapi.node.ListItem): Item to dedent.
            dirty (bool): Whether this node should be marked dirty.
        """
        if node.id not in self._subitems:
            return

        del self._subitems[node.id]
        node.super_list_item_id = None
        node.parent_item = None
        if dirty:
            node.touch(True)

    @property
    def subitems(self):
        """Get subitems for this item.

        Returns:
            list[gkeepapi.node.ListItem]: Subitems.
        """
        from gkeepapi.node.List import List
        return List.items_sort(
            self._subitems.values()
        )

    @property
    def indented(self):
        """Get indentation state.

        Returns:
            bool: Whether this item is indented.
        """
        return self.super_list_item_id is not None

    @property
    def checked(self):
        """Get the checked state.

        Returns:
            bool: Whether this item is checked.
        """
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        self.touch(True)

    def __str__(self):
        return u'%s%s %s' % (
            '  ' if self.indented else '',
            u'☑' if self.checked else u'☐',
            self.text
        )
