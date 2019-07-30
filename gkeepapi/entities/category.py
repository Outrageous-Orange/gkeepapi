from . import annotation, category_value


class Category(annotation.Annotation):
    """Represents a category annotation on a :class:`TopLevelNode`."""

    def __init__(self):
        super(Category, self).__init__()
        self._category = None

    def _load(self, raw):
        super(Category, self)._load(raw)
        self._category = category_value.CategoryValue(raw['topicCategory']['category'])

    def save(self, clean=True):
        ret = super(Category, self).save(clean)
        ret['topicCategory'] = {
            'category': self._category.value
        }
        return ret

    @property
    def category(self):
        """Get the category.

        Returns:
            gkeepapi.node.CategoryValue: The category.
        """
        return self._category

    @category.setter
    def category(self, value):
        self._category = value
        self._dirty = True
