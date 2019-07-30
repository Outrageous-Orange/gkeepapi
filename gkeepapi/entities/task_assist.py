from . import annotation


class TaskAssist(annotation.Annotation):
    """Unknown."""

    def __init__(self):
        super(TaskAssist, self).__init__()
        self._suggest = None

    def _load(self, raw):
        super(TaskAssist, self)._load(raw)
        self._suggest = raw['taskAssist']['suggestType']

    def save(self, clean=True):
        ret = super(TaskAssist, self).save(clean)
        ret['taskAssist'] = {
            'suggestType': self._suggest
        }
        return ret

    @property
    def suggest(self):
        """Get the suggestion.

        Returns:
            str: The suggestion.
        """
        return self._suggest

    @suggest.setter
    def suggest(self, value):
        self._suggest = value
        self._dirty = True
