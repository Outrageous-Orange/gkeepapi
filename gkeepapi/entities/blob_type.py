import enum


class BlobType(enum.Enum):
    """Valid blob types."""

    Audio = 'AUDIO'
    """Audio"""

    Image = 'IMAGE'
    """Image"""

    Drawing = 'DRAWING'
    """Drawing"""
