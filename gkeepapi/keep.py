from uuid import getnode as get_mac

import six

from . import node as _node

from .entities.label import Label
from .node.list import List
from .node.list_item import ListItem
from .node.note import Note

from . import Pattern, logger, exception
from .apis.api_auth import APIAuth
from .apis.keep_api import KeepAPI
from .apis.media_api import MediaAPI
from .apis.reminders_api import RemindersAPI
from .node.root import Root


class Keep(object):
    """High level Google Keep client.

    Stores a local copy of the Keep node tree. To start, first login::

        keep.login('...', '...')

    Individual Notes can be retrieved by id::

        some_note = keep.get('some_id')

    New Notes can be created::

        new_note = keep.createNote()

    These Notes can then be modified::

        some_note.text = 'Test'
        new_note.text = 'Text'

    These changes are automatically detected and synced up with::

        keep.sync()
    """
    OAUTH_SCOPES = 'oauth2:https://www.googleapis.com/auth/memento https://www.googleapis.com/auth/reminders'

    def __init__(self):
        self._keep_api = KeepAPI()
        self._reminders_api = RemindersAPI()
        self._media_api = MediaAPI()
        self._keep_version = None
        self._reminder_version = None
        self._labels = {}
        self._nodes = {}
        self._sid_map = {}

        self._clear()

    def _clear(self):
        self._keep_version = None
        self._reminder_version = None
        self._labels = {}
        self._nodes = {}
        self._sid_map = {}

        root_node = Root()
        self._nodes[Root.ID] = root_node

    def login(self, username, password, state=None, sync=True):
        """Authenticate to Google with the provided credentials & sync.

        Args:
            email (str): The account to use.
            password (str): The account password.
            state (dict): Serialized state to load.

        Raises:
            LoginException: If there was a problem logging in.
        """
        auth = APIAuth(self.OAUTH_SCOPES)

        ret = auth.login(username, password, get_mac())
        if ret:
            self.load(auth, state, sync)

        return ret

    def resume(self, email, master_token, state=None, sync=True):
        """Authenticate to Google with the provided master token & sync.

        Args:
            email (str): The account to use.
            master_token (str): The master token.
            state (dict): Serialized state to load.

        Raises:
            LoginException: If there was a problem logging in.
        """
        auth = APIAuth(self.OAUTH_SCOPES)

        ret = auth.load(email, master_token, android_id=get_mac())
        if ret:
            self.load(auth, state, sync)

        return ret

    def getMasterToken(self):
        """Get master token for resuming.

        Returns:
            str: The master token.
        """
        return self._keep_api.getAuth().getMasterToken()

    def load(self, auth, state=None, sync=True):
        """Authenticate to Google with a prepared authentication object & sync.
        Args:
            auth (APIAuth): Authentication object.
            state (dict): Serialized state to load.

        Raises:
            LoginException: If there was a problem logging in.
        """
        self._keep_api.setAuth(auth)
        self._reminders_api.setAuth(auth)
        self._media_api.setAuth(auth)
        if state is not None:
            self.restore(state)
        if sync:
            self.sync(True)

    def dump(self):
        """Serialize note data.

        Args:
            state (dict): Serialized state to load.
        """
        # Find all nodes manually, as the Keep object isn't aware of new ListItems
        # until they've been synced to the server.
        nodes = []
        for node in self.all():
            nodes.append(node)
            for child in node.children:
                nodes.append(child)
        return {
            'keep_version': self._keep_version,
            'labels': [label.save(False) for label in self.labels()],
            'nodes': [node.save(False) for node in nodes]
        }

    def restore(self, state):
        """Unserialize saved note data.

        Args:
            state (dict): Serialized state to load.
        """
        self._clear()
        self._parseUserInfo({'labels': state['labels']})
        self._parseNodes(state['nodes'])
        self._keep_version = state['keep_version']

    def get(self, node_id):
        """Get a note with the given ID.

        Args:
            node_id (str): The note ID.

        Returns:
            gkeepapi.node.TopLevelNode: The Note or None if not found.
        """
        return \
            self._nodes[Root.ID].get(node_id) or \
            self._nodes[Root.ID].get(self._sid_map.get(node_id))

    def add(self, node):
        """Register a top level node (and its children) for syncing up to the server. There's no need to call this for nodes created by
        :py:meth:`createNote` or :py:meth:`createList` as they are automatically added.

            LoginException: If :py:meth:`login` has not been called.
        Args:
            node (gkeepapi.node.Node): The node to sync.

        Raises:
            Invalid: If the parent node is not found.
        """
        if node.parent_id != Root.ID:
            raise exception.InvalidException('Not a top level node')

        self._nodes[node.id] = node
        self._nodes[node.parent_id].append(node, False)

    def find(self, query=None, func=None, labels=None, colors=None, pinned=None, archived=None,
             trashed=False):  # pylint: disable=too-many-arguments
        """Find Notes based on the specified criteria.

        Args:
            query (Union[_sre.SRE_Pattern, str, None]): A str or regular expression to match against the title and text.
            func (Union[callable, None]): A filter function.
            labels (Union[List[str], None]): A list of label ids or objects to match. An empty list matches notes with no labels.
            colors (Union[List[str], None]): A list of colors to match.
            pinned (Union[bool, None]): Whether to match pinned notes.
            archived (Union[bool, None]): Whether to match archived notes.
            trashed (Union[bool, None]): Whether to match trashed notes.

        Return:
            List[gkeepapi.node.TopLevelNode]: Results.
        """
        if labels is not None:
            labels = [i.id if isinstance(i, Label) else i for i in labels]

        return (node for node in self.all() if
                (query is None or (
                        (isinstance(query, six.string_types) and (query in node.title or query in node.text)) or
                        (isinstance(query, Pattern) and (
                                query.search(node.title) or query.search(node.text)
                        ))
                )) and
                (func is None or func(node)) and
                (labels is None or
                 (not labels and not node.labels.all()) or
                 (any((node.labels.get(i) is not None for i in labels)))
                 ) and \
                (colors is None or node.color in colors) and
                (pinned is None or node.pinned == pinned) and
                (archived is None or node.archived == archived) and
                (trashed is None or node.trashed == trashed)
                )

    def createNote(self, title=None, text=None):
        """Create a new managed note. Any changes to the note will be uploaded when :py:meth:`sync` is called.

        Args:
            title (str): The title of the note.
            text (str): The text of the note.

        Returns:
            gkeepapi.node.List: The new note.
        """
        node = Note()
        if title is not None:
            node.title = title
        if text is not None:
            node.text = text
        self.add(node)
        return node

    def createList(self, title=None, items=None):
        """Create a new list and populate it. Any changes to the note will be uploaded when :py:meth:`sync` is called.

        Args:
            title (str): The title of the list.
            items (List[(str, bool)]): A list of tuples. Each tuple represents the text and checked status of the listitem.

        Returns:
            gkeepapi.node.List: The new list.
        """
        if items is None:
            items = []

        node = List()
        if title is not None:
            node.title = title
        for text, checked in items:
            node.add(text, checked)
        self.add(node)
        return node

    def createLabel(self, name):
        """Create a new label.

        Args:
            name (str): Label name.

        Returns:
            gkeepapi.node.Label: The new label.

        Raises:
            LabelException: If the label exists.
        """
        if self.findLabel(name):
            raise exception.LabelException('Label exists')
        node = Label()
        node.name = name
        self._labels[node.id] = node  # pylint: disable=protected-access
        return node

    def findLabel(self, query, create=False):
        """Find a label with the given name.

        Args:
            name (Union[_sre.SRE_Pattern, str]): A str or regular expression to match against the name.
            create (bool): Whether to create the label if it doesn't exist (only if name is a str).

        Returns:
            Union[gkeepapi.node.Label, None]: The label.
        """
        if isinstance(query, six.string_types):
            query = query.lower()

        for label in self._labels.values():
            if (isinstance(query, six.string_types) and query == label.name.lower()) or \
                    (isinstance(query, Pattern) and query.search(label.name)):
                return label

        return self.createLabel(query) if create and isinstance(query, six.string_types) else None

    def getLabel(self, label_id):
        """Get an existing label.

        Args:
            label_id (str): Label id.

        Returns:
            Union[gkeepapi.node.Label, None]: The label.
        """
        return self._labels.get(label_id)

    def deleteLabel(self, label_id):
        """Deletes a label.

        Args:
            label_id (str): Label id.
        """
        if label_id not in self._labels:
            return

        label = self._labels[label_id]
        label.delete()
        for node in self.all():
            node.labels.remove(label)

    def labels(self):
        """Get all labels.

        Returns:
            List[gkeepapi.node.Label]: Labels
        """
        return self._labels.values()

    def getMediaLink(self, blob):
        """Get the canonical link to media.

        Args:
            blob (gkeepapi.node.Blob): The media resource.

        Returns:
            str: A link to the media.
        """
        return self._media_api.get(blob)

    def all(self):
        """Get all Notes.

        Returns:
            List[gkeepapi.node.TopLevelNode]: Notes
        """
        return self._nodes[Root.ID].children

    def sync(self, resync=False):
        """Sync the local Keep tree with the server. If resyncing, local changes will be detroyed. Otherwise, local changes to notes, labels and reminders will be detected and synced up.

        Args:
            resync (bool): Whether to resync data.

        Raises:
            SyncException: If there is a consistency issue.
        """
        if resync:
            self._clear()

        while True:
            logger.debug('Starting reminder sync: %s', self._reminder_version)
            changes = self._reminders_api.list()

            if 'task' in changes:
                self._parseTasks(changes['task'])

            self._reminder_version = changes['storageVersion']
            logger.debug('Finishing sync: %s', self._reminder_version)
            history = self._reminders_api.history(self._reminder_version)
            if self._reminder_version == history['highestStorageVersion']:
                break

        while True:
            logger.debug('Starting keep sync: %s', self._keep_version)

            labels_updated = any((i.dirty for i in self._labels.values()))
            changes = self._keep_api.changes(
                target_version=self._keep_version,
                nodes=[i.save() for i in self._findDirtyNodes()],
                labels=[i.save() for i in self._labels.values()] if labels_updated else None,
            )

            if changes.get('forceFullResync'):
                raise exception.ResyncRequiredException('Full resync required')

            if changes.get('upgradeRecommended'):
                raise exception.UpgradeRecommendedException('Upgrade recommended')

            if 'userInfo' in changes:
                self._parseUserInfo(changes['userInfo'])

            if 'nodes' in changes:
                self._parseNodes(changes['nodes'])

            self._keep_version = changes['toVersion']
            logger.debug('Finishing sync: %s', self._keep_version)
            if not changes['truncated']:
                break

        if _node.DEBUG:
            self._clean()

    def _parseTasks(self, raw):
        pass

    def _parseNodes(self, raw):  # pylint: disable=too-many-branches
        created_nodes = []
        deleted_nodes = []
        listitem_nodes = []
        for raw_node in raw:
            # Update nodes
            if raw_node['id'] in self._nodes:
                node = self._nodes[raw_node['id']]

                if 'parentId' in raw_node:
                    node.load(raw_node)
                    self._sid_map[node.server_id] = node.id
                    logger.debug('Updated node: %s', raw_node['id'])
                else:
                    deleted_nodes.append(node)

            else:
                node = _node.from_json(raw_node)
                if node is None:
                    logger.debug('Discarded unknown node')
                else:
                    self._nodes[raw_node['id']] = node
                    self._sid_map[node.server_id] = node.id
                    created_nodes.append(node)
                    logger.debug('Created node: %s', raw_node['id'])

            if isinstance(node, ListItem):
                listitem_nodes.append(node)

        # Attach list subitems
        for node in listitem_nodes:
            prev = node.prev_super_list_item_id
            curr = node.super_list_item_id
            if prev == curr:
                continue

            if prev is not None:
                self._nodes[prev].dedent(node, False)

            if curr is not None:
                self._nodes[curr].indent(node, False)

        # Attach created nodes to the tree
        for node in created_nodes:
            logger.debug('Attached node: %s to %s',
                         node.id if node else None,
                         node.parent_id if node else None
                         )
            parent_node = self._nodes.get(node.parent_id)
            parent_node.append(node, False)

        # Detach deleted nodes from the tree
        for node in deleted_nodes:
            node.parent.remove(node)
            del self._nodes[node.id]
            if node.server_id is not None:
                del self._sid_map[node.server_id]
            logger.debug('Deleted node: %s', node.id)

        for node in self.all():
            for label_id in node.labels._labels:  # pylint: disable=protected-access
                node.labels._labels[label_id] = self._labels.get(label_id)  # pylint: disable=protected-access

    def _parseUserInfo(self, raw):
        labels = {}
        if 'labels' in raw:
            for label in raw['labels']:
                if label['mainId'] in self._labels:
                    node = self._labels[label['mainId']]
                    del self._labels[label['mainId']]
                    logger.debug('Updated label: %s', label['mainId'])
                else:
                    node = Label()
                    logger.debug('Created label: %s', label['mainId'])
                node.load(label)
                labels[label['mainId']] = node

        for label_id in self._labels:
            logger.debug('Deleted label: %s', label_id)

        self._labels = labels

    def _findDirtyNodes(self):
        for node in list(self._nodes.values()):
            for child in node.children:
                if not child.id in self._nodes:
                    self._nodes[child.id] = child

        nodes = []
        for node in self._nodes.values():
            if node.dirty:
                nodes.append(node)

        return nodes

    def _clean(self):
        """Recursively check that all nodes are reachable."""
        found_ids = {}
        nodes = [self._nodes[Root.ID]]
        while nodes:
            node = nodes.pop()
            found_ids[node.id] = None
            nodes = nodes + node.children

        for node_id in self._nodes:
            if node_id in found_ids:
                continue
            logger.error('Dangling node: %s', node_id)

        for node_id in found_ids:
            if node_id in self._nodes:
                continue
            logger.error('Unregistered node: %s', node_id)
