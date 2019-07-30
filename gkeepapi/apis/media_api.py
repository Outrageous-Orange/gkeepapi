from . import api


class MediaAPI(api.API):
    """Low level Google Media API client. Mimics the Android Google Keep app.

    You probably want to use :py:class:`Keep` instead.
    """
    API_URL = 'https://keep.google.com/media/v2/'

    def __init__(self, auth=None):
        super(MediaAPI, self).__init__(self.API_URL, auth)

    def get(self, blob):
        """Get the canonical link to a media blob.

        Args:
            blob (gkeepapi.node.Blob): The blob.

        Returns:
            str: A link to the media.
        """
        return self._send(
            url=self._base_url + blob.parent.server_id + '/' + blob.server_id + '?s=0',
            method='GET',
            allow_redirects=False
        ).headers.get('Location')
