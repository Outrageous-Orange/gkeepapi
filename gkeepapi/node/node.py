import datetime
import random

import time

from .. import exception
from ..entities.node_type import NodeType
from .element import Element
from .node_annotations import NodeAnnotations
from .node_settings import NodeSettings
from .node_timestamps import NodeTimestamps
from .timestamps_mixin import TimestampsMixin


class Node(Element, TimestampsMixin):
    """Node base class."""

    def __init__(self, id_=None, type_=None, parent_id=None):
        super(Node, self).__init__()

        create_time = time.time()

        self.parent = None
        self.id = self._generateId(create_time) if id_ is None else id_
        self.server_id = None
        self.parent_id = parent_id
        self.type = type_
        self._sort = random.randint(1000000000, 9999999999)
        self._version = None
        self._text = ''
        self._children = {}
        self.timestamps = NodeTimestamps(create_time)
        self.settings = NodeSettings()
        self.annotations = NodeAnnotations()

        # Set if there is no baseVersion in the raw data
        self.moved = False

    @classmethod
    def _generateId(cls, tz):
        return '%x.%016x' % (
            int(tz * 1000),
            random.randint(0x0000000000000000, 0xffffffffffffffff)
        )

    def _load(self, raw):
        super(Node, self)._load(raw)
        # Verify this is a valid type
        NodeType(raw['type'])
        if raw['kind'] not in ['notes#node']:
            logger.warning('Unknown node kind: %s', raw['kind'])

        if 'mergeConflict' in raw:
            raise exception.MergeException(raw)

        self.id = raw['id']
        self.server_id = raw['serverId'] if 'serverId' in raw else self.server_id
        self.parent_id = raw['parentId']
        self._sort = raw['sortValue'] if 'sortValue' in raw else self.sort
        self._version = raw['baseVersion'] if 'baseVersion' in raw else self._version
        self._text = raw['text'] if 'text' in raw else self._text
        self.timestamps.load(raw['timestamps'])
        self.settings.load(raw['nodeSettings'])
        self.annotations.load(raw['annotationsGroup'])

    def save(self, clean=True):
        ret = super(Node, self).save(clean)
        ret['id'] = self.id
        ret['kind'] = 'notes#node'
        ret['type'] = self.type.value
        ret['parentId'] = self.parent_id
        ret['sortValue'] = self._sort
        if not self.moved and self._version is not None:
            ret['baseVersion'] = self._version
        ret['text'] = self._text
        if self.server_id is not None:
            ret['serverId'] = self.server_id
        ret['timestamps'] = self.timestamps.save(clean)
        ret['nodeSettings'] = self.settings.save(clean)
        ret['annotationsGroup'] = self.annotations.save(clean)
        return ret

    @property
    def sort(self):
        """Get the sort id.

        Returns:
            int: Sort id.
        """
        return self._sort

    @sort.setter
    def sort(self, value):
        self._sort = value
        self.touch()

    @property
    def version(self):
        """Get the node version.

        Returns:
            int: Version.
        """
        return self._version

    @property
    def text(self):
        """Get the text value.

        Returns:
            str: Text value.
        """
        return self._text

    @text.setter
    def text(self, value):
        """Set the text value.

        Args:
            value (str): Text value.
        """
        self._text = value
        self.timestamps.edited = datetime.datetime.utcnow()
        self.touch(True)

    @property
    def trashed(self):
        return self.timestamps.trashed > NodeTimestamps.int_to_dt(0)

    @trashed.setter
    def trashed(self, value):
        self.timestamps.trashed = datetime.datetime.utcnow() if value else NodeTimestamps.int_to_dt(0)
        self.touch()

    @property
    def children(self):
        """Get all children.

        Returns:
            list[gkeepapi.Node]: Children nodes.
        """
        return list(self._children.values())

    def get(self, node_id):
        """Get child node with the given ID.

        Args:
            node_id (str): The node ID.

        Returns:
            gkeepapi.Node: Child node.
        """
        return self._children.get(node_id)

    def append(self, node, dirty=True):
        """Add a new child node.

        Args:
            node (gkeepapi.Node): Node to add.
            dirty (bool): Whether this node should be marked dirty.
        """
        self._children[node.id] = node
        node.parent = self
        if dirty:
            self.touch()

        return node

    def remove(self, node, dirty=True):
        """Remove the given child node.

        Args:
            node (gkeepapi.Node): Node to remove.
            dirty (bool): Whether this node should be marked dirty.
        """
        if node.id in self._children:
            self._children[node.id].parent = None
            del self._children[node.id]
        if dirty:
            self.touch()

    @property
    def new(self):
        """Get whether this node has been persisted to the server.

        Returns:
            bool: True if node is new.
        """
        return self.server_id is None

    @property
    def dirty(self):
        return super(Node, self).dirty or self.timestamps.dirty or self.annotations.dirty or self.settings.dirty or any(
            (node.dirty for node in self.children))
