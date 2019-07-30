from .. import logger

import future.utils

from ..entities import blob
from ..entities.node_type import NodeType
from . import list, list_item, note
from .node import Node
from .. import exception

_type_map = {
    NodeType.Note: note.Note,
    NodeType.List: list.List,
    NodeType.ListItem: list_item.ListItem,
    NodeType.Blob: blob.Blob,
}


def from_json(raw):
    """Helper to construct a node from a dict.

    Args:
        raw (dict): Raw node representation.

    Returns:
        Node: A Node object or None.
    """

    from . import DEBUG
    ncls = None
    _type = raw.get('type')
    try:
        ncls = _type_map[NodeType(_type)]
    except (KeyError, ValueError) as e:
        logger.warning('Unknown node type: %s', _type)
        if DEBUG:
            future.utils.raise_from(exception.ParseException('Parse error for %s' % (_type), raw), e)
        return None
    node = ncls()
    node.load(raw)

    return node
