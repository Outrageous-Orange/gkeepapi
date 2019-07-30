import datetime

from .node_timestamps import NodeTimestamps


class TimestampsMixin(object):
    """A mixin to add methods for updating timestamps."""

    def touch(self, edited=False):
        """Mark the node as dirty.

        Args:
            edited (bool): Whether to set the edited time.
        """
        self._dirty = True
        dt = datetime.datetime.utcnow()
        self.timestamps.updated = dt
        if edited:
            self.timestamps.edited = dt

    @property
    def trashed(self):
        """Get the trashed state.

        Returns:
            bool: Whether this item is trashed.
        """
        return self.timestamps.trashed is not None and self.timestamps.trashed > NodeTimestamps.int_to_dt(0)

    @property
    def deleted(self):
        """Get the deleted state.

        Returns:
            bool: Whether this item is deleted.
        """
        return self.timestamps.deleted is not None and self.timestamps.deleted > NodeTimestamps.int_to_dt(0)

    def delete(self):
        """Mark the item as deleted."""
        self.timestamps.deleted = datetime.datetime.utcnow()
