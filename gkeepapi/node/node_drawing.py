from ..entities.blob_type import BlobType
from .node_drawing_info import NodeDrawingInfo
from .node_blob import NodeBlob


class NodeDrawing(NodeBlob):
    """Represents a drawing blob."""
    _TYPE = BlobType.Drawing

    def __init__(self):
        super(NodeDrawing, self).__init__(type_=self._TYPE)
        self._extracted_text = ''
        self._extraction_status = ''
        self._drawing_info = None

    def _load(self, raw):
        super(NodeDrawing, self)._load(raw)
        self._extracted_text = raw.get('extracted_text')
        self._extraction_status = raw.get('extraction_status')
        drawing_info = None
        if 'drawingInfo' in raw:
            drawing_info = NodeDrawingInfo()
            drawing_info.load(raw['drawingInfo'])
        self._drawing_info = drawing_info

    def save(self, clean=True):
        ret = super(NodeDrawing, self).save(clean)
        ret['extracted_text'] = self._extracted_text
        ret['extraction_status'] = self._extraction_status
        if self._drawing_info is not None:
            ret['drawingInfo'] = self._drawing_info.save(clean)
        return ret
