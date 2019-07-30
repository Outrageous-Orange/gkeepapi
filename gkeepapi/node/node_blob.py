from .element import Element
from ..entities.blob_type import BlobType


class NodeBlob(Element):
    """Represents a blob descriptor."""
    _TYPE = None

    def __init__(self, type_=None):
        super(NodeBlob, self).__init__()
        self.blob_id = None
        self.type = type_
        self._media_id = None
        self._mimetype = ''
        self._is_uploaded = False

    def _load(self, raw):
        super(NodeBlob, self)._load(raw)
        # Verify this is a valid type
        BlobType(raw['type'])
        self.blob_id = raw.get('blob_id')
        self._media_id = raw.get('media_id')
        self._mimetype = raw.get('mimetype')

    def save(self, clean=True):
        ret = super(NodeBlob, self).save(clean)
        ret['kind'] = 'notes#blob'
        ret['type'] = self.type.value
        if self.blob_id is not None:
            ret['blob_id'] = self.blob_id
        if self._media_id is not None:
            ret['media_id'] = self._media_id
        ret['mimetype'] = self._mimetype
        return ret
