from ..entities import blob
from ..entities.color_value import ColorValue
from .node import Node
from .node_collaborators import NodeCollaborators
from .node_labels import NodeLabels
from .root import Root


class TopLevelNode(Node):
    """Top level node base class."""
    _TYPE = None

    def __init__(self, **kwargs):
        super(TopLevelNode, self).__init__(parent_id=Root.ID, **kwargs)
        self._color = ColorValue.White
        self._archived = False
        self._pinned = False
        self._title = ''
        self.labels = NodeLabels()
        self.collaborators = NodeCollaborators()

    def _load(self, raw):
        super(TopLevelNode, self)._load(raw)
        self._color = ColorValue(raw['color']) if 'color' in raw else ColorValue.White
        self._archived = raw['isArchived'] if 'isArchived' in raw else False
        self._pinned = raw['isPinned'] if 'isPinned' in raw else False
        self._title = raw['title'] if 'title' in raw else ''
        self.labels.load(raw['labelIds'] if 'labelIds' in raw else [])

        self.collaborators.load(
            raw['roleInfo'] if 'roleInfo' in raw else [],
            raw['shareRequests'] if 'shareRequests' in raw else [],
        )
        self.moved = 'moved' in raw

    def save(self, clean=True):
        ret = super(TopLevelNode, self).save(clean)
        ret['color'] = self._color.value
        ret['isArchived'] = self._archived
        ret['isPinned'] = self._pinned
        ret['title'] = self._title
        labels = self.labels.save(clean)

        collaborators, requests = self.collaborators.save(clean)
        if labels:
            ret['labelIds'] = labels
        ret['collaborators'] = collaborators
        if requests:
            ret['shareRequests'] = requests
        return ret

    @property
    def color(self):
        """Get the node color.

        Returns:
            gkeepapi.node.Color: Color.
        """
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.touch(True)

    @property
    def archived(self):
        """Get the archive state.

        Returns:
            bool: Whether this node is archived.
        """
        return self._archived

    @archived.setter
    def archived(self, value):
        self._archived = value
        self.touch(True)

    @property
    def pinned(self):
        """Get the pin state.

        Returns:
            bool: Whether this node is pinned.
        """
        return self._pinned

    @pinned.setter
    def pinned(self, value):
        self._pinned = value
        self.touch(True)

    @property
    def title(self):
        """Get the title.

        Returns:
            str: Title.
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.touch(True)

    @property
    def url(self):
        """Get the url for this node.

        Returns:
            str: Google Keep url.
        """
        return 'https://keep.google.com/u/0/#' + self._TYPE.value + '/' + self.id

    @property
    def dirty(self):
        return super(TopLevelNode, self).dirty or self.labels.dirty or self.collaborators.dirty

    @property
    def blobs(self):
        """Get all media blobs.

        Returns:
            list[gkeepapi.node.Blob]: Media blobs.
        """
        return [node for node in self.children if isinstance(node, blob.Blob)]
