import random

import time

from ..node.element import Element
from ..node.timestamps_mixin import TimestampsMixin
from ..node.node_timestamps import NodeTimestamps


class Label(Element, TimestampsMixin):
    """Represents a label."""

    def __init__(self):
        super(Label, self).__init__()

        create_time = time.time()

        self.id = self._generateId(create_time)
        self._name = ''
        self.timestamps = NodeTimestamps(create_time)
        self._merged = NodeTimestamps.int_to_dt(0)

    @classmethod
    def _generateId(cls, tz):
        return 'tag.%s.%x' % (
            ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(12)]),
            int(tz * 1000)
        )

    def _load(self, raw):
        super(Label, self)._load(raw)
        self.id = raw['mainId']
        self._name = raw['name']
        self.timestamps.load(raw['timestamps'])
        self._merged = NodeTimestamps.str_to_dt(
            raw['lastMerged']) if 'lastMerged' in raw else NodeTimestamps.int_to_dt(
            0)

    def save(self, clean=True):
        ret = super(Label, self).save(clean)
        ret['mainId'] = self.id
        ret['name'] = self._name
        ret['timestamps'] = self.timestamps.save(clean)
        ret['lastMerged'] = NodeTimestamps.dt_to_str(self._merged)
        return ret

    @property
    def name(self):
        """Get the label name.

        Returns:
            str: Label name.
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.touch(True)

    @property
    def merged(self):
        """Get last merge datetime.

        Returns:
            datetime: Datetime.
        """
        return self._merged

    @merged.setter
    def merged(self, value):
        self._merged = value
        self.touch()

    @property
    def dirty(self):
        return super(Label, self).dirty or self.timestamps.dirty

    def __str__(self):
        return self.name
