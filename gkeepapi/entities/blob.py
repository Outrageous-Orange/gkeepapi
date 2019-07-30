import future.utils

from . import blob_type, node_type
from .. import exception
from ..node import node, node_audio, node_drawing, node_image


class Blob(node.Node):
    """Represents a Google Keep blob."""
    _blob_type_map = {
        blob_type.BlobType.Audio: node_audio.NodeAudio,
        blob_type.BlobType.Image: node_image.NodeImage,
        blob_type.BlobType.Drawing: node_drawing.NodeDrawing,
    }

    def __init__(self, parent_id=None, **kwargs):
        super(Blob, self).__init__(type_=node_type.NodeType.Blob, parent_id=parent_id, **kwargs)
        self.blob = None

    @classmethod
    def from_json(cls, raw):
        """Helper to construct a blob from a dict.

        Args:
            raw (dict): Raw blob representation.

        Returns:
            NodeBlob: A NodeBlob object or None.
        """
        from ..node import DEBUG
        if raw is None:
            return None

        bcls = None
        _type = raw.get('type')
        try:
            bcls = cls._blob_type_map[blob_type.BlobType(_type)]
        except (KeyError, ValueError) as e:
            logger.warning('Unknown blob type: %s', _type)
            if DEBUG:
                future.utils.raise_from(exception.ParseException('Parse error for %s' % (_type), raw), e)
            return None
        blob = bcls()
        blob.load(raw)

        return blob

    def _load(self, raw):
        super(Blob, self)._load(raw)
        self.blob = self.from_json(raw.get('blob'))

    def save(self, clean=True):
        ret = super(Blob, self).save(clean)
        if self.blob != None:
            ret['blob'] = self.blob.save(clean)
        return ret
