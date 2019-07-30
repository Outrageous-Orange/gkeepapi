from .element import Element
from ..entities.role_value import RoleValue
from ..entities.share_request_value import ShareRequestValue


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
