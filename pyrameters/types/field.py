"""
Field represents an individual field in a Definition.
"""
from enum import Enum, unique


@unique
class defaultValues(Enum):
    NO_DEFAULT = 0


class Field(object):
    __slots__ = "name", "_default", "_factory"

    def __init__(
        self, name: str = None, default=defaultValues.NO_DEFAULT, factory=None
    ):
        if default != defaultValues.NO_DEFAULT and factory is not None:
            raise ValueError("Field cannot have both a default value and a factory.")

        if name is not None and not isinstance(name, str):
            raise ValueError("Name must be a string if provided.")

        self.name = name
        self._default = default
        self._factory = factory

    @property
    def default(self):
        if self._default != defaultValues.NO_DEFAULT:
            return self._default, True

        if self._factory is not None:
            return self._factory(), True

        return None, False

    @staticmethod
    def empty(name=None):
        """
        Returns a field with (optionally a name), no default, and no factory.
        """
        return Field(name=name)
