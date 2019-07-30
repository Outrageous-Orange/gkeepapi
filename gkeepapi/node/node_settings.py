from ..entities.checked_list_items_policy_value import CheckedListItemsPolicyValue
from ..entities.graveyard_state_value import GraveyardStateValue

from .element import Element
from .new_list_item_placement_value import NewListItemPlacementValue


class NodeSettings(Element):
    """Represents the settings associated with a :class:`TopLevelNode`."""

    def __init__(self):
        super(NodeSettings, self).__init__()
        self._new_listitem_placement = NewListItemPlacementValue.Bottom
        self._graveyard_state = GraveyardStateValue.Collapsed
        self._checked_listitems_policy = CheckedListItemsPolicyValue.Graveyard

    def _load(self, raw):
        super(NodeSettings, self)._load(raw)
        self._new_listitem_placement = NewListItemPlacementValue(raw['newListItemPlacement'])
        self._graveyard_state = GraveyardStateValue(raw['graveyardState'])
        self._checked_listitems_policy = CheckedListItemsPolicyValue(raw['checkedListItemsPolicy'])

    def save(self, clean=True):
        ret = super(NodeSettings, self).save(clean)
        ret['newListItemPlacement'] = self._new_listitem_placement.value
        ret['graveyardState'] = self._graveyard_state.value
        ret['checkedListItemsPolicy'] = self._checked_listitems_policy.value
        return ret

    @property
    def new_listitem_placement(self):
        """Get the default location to insert new listitems.

        Returns:
            gkeepapi.node.NewListItemPlacementValue: Placement.
        """
        return self._new_listitem_placement

    @new_listitem_placement.setter
    def new_listitem_placement(self, value):
        self._new_listitem_placement = value
        self._dirty = True

    @property
    def graveyard_state(self):
        """Get the visibility state for the list graveyard.

        Returns:
            gkeepapi.node.GraveyardStateValue: Visibility.
        """
        return self._graveyard_state

    @graveyard_state.setter
    def graveyard_state(self, value):
        self._graveyard_state = value
        self._dirty = True

    @property
    def checked_listitems_policy(self):
        """Get the policy for checked listitems.

        Returns:
            gkeepapi.node.CheckedListItemsPolicyValue: Policy.
        """
        return self._checked_listitems_policy

    @checked_listitems_policy.setter
    def checked_listitems_policy(self, value):
        self._checked_listitems_policy = value
        self._dirty = True
