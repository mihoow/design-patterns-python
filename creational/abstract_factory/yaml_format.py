"""YAML product family for the Abstract Factory example."""

from __future__ import annotations

import json

from .abstractions import (
    DataFormat,
    DictNode,
    KeyValueNode,
    ListNode,
    RootNode,
    SerializationContext,
)


class YAMLKeyValueNode(KeyValueNode):
    """Represent a named YAML value."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a YAML mapping entry."""
        current = _context(context)
        indentation = " " * current.indentation
        if isinstance(self.value, str):
            value = json.dumps(self.value, ensure_ascii=False)
            return f"{indentation}{self.key}: {value}"

        value = self.value.serialize(_indented(current))
        return f"{indentation}{self.key}:\n{value}"


class YAMLDictNode(DictNode):
    """Represent a YAML mapping."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a nested YAML mapping."""
        current = _context(context)
        if not self.entries:
            return f"{' ' * current.indentation}{{}}"
        return "\n".join(
            entry.serialize(current) for entry in self.entries
        )


class YAMLRootNode(YAMLDictNode, RootNode):
    """Represent the root of a YAML document."""


class YAMLListNode(ListNode):
    """Represent a YAML sequence."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a YAML sequence."""
        current = _context(context)
        indentation = " " * current.indentation
        lines = []
        for value in self.values:
            if isinstance(value, str):
                text = json.dumps(value, ensure_ascii=False)
                lines.append(f"{indentation}- {text}")
                continue

            nested = value.serialize(_indented(current)).splitlines()
            first = nested[0][current.indentation + 2 :]
            lines.append(f"{indentation}- {first}")
            lines.extend(nested[1:])
        return "\n".join(lines)


class YAMLDataFormat(DataFormat):
    """Create a compatible family of YAML nodes."""

    def create_root(self, *entries: KeyValueNode) -> RootNode:
        """Create a YAML root node."""
        return YAMLRootNode(*entries)

    def create_key_value(
        self,
        key: str,
        value: str | DictNode | ListNode,
    ) -> KeyValueNode:
        """Create a YAML key-value node."""
        return YAMLKeyValueNode(key, value)

    def create_dict(self, *entries: KeyValueNode) -> DictNode:
        """Create a YAML dictionary node."""
        return YAMLDictNode(*entries)

    def create_list(
        self,
        *values: str | DictNode | ListNode,
    ) -> ListNode:
        """Create a YAML list node."""
        return YAMLListNode(*values)


def _context(
    context: SerializationContext | None,
) -> SerializationContext:
    return context if context is not None else SerializationContext()


def _indented(context: SerializationContext) -> SerializationContext:
    return SerializationContext(
        indentation=context.indentation + 2,
        path=context.path,
    )
