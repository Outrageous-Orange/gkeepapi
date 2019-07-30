import enum


class ShareRequestValue(enum.Enum):
    """Collaborator change type."""

    Add = 'WR'
    """Grant access."""

    Remove = 'RM'
    """Remove access."""
