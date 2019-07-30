import datetime

import time

# from gkeepapi._Element import *
from .element import Element


class NodeTimestamps(Element):
    """Represents the timestamps associated with a :class:`TopLevelNode`."""
    TZ_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, create_time=None):
        super(NodeTimestamps, self).__init__()
        if create_time is None:
            create_time = time.time()

        self._created = self.int_to_dt(create_time)
        self._deleted = self.int_to_dt(0)
        self._trashed = self.int_to_dt(0)
        self._updated = self.int_to_dt(create_time)
        self._edited = self.int_to_dt(create_time)

    def _load(self, raw):
        super(NodeTimestamps, self)._load(raw)
        self._created = self.str_to_dt(raw['created'])
        self._deleted = self.str_to_dt(raw['deleted']) \
            if 'deleted' in raw else None
        self._trashed = self.str_to_dt(raw['trashed']) \
            if 'trashed' in raw else None
        self._updated = self.str_to_dt(raw['updated'])
        self._edited = self.str_to_dt(raw['userEdited']) \
            if 'userEdited' in raw else None

    def save(self, clean=True):
        ret = super(NodeTimestamps, self).save(clean)
        ret['kind'] = 'notes#timestamps'
        ret['created'] = self.dt_to_str(self._created)
        if self._deleted is not None:
            ret['deleted'] = self.dt_to_str(self._deleted)
        if self._trashed is not None:
            ret['trashed'] = self.dt_to_str(self._trashed)
        ret['updated'] = self.dt_to_str(self._updated)
        if self._edited is not None:
            ret['userEdited'] = self.dt_to_str(self._edited)
        return ret

    @classmethod
    def str_to_dt(cls, tzs):
        """Convert a datetime string into an object.

        Params:
            tsz (str): Datetime string.

        Returns:
            datetime.datetime: Datetime.
        """
        return datetime.datetime.strptime(tzs, cls.TZ_FMT)

    @classmethod
    def int_to_dt(cls, tz):
        """Convert a unix timestamp into an object.

        Params:
            ts (int): Unix timestamp.

        Returns:
            datetime.datetime: Datetime.
        """
        return datetime.datetime.utcfromtimestamp(tz)

    @classmethod
    def dt_to_str(cls, dt):
        """Convert a datetime to a str.

        Returns:
            str: Datetime string.
        """
        return dt.strftime(cls.TZ_FMT)

    @classmethod
    def int_to_str(cls, tz):
        """Convert a unix timestamp to a str.

        Returns:
            str: Datetime string.
        """
        return cls.dt_to_str(cls.int_to_dt(tz))

    @property
    def created(self):
        """Get the creation datetime.

        Returns:
            datetime.datetime: Datetime.
        """
        return self._created

    @created.setter
    def created(self, value):
        self._created = value
        self._dirty = True

    @property
    def deleted(self):
        """Get the deletion datetime.

        Returns:
            datetime.datetime: Datetime.
        """
        return self._deleted

    @deleted.setter
    def deleted(self, value):
        self._deleted = value
        self._dirty = True

    @property
    def trashed(self):
        """Get the move-to-trash datetime.

        Returns:
            datetime.datetime: Datetime.
        """
        return self._trashed

    @trashed.setter
    def trashed(self, value):
        self._trashed = value
        self._dirty = True

    @property
    def updated(self):
        """Get the updated datetime.

        Returns:
            datetime.datetime: Datetime.
        """
        return self._updated

    @updated.setter
    def updated(self, value):
        self._updated = value
        self._dirty = True

    @property
    def edited(self):
        """Get the user edited datetime.

        Returns:
            datetime.datetime: Datetime.
        """
        return self._edited

    @edited.setter
    def edited(self, value):
        self._edited = value
        self._dirty = True


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


class NodeCollaborators(Element):
    """Represents the collaborators on a :class:`TopLevelNode`."""

    def __init__(self):
        super(NodeCollaborators, self).__init__()
        self._collaborators = {}

    def __len__(self):
        return len(self._collaborators)

    def load(self, collaborators_raw, requests_raw):  # pylint: disable=arguments-differ
        # Parent method not called.
        if requests_raw and isinstance(requests_raw[-1], bool):
            self._dirty = requests_raw.pop()
        else:
            self._dirty = False
        self._collaborators = {}
        for collaborator in collaborators_raw:
            self._collaborators[collaborator['email']] = RoleValue(collaborator['role'])
        for collaborator in requests_raw:
            self._collaborators[collaborator['email']] = ShareRequestValue(collaborator['type'])

    def save(self, clean=True):
        # Parent method not called.
        collaborators = []
        requests = []
        for email, action in self._collaborators.items():
            if isinstance(action, ShareRequestValue):
                requests.append({'email': email, 'type': action.value})
            else:
                collaborators.append({'email': email, 'role': action.value, 'auxiliary_type': 'None'})
        if not clean:
            requests.append(self._dirty)
        else:
            self._dirty = False
        return (collaborators, requests)

    def add(self, email):
        """Add a collaborator.

        Args:
            str : Collaborator email address.
        """
        if email not in self._collaborators:
            self._collaborators[email] = ShareRequestValue.Add
        self._dirty = True

    def remove(self, email):
        """Remove a Collaborator.

        Args:
            str : Collaborator email address.
        """
        if email in self._collaborators:
            if self._collaborators[email] == ShareRequestValue.Add:
                del self._collaborators[email]
            else:
                self._collaborators[email] = ShareRequestValue.Remove
        self._dirty = True

    def all(self):
        """Get all collaborators.

        Returns:
            List[str]: Collaborators.
        """
        return [email for email, action in self._collaborators.items() if
                action in [RoleValue.Owner, RoleValue.User, ShareRequestValue.Add]]
