import enum


class RoleValue(enum.Enum):
    """Collaborator role type."""

    Owner = 'O'
    """Note owner."""

    User = 'W'
    """Note collaborator."""
