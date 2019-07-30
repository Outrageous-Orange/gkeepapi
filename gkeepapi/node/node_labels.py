import datetime

from .element import Element
from .node_timestamps import NodeTimestamps


class NodeLabels(Element):
    """Represents the labels on a :class:`TopLevelNode`."""

    def __init__(self):
        super(NodeLabels, self).__init__()
        self._labels = {}

    def __len__(self):
        return len(self._labels)

    def _load(self, raw):
        # Parent method not called.
        if raw and isinstance(raw[-1], bool):
            self._dirty = raw.pop()
        else:
            self._dirty = False
        self._labels = {}
        for raw_label in raw:
            self._labels[raw_label['labelId']] = None

    def save(self, clean=True):
        # Parent method not called.
        ret = [
            {'labelId': label_id, 'deleted': NodeTimestamps.dt_to_str(
                datetime.datetime.utcnow()) if label is None else NodeTimestamps.int_to_str(0)}
            for label_id, label in self._labels.items()]
        if not clean:
            ret.append(self._dirty)
        else:
            self._dirty = False
        return ret

    def add(self, label):
        """Add a label.

        Args:
            label (gkeepapi.node.Label): The Label object.
        """
        self._labels[label.id] = label
        self._dirty = True

    def remove(self, label):
        """Remove a label.

        Args:
            label (gkeepapi.node.Label): The Label object.
        """
        if label.id in self._labels:
            self._labels[label.id] = None
        self._dirty = True

    def get(self, label_id):
        """Get a label by ID.

        Args:
            label_id (str): The label ID.
        """
        return self._labels.get(label_id)

    def all(self):
        """Get all labels.

        Returns:
            List[gkeepapi.node.Label]: Labels.
        """
        return [label for _, label in self._labels.items() if label is not None]
