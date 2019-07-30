import logging

import future.utils
import six

from .. import exception

logger = logging.getLogger(__name__)


class Element(object):
    """Interface for elements that can be serialized and deserialized."""

    def __init__(self):
        self._dirty = False

    def _find_discrepancies(self, raw):
        s_raw = self.save(False)
        if isinstance(raw, dict):
            for key, val in raw.items():
                if key in ['parentServerId', 'lastSavedSessionId']:
                    continue
                if key not in s_raw:
                    logger.info('Missing key for %s key %s', type(self), key)
                    continue

                if isinstance(val, (list, dict)):
                    continue

                val_a = raw[key]
                val_b = s_raw[key]
                # Python strftime's 'z' format specifier includes microseconds, but the response from GKeep
                # only has milliseconds. This causes a string mismatch, so we construct datetime objects
                # to properly compare
                if isinstance(val_a, six.string_types) and isinstance(val_b, six.string_types):
                    try:
                        from gkeepapi import NodeTimestamps
                        tval_a = NodeTimestamps.str_to_dt(val_a)
                        tval_b = NodeTimestamps.str_to_dt(val_b)
                        val_a, val_b = tval_a, tval_b
                    except (KeyError, ValueError):
                        pass
                if val_a != val_b:
                    logger.info('Different value for %s key %s: %s != %s', type(self), key, raw[key], s_raw[key])
        elif isinstance(raw, list):
            if len(raw) != len(s_raw):
                logger.info('Different length for %s: %d != %d', type(self), len(raw), len(s_raw))

    def load(self, raw):
        """Unserialize from raw representation. (Wrapper)

        Args:
            raw (dict): Raw.
        Raises:
            ParseException: If there was an error parsing data.
        """
        try:
            self._load(raw)
        except (KeyError, ValueError) as e:
            future.utils.raise_from(exception.ParseException('Parse error in %s' % (type(self)), raw), e)

    def _load(self, raw):
        """Unserialize from raw representation. (Implementation logic)

        Args:
            raw (dict): Raw.
        """
        self._dirty = raw.get('_dirty', False)

    def save(self, clean=True):
        """Serialize into raw representation. Clears the dirty bit by default.

        Args:
            clean (bool): Whether to clear the dirty bit.

        Returns:
            dict: Raw.
        """
        ret = {}
        if clean:
            self._dirty = False
        else:
            ret['_dirty'] = self._dirty
        return ret

    @property
    def dirty(self):
        """Get dirty state.

        Returns:
            str: Whether this element is dirty.
        """
        return self._dirty
