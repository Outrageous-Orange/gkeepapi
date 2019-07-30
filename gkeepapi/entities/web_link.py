from . import annotation


class WebLink(annotation.Annotation):
    """Represents a link annotation on a :class:`TopLevelNode`."""

    def __init__(self):
        super(WebLink, self).__init__()
        self._title = ''
        self._url = ''
        self._image_url = None
        self._provenance_url = ''
        self._description = ''

    def _load(self, raw):
        super(WebLink, self)._load(raw)
        self._title = raw['webLink']['title']
        self._url = raw['webLink']['url']
        self._image_url = raw['webLink']['imageUrl'] if 'imageUrl' in raw['webLink'] else self.image_url
        self._provenance_url = raw['webLink']['provenanceUrl']
        self._description = raw['webLink']['description']

    def save(self, clean=True):
        ret = super(WebLink, self).save(clean)
        ret['webLink'] = {
            'title': self._title,
            'url': self._url,
            'imageUrl': self._image_url,
            'provenanceUrl': self._provenance_url,
            'description': self._description,
        }
        return ret

    @property
    def title(self):
        """Get the link title.

        Returns:
            str: The link title.
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._dirty = True

    @property
    def url(self):
        """Get the link url.

        Returns:
            str: The link url.
        """
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
        self._dirty = True

    @property
    def image_url(self):
        """Get the link image url.

        Returns:
            str: The image url or None.
        """
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        self._image_url = value
        self._dirty = True

    @property
    def provenance_url(self):
        """Get the provenance url.

        Returns:
            url: The provenance url.
        """
        return self._provenance_url

    @provenance_url.setter
    def provenance_url(self, value):
        self._provenance_url = value
        self._dirty = True

    @property
    def description(self):
        """Get the link description.

        Returns:
            str: The link description.
        """
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._dirty = True
