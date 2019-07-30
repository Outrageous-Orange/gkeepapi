import random

import time

from .. import logger
from . import api
from ..node import node_timestamps


class KeepAPI(api.API):
    """Low level Google Keep API client. Mimics the Android Google Keep app.

    You probably want to use :py:class:`Keep` instead.
    """
    API_URL = 'https://www.googleapis.com/notes/v1/'

    def __init__(self, auth=None):
        super(KeepAPI, self).__init__(self.API_URL, auth)

        create_time = time.time()
        self._session_id = self._generateId(create_time)

    @classmethod
    def _generateId(cls, tz):
        return 's--%d--%d' % (
            int(tz * 1000),
            random.randint(1000000000, 9999999999)
        )

    def changes(self, target_version=None, nodes=None, labels=None):
        """Sync up (and down) all changes.

        Args:
            target_version (str): The local change version.
            nodes (List[dict]): A list of nodes to sync up to the server.
            labels (List[dict]): A list of labels to sync up to the server.

        Return:
            dict: Description of all changes.

        Raises:
            APIException: If the server returns an error.
        """
        if nodes is None:
            nodes = []
        if labels is None:
            labels = []

        current_time = time.time()

        params = {
            'nodes': nodes,
            'clientTimestamp': node_timestamps.NodeTimestamps.int_to_str(current_time),
            'requestHeader': {
                'clientSessionId': self._session_id,
                'clientPlatform': 'ANDROID',
                'clientVersion': {
                    'major': '9',
                    'minor': '9',
                    'build': '9',
                    'revision': '9'
                },
                'capabilities': [
                    {'type': 'NC'},  # Color support (Send note color)
                    {'type': 'PI'},  # Pinned support (Send note pinned)
                    {'type': 'LB'},  # Labels support (Send note labels)
                    {'type': 'AN'},  # Annotations support (Send annotations)
                    {'type': 'SH'},  # Sharing support
                    {'type': 'DR'},  # Drawing support
                    {'type': 'TR'},  # Trash support (Stop setting the delete timestamp)
                    {'type': 'IN'},  # Indentation support (Send listitem parent)

                    {'type': 'SNB'},  # Allows modification of shared notes?
                    {'type': 'MI'},  # Concise blob info?
                    {'type': 'CO'},  # VSS_SUCCEEDED when off?

                    # TODO: Figure out what these do:
                    # {'type': 'EC'}, # ???
                    # {'type': 'RB'}, # Rollback?
                    # {'type': 'EX'}, # ???
                ]
            },
        }
        if target_version is not None:
            params['targetVersion'] = target_version

        if labels:
            params['userInfo'] = {
                'labels': labels
            }

        logger.debug('Syncing %d labels and %d nodes', len(labels), len(nodes))

        return self.send(
            url=self._base_url + 'changes',
            method='POST',
            json=params
        )
