"""Abstract products and factory for data format families."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SerializationContext:
    """Carry state needed while serializing nested nodes."""

    indentation: int = 0
    path: tuple[str, ...] = ()


class ListNode(ABC):
    """Represent a format-specific sequence of values and nodes."""

    def __init__(
        self,
        *values: str | DictNode | ListNode,
    ) -> None:
        """Store values without requiring a Python list as input."""
        self.values = values

    @abstractmethod
    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize the list for its data format."""


class KeyValueNode(ABC):
    """Represent a format-specific named value."""

    def __init__(
        self,
        key: str,
        value: str | DictNode | ListNode,
    ) -> None:
        """Store a key and its text or nested node."""
        self.key = key
        self.value = value

    @abstractmethod
    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize the named value for its data format."""


class DictNode(ABC):
    """Represent a format-specific collection of named values."""

    def __init__(self, *entries: KeyValueNode) -> None:
        """Store entries without requiring a Python dictionary."""
        self.entries = entries

    @abstractmethod
    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize the dictionary for its data format."""


class RootNode(DictNode, ABC):
    """Represent a dictionary used as the document root."""


class DataFormat(ABC):
    """Declare operations for creating a family of format nodes."""

    @abstractmethod
    def create_root(self, *entries: KeyValueNode) -> RootNode:
        """Create the root node."""

    @abstractmethod
    def create_key_value(
        self,
        key: str,
        value: str | DictNode | ListNode,
    ) -> KeyValueNode:
        """Create a named value node."""

    @abstractmethod
    def create_dict(self, *entries: KeyValueNode) -> DictNode:
        """Create a dictionary node."""

    @abstractmethod
    def create_list(
        self,
        *values: str | DictNode | ListNode,
    ) -> ListNode:
        """Create a list node."""
