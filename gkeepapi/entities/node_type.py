import enum


class NodeType(enum.Enum):
    """Valid note types."""

    Note = 'NOTE'
    """A Note"""

    List = 'LIST'
    """A List"""

    ListItem = 'LIST_ITEM'
    """A List item"""

    Blob = 'BLOB'
    """A blob (attachment)"""
