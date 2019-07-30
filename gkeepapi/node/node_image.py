from .node_blob import NodeBlob
from ..entities.blob_type import BlobType


class NodeImage(NodeBlob):
    """Represents an image blob."""
    _TYPE = BlobType.Image

    def __init__(self):
        super(NodeImage, self).__init__(type_=self._TYPE)
        self._is_uploaded = False
        self._width = 0
        self._height = 0
        self._byte_size = 0
        self._extracted_text = ''
        self._extraction_status = ''

    def _load(self, raw):
        super(NodeImage, self)._load(raw)
        self._is_uploaded = raw.get('is_uploaded') or False
        self._width = raw.get('width')
        self._height = raw.get('height')
        self._byte_size = raw.get('byte_size')
        self._extracted_text = raw.get('extracted_text')
        self._extraction_status = raw.get('extraction_status')

    def save(self, clean=True):
        ret = super(NodeImage, self).save(clean)
        ret['width'] = self._width
        ret['height'] = self._height
        ret['byte_size'] = self._byte_size
        ret['extracted_text'] = self._extracted_text
        ret['extraction_status'] = self._extraction_status
        return ret

    @property
    def url(self):
        """Get a url to the image.
        Returns:
            str: Image url.
        """
        raise NotImplementedError()
