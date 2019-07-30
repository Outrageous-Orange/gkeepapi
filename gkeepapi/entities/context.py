from . import annotation


class Context(annotation.Annotation):
    """Represents a context annotation, which may contain other annotations."""

    def __init__(self):
        super(Context, self).__init__()
        self._entries = {}

    def _load(self, raw):
        super(Context, self)._load(raw)
        self._entries = {}
        from ..node.node_annotations import NodeAnnotations
        for key, entry in raw.get('context', {}).items():
            self._entries[key] = NodeAnnotations.from_json({key: entry})

    def save(self, clean=True):
        ret = super(Context, self).save(clean)
        context = {}
        for entry in self._entries.values():
            context.update(entry.save(clean))
        ret['context'] = context
        return ret

    def all(self):
        """Get all sub annotations.

        Returns:
            List[gkeepapi.entities._Annotation.Annotation]: Sub Annotations.
        """
        return self._entries.values()

    @property
    def dirty(self):
        return super(Context, self).dirty or any((annotation.dirty for annotation in self._entries.values()))
