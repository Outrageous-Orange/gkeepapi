from ..entities.blob_type import BlobType
from .node_blob import NodeBlob


class NodeAudio(NodeBlob):
    """Represents an audio blob."""
    _TYPE = BlobType.Audio

    def __init__(self):
        super(NodeAudio, self).__init__(type_=self._TYPE)
        self._length = None

    def _load(self, raw):
        super(NodeAudio, self)._load(raw)
        self._length = raw.get('length')

    def save(self, clean=True):
        ret = super(NodeAudio, self).save(clean)
        if self._length is not None:
            ret['length'] = self._length
        return ret
