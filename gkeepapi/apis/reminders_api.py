import time

from . import api


class RemindersAPI(api.API):
    """Low level Google Reminders API client. Mimics the Android Google Keep app.

    You probably want to use :py:class:`Keep` instead.
    """
    API_URL = 'https://www.googleapis.com/reminders/v1internal/reminders/'

    def __init__(self, auth=None):
        super(RemindersAPI, self).__init__(self.API_URL, auth)
        self.static_params = {
            "taskList": [
                {"systemListId": "MEMENTO"},
            ],
            "requestParameters": {
                "userAgentStructured": {
                    "clientApplication": "KEEP",
                    "clientApplicationVersion": {
                        "major": "9", "minor": "9.9.9.9",
                    },
                    "clientPlatform": "ANDROID",
                },
            },
        }

    def create(self):
        """Create a new reminder.
        """
        params = {}
        return self.send(
            url=self._base_url + 'create',
            method='POST',
            json=params
        )

    def list(self, master=True):
        """List current reminders.
        """
        params = {}
        params.update(self.static_params)

        if master:
            params.update({
                "recurrenceOptions": {
                    "collapseMode": "MASTER_ONLY",
                },
                "includeArchived": True,
                "includeDeleted": False,
            })
        else:
            current_time = time.time()
            start_time = int((current_time - (365 * 24 * 60 * 60)) * 1000)
            end_time = int((current_time + (24 * 60 * 60)) * 1000)

            params.update({
                "recurrenceOptions": {
                    "collapseMode": "INSTANCES_ONLY",
                    "recurrencesOnly": True,
                },
                "includeArchived": False,
                "includeCompleted": False,
                "includeDeleted": False,
                "dueAfterMs": start_time,
                "dueBeforeMs": end_time,
                "recurrenceId": [],
            })

        return self.send(
            url=self._base_url + 'list',
            method='POST',
            json=params
        )

    def history(self, storage_version):
        """Get reminder changes.
        """
        params = {
            "storageVersion": storage_version,
            "includeSnoozePresetUpdates": True,
        }
        params.update(self.static_params)

        return self.send(
            url=self._base_url + 'history',
            method='POST',
            json=params
        )

    def update(self):
        """Sync up changes to reminders.
        """
        params = {}
        return self.send(
            url=self._base_url + 'update',
            method='POST',
            json=params
        )
