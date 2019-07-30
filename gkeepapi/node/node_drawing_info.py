from .element import Element
from .node_image import NodeImage
from .node_timestamps import NodeTimestamps


class NodeDrawingInfo(Element):
    """Represents information about a drawing blob."""

    def __init__(self):
        super(NodeDrawingInfo, self).__init__()
        self.drawing_id = ''
        self.snapshot = NodeImage()
        self._snapshot_fingerprint = ''
        self._thumbnail_generated_time = NodeTimestamps.int_to_dt(0)
        self._ink_hash = ''
        self._snapshot_proto_fprint = ''

    def _load(self, raw):
        super(NodeDrawingInfo, self)._load(raw)
        self.drawing_id = raw['drawingId']
        self.snapshot.load(raw['snapshotData'])
        self._snapshot_fingerprint = raw[
            'snapshotFingerprint'] if 'snapshotFingerprint' in raw else self._snapshot_fingerprint
        self._thumbnail_generated_time = NodeTimestamps.str_to_dt(
            raw['thumbnailGeneratedTime']) if 'thumbnailGeneratedTime' in raw else NodeTimestamps.int_to_dt(0)
        self._ink_hash = raw['inkHash'] if 'inkHash' in raw else ''
        self._snapshot_proto_fprint = raw[
            'snapshotProtoFprint'] if 'snapshotProtoFprint' in raw else self._snapshot_proto_fprint

    def save(self, clean=True):
        ret = super(NodeDrawingInfo, self).save(clean)
        ret['drawingId'] = self.drawing_id
        ret['snapshotData'] = self.snapshot.save(clean)
        ret['snapshotFingerprint'] = self._snapshot_fingerprint
        ret['thumbnailGeneratedTime'] = NodeTimestamps.dt_to_str(self._thumbnail_generated_time)
        ret['inkHash'] = self._ink_hash
        ret['snapshotProtoFprint'] = self._snapshot_proto_fprint
        return ret
