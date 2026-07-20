"""JSON product family for the Abstract Factory example."""

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


class JSONRootNode(RootNode):
    """Represent the root of a JSON document."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize the complete JSON document."""
        return _serialize_dict(self.entries, _context(context))


class JSONKeyValueNode(KeyValueNode):
    """Represent a named JSON value."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a JSON object member."""
        current = _context(context)
        indentation = " " * current.indentation
        key = json.dumps(self.key, ensure_ascii=False)
        value = _serialize_value(self.value, current)
        return f"{indentation}{key}: {value}"


class JSONDictNode(DictNode):
    """Represent a JSON object."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a nested JSON object."""
        return _serialize_dict(self.entries, _context(context))


class JSONListNode(ListNode):
    """Represent a JSON array."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a JSON array."""
        current = _context(context)
        if not self.values:
            return "[]"

        child_context = _indented(current)
        indentation = " " * child_context.indentation
        values = [
            f"{indentation}{_serialize_value(value, child_context)}"
            for value in self.values
        ]
        closing = " " * current.indentation
        return "[\n" + ",\n".join(values) + f"\n{closing}]"


class JSONDataFormat(DataFormat):
    """Create a compatible family of JSON nodes."""

    def create_root(self, *entries: KeyValueNode) -> RootNode:
        """Create a JSON root node."""
        return JSONRootNode(*entries)

    def create_key_value(
        self,
        key: str,
        value: str | DictNode | ListNode,
    ) -> KeyValueNode:
        """Create a JSON key-value node."""
        return JSONKeyValueNode(key, value)

    def create_dict(self, *entries: KeyValueNode) -> DictNode:
        """Create a JSON dictionary node."""
        return JSONDictNode(*entries)

    def create_list(
        self,
        *values: str | DictNode | ListNode,
    ) -> ListNode:
        """Create a JSON list node."""
        return JSONListNode(*values)


def _context(
    context: SerializationContext | None,
) -> SerializationContext:
    return context if context is not None else SerializationContext()


def _indented(context: SerializationContext) -> SerializationContext:
    return SerializationContext(
        indentation=context.indentation + 2,
        path=context.path,
    )


def _serialize_value(
    value: str | DictNode | ListNode,
    context: SerializationContext,
) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return value.serialize(context)


def _serialize_dict(
    entries: tuple[KeyValueNode, ...],
    context: SerializationContext,
) -> str:
    if not entries:
        return "{}"

    child_context = _indented(context)
    values = [entry.serialize(child_context) for entry in entries]
    closing = " " * context.indentation
    return "{\n" + ",\n".join(values) + f"\n{closing}}}"
