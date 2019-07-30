from ..entities.category import Category
from ..entities.context import Context
from ..entities.task_assist import TaskAssist
from ..entities.web_link import WebLink
from .element import Element


class NodeAnnotations(Element):
    """Represents the annotation container on a :class:`TopLevelNode`."""

    def __init__(self):
        super(NodeAnnotations, self).__init__()
        self._annotations = {}

    def __len__(self):
        return len(self._annotations)

    @classmethod
    def from_json(cls, raw):
        """Helper to construct an annotation from a dict.

        Args:
            raw (dict): Raw annotation representation.

        Returns:
            Node: An Annotation object or None.
        """
        bcls = None
        if 'webLink' in raw:
            bcls = WebLink
        elif 'topicCategory' in raw:
            bcls = Category
        elif 'taskAssist' in raw:
            bcls = TaskAssist
        elif 'context' in raw:
            bcls = Context

        if bcls is None:
            logger.warning('Unknown annotation type: %s', raw.keys())
            return None
        annotation = bcls()
        annotation.load(raw)

        return annotation

    def all(self):
        """Get all annotations.

        Returns:
            List[gkeepapi.entities._Annotation.Annotation]: Annotations.
        """
        return self._annotations.values()

    def _load(self, raw):
        super(NodeAnnotations, self)._load(raw)
        self._annotations = {}
        if 'annotations' not in raw:
            return

        for raw_annotation in raw['annotations']:
            annotation = self.from_json(raw_annotation)
            self._annotations[annotation.id] = annotation

    def save(self, clean=True):
        ret = super(NodeAnnotations, self).save(clean)
        ret['kind'] = 'notes#annotationsGroup'
        if self._annotations:
            ret['annotations'] = [annotation.save(clean) for annotation in self._annotations.values()]
        return ret

    def _get_category_node(self):
        for annotation in self._annotations.values():
            if isinstance(annotation, Category):
                return annotation
        return None

    @property
    def category(self):
        """Get the category.

        Returns:
            Union[gkeepapi.node.CategoryValue, None]: The category or None.
        """
        node = self._get_category_node()

        return node.category if node is not None else None

    @category.setter
    def category(self, value):
        node = self._get_category_node()
        if value is None:
            if node is not None:
                del self._annotations[node.id]
        else:
            if node is None:
                node = Category()
                self._annotations[node.id] = node

            node.category = value
        self._dirty = True

    @property
    def links(self):
        """Get all links.

        Returns:
            list[gkeepapi.entities.WebLink.WebLink]: A list of links.
        """
        return [annotation for annotation in self._annotations.values()
                if isinstance(annotation, WebLink)
                ]

    def append(self, annotation):
        """Add an annotation.

        Args:
            annotation (gkeepapi.entities.Annotation.Annotation): An Annotation object.

        Returns:
            gkeepapi.entities.Annotation.Annotation: The Annotation.
        """
        self._annotations[annotation.id] = annotation
        self._dirty = True
        return annotation

    def remove(self, annotation):
        """Removes an annotation.

        Args:
            annotation (gkeepapi.entities.Annotation.Annotation): An Annotation object.

        Returns:
            gkeepapi.entities.Annotation.Annotation: The Annotation.
        """
        if annotation.id in self._annotations:
            del self._annotations[annotation.id]
        self._dirty = True

    @property
    def dirty(self):
        return super(NodeAnnotations, self).dirty or any(
            (annotation.dirty for annotation in self._annotations.values()))
