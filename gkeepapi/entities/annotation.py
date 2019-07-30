import random

from ..node import element


class Annotation(element.Element):
    """Note annotations base class."""

    def __init__(self):
        super(Annotation, self).__init__()
        self.id = self._generateAnnotationId()

    def _load(self, raw):
        super(Annotation, self)._load(raw)
        self.id = raw.get('id')

    def save(self, clean=True):
        ret = {}
        if self.id is not None:
            ret = super(Annotation, self).save(clean)
        if self.id is not None:
            ret['id'] = self.id
        return ret

    @classmethod
    def _generateAnnotationId(cls):
        return '%08x-%04x-%04x-%04x-%012x' % (
            random.randint(0x00000000, 0xffffffff),
            random.randint(0x0000, 0xffff),
            random.randint(0x0000, 0xffff),
            random.randint(0x0000, 0xffff),
            random.randint(0x000000000000, 0xffffffffffff)
        )
